"""
The FitFindr planning loop.

This is the file that makes FitFindr an agent rather than a script. It decides
which tool to run next based on what the last one returned.

If your loop calls all three tools no matter what comes back, you have a list
of function calls. A loop looks at the last result before it picks the next
step. **That branch is the graded part of this unit.**

Build and test your three tools in `tools.py` first. Then come here.

    python agent.py          runs both example paths below
"""

import re

import config
import trace
from tools import search_listings, suggest_outfit, create_fit_card
from generate import ModelUnavailable


# ── session state ─────────────────────────────────────────────────────────────

def new_session(query: str, wardrobe: dict) -> dict:
    """
    A fresh session for one user interaction.

    The session is the single source of truth for a run. Every tool result goes
    in here, and the next tool reads it back out.

    You could pass values straight from one call to the next. It would work,
    and you would not be able to test it — you can't print a variable you have
    already overwritten. Going through the session is what makes the state
    visible, and unit 4 has you write a criterion about exactly that.

    Add fields if you need them.
    """
    return {
        "query": query,              # what the user typed
        "parsed": {},                # description / size / max_price you pulled out of it
        "search_results": [],        # everything search_listings returned
        "selected_item": None,       # the one you chose — goes into suggest_outfit
        "wardrobe": wardrobe,        # the user's wardrobe
        "outfit_suggestion": None,   # what suggest_outfit returned
        "fit_card": None,            # what create_fit_card returned
        "error": None,               # set when the run ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the loop once and return the finished session.

    Args:
        query:    what the user asked for, in plain language
                  (e.g. "vintage graphic tee under $30, size M").
        wardrobe: a wardrobe dict — get_example_wardrobe() or
                  get_empty_wardrobe() from utils/data_loader.py.

    Returns:
        The session dict. **Check session["error"] first** — if it isn't None,
        the run ended early and the later fields will still be None.
    """
    session = new_session(query, wardrobe)

    for count in range(1, config.MAX_ITERATIONS + 2):
        trace.check_iterations(count)

        text = (query or "").strip()
        parsed = {"description": text, "size": None, "max_price": None}

        max_match = re.search(r"under\s*\$?\s*(\d+(?:\.\d+)?)", text, re.I)
        if max_match:
            parsed["max_price"] = float(max_match.group(1))
            text = text[: max_match.start()] + " " + text[max_match.end() :]

        size_match = re.search(r"(?:size|in)\s+([A-Za-z0-9/]+)", text, re.I)
        if size_match:
            parsed["size"] = size_match.group(1).strip()
            text = text[: size_match.start()] + " " + text[size_match.end() :]

        cleaned = " ".join(re.findall(r"[A-Za-z0-9]+(?:['-][A-Za-z0-9]+)?", text))
        parsed["description"] = cleaned.strip() or query.strip()
        session["parsed"] = parsed

        results = search_listings(
            description=parsed["description"],
            size=parsed["size"],
            max_price=parsed["max_price"],
        )
        session["search_results"] = results
        trace.step(
            "search_listings",
            inputs={
                "description": parsed["description"],
                "size": parsed["size"],
                "max_price": parsed["max_price"],
            },
            returned=results,
        )

        if not results:
            session["error"] = (
                "No listings matched that search. Try a broader description, a different size, "
                "or a higher price ceiling."
            )
            trace.step(
                "branch: empty results",
                inputs={"search_results_count": len(results)},
                returned=None,
                note="stop before suggest_outfit",
            )
            return session

        session["selected_item"] = results[0]
        try:
            outfit = suggest_outfit(session["selected_item"], wardrobe)
            session["outfit_suggestion"] = outfit
            trace.step(
                "suggest_outfit",
                inputs={"selected_item": session["selected_item"].get("title")},
                returned=outfit,
            )

            fit_card = create_fit_card(outfit, session["selected_item"])
            session["fit_card"] = fit_card
            trace.step(
                "create_fit_card",
                inputs={"item_title": session["selected_item"].get("title")},
                returned=fit_card,
            )
        except ModelUnavailable as exc:
            session["error"] = str(exc)
            return session

        return session

    session["error"] = "The loop did not finish in the allowed number of iterations."
    return session


# ── running it directly ───────────────────────────────────────────────────────

def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(f"  found:    {item.get('title')} — ${item.get('price')} on {item.get('platform')}")
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    ))

    print("\n=== A query it can't ===")
    _show(run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    ))

    print(
        "\nThe second one should stop before the fit card. If both paths look "
        "the same,\nthe branch isn't doing anything yet."
    )
