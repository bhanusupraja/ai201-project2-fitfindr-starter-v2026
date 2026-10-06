# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> The core tool loop and state handling are now implemented in this repo.
> The remaining work is validation and tuning against the live model quota.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr takes a shopping query in plain English, searches the thrift listings data for a matching item, and then suggests an outfit using the user’s wardrobe before creating a short fit-card caption. The agent keeps the selected item in session state so each step reads the previous result instead of re-asking the user. When a query has no valid matches, it stops early and tells the user how to broaden the search instead of calling the model with nothing.

---

## Tool Inventory

### `search_listings`

- **What it does:** Filters the listing dataset by keyword overlap, optional size, and optional max price, then returns the best matches first.
- **Inputs:** `description` (str), `size` (str | None), `max_price` (float | None)
- **Returns:** A list of matching listing dicts, ordered by score and capped at `config.SEARCH_RESULT_LIMIT`.
- **When it has nothing:** Returns `[]` when no listing matches the description, size, or price ceiling.

### `suggest_outfit`

- **What it does:** Produces one or two outfit suggestions for a thrifted item, either using the user’s wardrobe or generic styling advice when the wardrobe is empty.
- **Inputs:** `new_item` (dict), `wardrobe` (dict)
- **Returns:** A non-empty string with the outfit suggestion text from the model.
- **When it has nothing:** Returns a general styling response instead of raising when `wardrobe['items']` is empty.

### `create_fit_card`

- **What it does:** Writes a short social-caption style summary that mentions the item, its price, platform, and outfit vibe.
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** A 2-4 sentence caption string.
- **When it has nothing:** Returns a fallback descriptive sentence if `outfit` is empty or whitespace-only.

---

## Planning Loop

**Branch rule:** If `search_listings` returns an empty list, put a message in the session and stop. Otherwise take the first result and go to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** I used regex to extract `max_price` with `under $N` patterns and `size` with `size ...` or `in ...` patterns, then cleaned the remaining text into a keyword description.

**What moves through the session:** `query` → `parsed` → `search_results` → `selected_item` → `outfit_suggestion` → `fit_card`, with `error` set early when the empty-search branch triggers.

---

## Sample Run

**One full query**

```
$ python app.py ask 'designer ballgown size XXS under $5'

  [1] search_listings
      in:  dict with keys: description, size, max_price
      out: [] (empty)
  [2] branch: empty results
      in:  dict with keys: search_results_count
      →    stop before suggest_outfit
  No listings matched that search. Try a broader description, a different size, or a higher price ceiling.
```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('vintage graphic tee', max_price=30)[:3])"

[{'id': 'lst_006', 'title': 'Graphic Tee — 2003 Tour Bootleg Style', 'description': 'Vintage-style bootleg tee ...', 'category': 'tops', 'style_tags': ['graphic tee', 'vintage', 'grunge', 'streetwear', 'band tee'], 'size': 'L', 'condition': 'good', 'price': 24.0, 'colors': ['black'], 'brand': None, 'platform': 'depop'}]
```

```
$ python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe())[:200])"

# This calls the model, and the current environment is rate-limited with a 402 RESOURCE_EXHAUSTED response.
```

```
$ python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0])[:200])"

# This also calls the model, and the current environment is rate-limited with a 402 RESOURCE_EXHAUSTED response.
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* I asked for help defining the `search_listings` scoring and size-matching logic so it would return a realistic list of thrift listings rather than every item with a matching letter.
- *What came back:* It suggested a weighted keyword-overlap approach with size-aware filtering and a clear empty-list case.
- *What I changed:* I implemented the score calculation, filtered out no-match results, and kept the empty-list branch as the stopping condition in `agent.py`.

**Moment 2**

- *What I asked for:* I asked for a way to phrase the empty-search branch so it told the user what to change instead of returning a generic `No results` message.
- *What came back:* A sentence pattern focused on broadening the description, changing the size, or increasing the price ceiling.
- *What I changed:* I encoded that text into `session['error']` in the early stop condition and used it in the CLI output.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->



---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
