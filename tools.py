"""
The three FitFindr tools.

Each one is a standalone function you can call and test on its own, before any
of them are wired into the loop. Build and test them one at a time — three
untested tools joined by a loop is one problem that looks like six, because you
can't tell which layer is lying to you.

    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)             → str
    create_fit_card(outfit, new_item)              → str

All three are stubs right now. They run and they do nothing — that's the
starting position and it's deliberate.

⚠️ Before you write any of them, fill in the **Tool Inventory** section of your
README (Milestone 2). Four lines per tool: what it does, each input with its
type, exactly what it returns, and what it returns when it has nothing to give.
That last line is what your loop branches on. "Returns a list" earns nothing —
the description has to say what is *in* the list.
"""

import config  # noqa: F401 — you'll use this in search_listings
import re

from generate import generate
from utils.data_loader import load_listings


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _size_matches(listing_size: str | None, filter_size: str | None) -> bool:
    if filter_size is None:
        return True
    if listing_size is None:
        return False

    listing = str(listing_size).lower()
    target = str(filter_size).lower()
    target_tokens = {
        token
        for token in re.findall(r"[a-z0-9]+", target)
        if token not in {"size", "in"}
    }
    if not target_tokens:
        return True
    if any(token in listing for token in target_tokens):
        return True
    # Allow a size like "M" to match "S/M" and similar combined labels.
    shortened = listing.replace("/", " ")
    return any(token in shortened for token in target_tokens)


# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the listings data for items matching a description, and optionally a
    size and a price ceiling.

    This is the tool that doesn't call the model, which makes it the easiest one
    to test and the one to move onto MCP in unit 4.

    Args:
        description: keywords describing what the user wants
                     (e.g. "vintage graphic tee").
        size:        a size string to filter by, or None to skip size filtering.
                     Match case-insensitively — "M" should match "S/M".

                     ⚠️ Read the sizes in the data before you reach for a plain
                     substring test. `"s" in "us 9"` is True, and so is
                     `"l" in "xl"`. A filter that returns shoes when someone
                     asked for a small top reads like a broken search, and it
                     will quietly cost you in unit 4 when you test criterion 1.
                     What counts as a size match is part of your spec — decide
                     it and write it into your Tool Inventory.
        max_price:   maximum price, inclusive, or None to skip price filtering.

    Returns:
        A list of matching listing dicts, best match first.
        **Returns an empty list when nothing matches — an empty list, not None,
        and not an exception.** Your loop branches on this.

    Each listing dict has these fields:
        id, title, description, category, style_tags (list), size,
        condition, price (float), colors (list), brand (str or None), platform

    Note that `brand` is None for most listings. That is deliberate and
    realistic — thrift listings often have no brand. If something you write
    assumes a brand is always there, you will find out in unit 4.
    """
    description_text = (description or "").strip()
    if not description_text:
        return []

    keywords = [
        token
        for token in _tokenize(description_text)
        if token not in {"under", "price", "size", "in", "for", "the", "a", "an"}
    ]
    if not keywords:
        return []

    matches = []
    for listing in load_listings():
        price = listing.get("price")
        if max_price is not None and price is not None and float(price) > float(max_price):
            continue
        if not _size_matches(listing.get("size"), size):
            continue

        haystack = " ".join(
            [
                listing.get("title", ""),
                listing.get("description", ""),
                listing.get("category", ""),
                " ".join(listing.get("style_tags", []) or []),
                " ".join(listing.get("colors", []) or []),
                str(listing.get("brand") or ""),
            ]
        ).lower()
        score = 0
        for keyword in keywords:
            if keyword in haystack:
                score += 2
        if score == 0:
            continue
        matches.append((score, listing))

    matches.sort(key=lambda item: (-item[0], float(item[1].get("price", 9999))))
    return [listing for _, listing in matches[: config.SEARCH_RESULT_LIMIT]]


# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest one or two outfits.

    This one calls the model, through `generate()`. You don't need to think
    about rate limits — the adapter handles pacing for you.

    Args:
        new_item: a listing dict — the item the user is considering.
        wardrobe: a wardrobe dict with an 'items' key holding a list of items.
                  **It may be empty.** Handle that.

    Returns:
        A non-empty string with outfit suggestions.
        With an empty wardrobe, return general styling advice rather than
        raising or returning "". Unit 4 has you trigger the empty wardrobe on
        purpose, so decide now what it should do.
    """
    item_title = new_item.get("title") or new_item.get("name") or "this thrifted item"
    item_price = new_item.get("price")
    item_category = new_item.get("category") or "piece"

    if not wardrobe or not wardrobe.get("items"):
        prompt = (
            f"Give me 2 outfit ideas for {item_title}, a {item_category}. "
            f"The user has no saved wardrobe yet. Keep the advice general, wearable, "
            f"and specific about vibe. Mention the item and suggest complementary basics."
            f"{' Price: $' + str(item_price) if item_price is not None else ''}"
        )
        return generate(
            prompt,
            system="You are a concise fashion stylist who gives practical outfit suggestions.",
        )

    wardrobe_text = "\n".join(
        f"- {item.get('category', 'unknown')}: {item.get('name', 'item')}"
        for item in wardrobe.get("items", [])
    )
    prompt = (
        f"Suggest 1 or 2 outfits that work with this new thrifted item: "
        f"{item_title} ({item_category}, {'$' + str(item_price) if item_price is not None else 'price not listed'}). "
        f"Use only the pieces the user already owns from this wardrobe:\n{wardrobe_text}\n"
        f"Keep the suggestions specific and casual, naming the existing wardrobe pieces."
    )
    return generate(
        prompt,
        system="You are a helpful personal stylist. Return practical outfit combinations using items already in the wardrobe.",
    )


# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Write a short caption someone would actually post about the find.

    This calls the model too.

    Args:
        outfit:   the outfit suggestion string from suggest_outfit().
        new_item: the listing dict for the item.

    Returns:
        A two-to-four sentence caption.
        If `outfit` is empty or whitespace, return a descriptive message rather
        than raising.

    The caption should read like a real post rather than a product description,
    mention the item and its price and platform once each, and be specific about
    the vibe.
    """
    if not outfit or not outfit.strip():
        title = new_item.get("title") or "this thrifted find"
        price = new_item.get("price")
        platform = new_item.get("platform") or "the marketplace"
        return (
            f"Found {title} for ${price} on {platform} — the kind of piece that instantly \
            gives the outfit a lived-in, vintage edge."
        )

    item_title = new_item.get("title") or "this thrifted find"
    item_price = new_item.get("price")
    platform = new_item.get("platform") or "the marketplace"
    prompt = (
        f"Write a 2-4 sentence Instagram-style caption for this thrifted item: "
        f"{item_title}. Price: ${item_price}. Platform: {platform}. "
        f"Outfit idea: {outfit}. "
        f"Make it sound like a real post, mention the item and price and platform once each, "
        f"and keep the vibe specific and fun."
    )
    return generate(
        prompt,
        system="You are a witty fashion caption writer. Write polished, human-sounding captions for thrift finds.",
    )
