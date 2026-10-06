# Acceptance criteria — FitFindr

Five criteria that say what "working" means for this agent, written in unit 3
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"The agent handles errors"* is an opinion.
*"When search returns nothing, the agent stops before calling the second tool,
in 5 of 5 tries"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter one. A reason that says something about your tools, your loop, or the
data earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

**Two are written for you. You write three.**

---

## 1. A matching query completes all three tools

Given a query that matches at least one listing, the agent completes all three
tool calls and returns a fit card — in at least 4 of 5 tries.

**Why this target:**
<!-- Why 4 of 5 and not 5 of 5? Something about your search, probably —
     "my search is a plain keyword match and some phrasings will miss" is a
     real answer. -->

---

## 2. An impossible query stops before the second tool

Given a query that matches no listings, the agent stops before calling
`suggest_outfit` and returns a message naming what to change — 5 of 5 tries.

**Why this target:**
<!-- Why is 5 of 5 reasonable here when criterion 1 isn't? What's different
     about this path? -->

---

## 3. The chosen item is carried through session state

For a query that matches at least one listing, the item in `session["selected_item"]` is the same title and price that the agent used for the next tool call in 5 of 5 tries.

**Why this target:**
This checks the actual state handoff rather than whether the search tool returned something reasonable. A broken session passed between tools can look like a model-quality problem, but the real cause is that the loop overwrote or changed the selected item before `suggest_outfit` ran.

---

## 4. The fit card includes the required information

For 5 different matching items, each fit card is 2 to 4 sentences long and includes the item title, the price, and the marketplace/platform name in the same caption, in 5 of 5 tries.

**Why this target:**
The model is allowed to vary wording, but a fit card that omits price or platform is not usable as a product post. This makes the requirement specific enough to score without demanding identical wording across runs.

---

## 5. The price ceiling is respected during search

For 5 queries with a declared `under $X` limit, every returned listing costs at most the requested maximum, in 5 of 5 tries.

**Why this target:**
This is a concrete, observable behavior that matters to shoppers and is easy to validate from the session or the tool result. It is stricter than the loose “search is reasonable” standard and directly checks the tool’s filtering logic.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 4 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 4. Something about the fit card

         The fit card is different every time.

         **Why this target:** ...

         > **Revised in unit 4:** For 5 different items, the 5 fit cards share
         > no opening sentence.
         >
         > **Why revised:** "different" wasn't checkable — two cards that
         > differed by one word still counted. The new version is something I
         > can actually score.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said the empty search stops it 5 of 5 times, but I got 3 of 5,
            so 3 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
