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
| 1. A matching query completes all three tools | 4 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The chosen item is carried through session state | 5 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |
| 4. The fit card includes the required information | 5 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |
| 5. The price ceiling is respected during search | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```
python run_eval.py --label before

matching query completes (example wardrobe)
  query: vintage graphic tee under $30
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
[2] branch: model unavailable
      in:  dict with keys: tool
      →    Still rate limited after 5 attempts. Wait a minute and try again — your key is fine.
Last error: 402 RESOURCE_EXHAUSTED. {'error': {'code': 402, 'message': 'Your prepayment credits are depleted. Please go to AI Studio at https://ai.studio/projects to manage your project and billing. Learn more at https://ai.google.dev/gemini-api/docs/billing#prepay. ', 'status': 'RESOURCE_EXHAUSTED'}}
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
| 1 | A matching query completes all three tools | 4 of 5 | MISSED | The search step succeeded, but every run stopped at the model layer with a 402 prepayment exhaustion error before the outfit suggestion or fit card was produced. |
| 2 | An impossible query stops before the second tool | 5 of 5 | MET | The empty-search branch fired consistently and returned the user-facing message telling them to broaden the description, size, or price ceiling. |
| 3 | The chosen item is carried through session state | 5 of 5 | MISSED | No run reached the second model step, so the selected item was never compared against the next tool call in a completed end-to-end path. |
| 4 | The fit card includes the required information | 5 of 5 | MISSED | The model never returned the final caption because the session was cut off by the external 402 billing error before the fit card was generated. |
| 5 | The price ceiling is respected during search | 5 of 5 | MET | The search tool filtered by max price and every result observed was under the requested ceiling across all five tries. |

**Diagnoses**

The dominant pattern was not a logic bug in the loop or the search tool; it was an external service failure. The search tool executed correctly, the empty-search branch behaved correctly, and the price filter was respected. The runs failed at the model/call layer because the API returned `402 RESOURCE_EXHAUSTED` with "Your prepayment credits are depleted." That means the remaining problems are not in FitFindr's branching logic but in the live model access available during testing.

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
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Y2K Baby Tee — Butterfly Print, Vintage Band Tee — Faded Grey, Graphic Tee — 2003 Tour Bootleg Style … +7 more
[2] branch: model unavailable
      in:  dict with keys: tool
      →    Still rate limited after 5 attempts. Wait a minute and try again — your key is fine.
```

**Empty search**

```
[1] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: [] (empty)
[2] branch: empty results
      in:  dict with keys: search_results_count
      →    stop before suggest_outfit
```

**On the MCP move:** The direct `search_listings` call was replaced with `call_tool("search_listings", {...})` in `agent.py`. The MCP server was verified to advertise the tool via `python mcp_client.py`, and the server listed `search_listings` as available. The observable difference afterward was not the data itself; it was that the run reached the external model layer and then stopped on a `402 RESOURCE_EXHAUSTED` billing error. That is the point where the model provider blocked the request, not where the FitFindr loop failed.

---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

I changed the agent's first tool call to the MCP client and added a clearer model-unavailable branch in `agent.py` so the app reports the provider failure as a user-facing message instead of crashing unhelpfully.

**Which failure it was meant to fix:**

The model-unavailable path and the MCP wiring seam. The goal was to preserve the same result shape from the tool while making the error path explicit and readable.

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1. A matching query completes all three tools | 4 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |
| 2. An impossible query stops before the second tool | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |
| 3. The chosen item is carried through session state | 5 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |
| 4. The fit card includes the required information | 5 of 5 | FAIL | FAIL | FAIL | FAIL | FAIL | MISSED (0/5) |
| 5. The price ceiling is respected during search | 5 of 5 | PASS | PASS | PASS | PASS | PASS | MET (5/5) |

**Did it help, and how do I know:**

It helped the MCP wiring and the message quality, but it did not change the external blocker. The same `402 RESOURCE_EXHAUSTED` error still occurred on every model call, so the improvement is partial: the app handles the failure as intended, but the API remains unavailable until billing is restored.

---

## What's Still Broken

- Criterion 1, 3, and 4 are still blocked by the live model service being out of credits. The agent reaches the search step and the empty-search branch correctly, but cannot get a response from Gemini to continue to `suggest_outfit` or `create_fit_card`.
- The remaining fix is not in the FitFindr code path; it is re-enabling or restoring billing access to the model provider so model calls succeed again.
- I stopped there because the source of failure is external to the repository and the code is already handling the failure path as a readable message instead of a stack trace.



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
