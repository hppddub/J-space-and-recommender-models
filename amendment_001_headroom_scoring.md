# Amendment 001 — headroom scoring criterion

**File:** `preregistration/amendments.md` (first entry)
**Date:** 2026-07-27
**Amends:** `THRESHOLD_headroom.md` §1 (primary metric)
**Status:** drafted for sign-off — decision is the user's

---

## 1. What is being changed

`THRESHOLD_headroom.md` named **`exact`** as the primary metric: the model's greedy continuation, truncated to the answer's token length, must equal the answer string. Threshold 70%.

This amendment adds three normalisation rules to that comparison. The strict number is retained and reported alongside; the amendment adds a second number, it does not replace the first.

## 2. **This amendment was written after seeing the result**

Stated plainly because it is the first thing a reviewer will ask.

The strict run produced **57/90 = 63.3%**, missing the pre-registered 70% threshold. The rules below were written after inspecting the 33 strict misses. They were therefore written with knowledge of which items they would flip and which side of the threshold each rule lands on.

Nothing in the design below removes that. The mitigations are: the rules are general rather than item-specific (§3), the weakest available rule was deliberately declined (§4), the rules were adversarially tested against cases they must *not* credit (§5), and both numbers are reported everywhere (§6).

`THRESHOLD_headroom.md` §3 pre-committed option 3 — "re-check the failures first" — as the response to a miss. This amendment is the result of that re-check. It is not an unplanned deviation, but it is post-hoc with respect to the rules themselves.

## 3. The rules

Each is stated so that it could be applied to a dataset never seen. The model's answer phrase is the generated text up to the first sentence-ending punctuation or newline.

| Rule | Statement | Justification |
|---|---|---|
| **R1** | Numerals and number-words are equivalent (`4` ≡ `four`, `2` ≡ `two`), single-token answers only | Orthographic convention, no semantic content. The answer key is internally inconsistent about this — it uses `5` and `8` for some items and `four` and `two` for others |
| **R2** | A leading determiner (`a`, `an`, `the`) is stripped before comparison | `a liquid` and `liquid` denote the same state of matter. English requires the article in some framings and forbids it in others |
| **R3** | A two-word phrase whose **head** (final word) is the answer is credited, unless the modifier is a negator | `honey bee` and `bee` denote the same referent. Capped at two words: a longer phrase is a different answer, not a compound form of this one |

**Monotonicity.** A strict pass is always credited; the rules can only add. This is enforced in code, not by convention. It matters because the rules operate on the answer *phrase* while `strict` operates on the *first token*, so they are not nested — `North` is a strict pass against `" North America"` but the phrase is `north america`. Without explicit monotonicity, the amendment would silently remove seven items it was never intended to touch. This was caught by testing, not by inspection.

## 4. One rule deliberately declined

The strict-miss list contains `bird-country-eagle`: answer `America`, model said `the United States`. This is semantically correct and would be credited by a synonym list.

**No synonym list is being added.** A synonym rule cannot be stated generally — it is a list, and every entry would be written knowing which item it flips. It is the one component of this amendment that could not be defended as anything but post-hoc curve-fitting.

Cost: one item. `bird-country-eagle` is scored as a miss despite being semantically correct, and this is recorded as a known conservative error in the amended number.

## 5. Adversarial testing

The rules were tested against cases they must **not** credit:

| Case | Result |
|---|---|
| answer `red`, model `not red` | not credited (negator guard) |
| answer `liquid`, model `a gas` | not credited |
| answer `sticks`, model `a drum kit` | not credited |
| answer `6`, model `4 from the sun` | not credited |
| answer `Portugal`, model `the United Kingdom` | not credited |
| answer `America`, model `the United States` | not credited (§4) |

The negator guard exists because R3 initially credited `not red` for `red` — two words, head `red`. No negation appears in the 90 items, so the dataset would not have caught it. Ablated output in Control A plausibly will.

## 6. Result

| Criterion | Score | 95% CI | vs 70% |
|---|---|---|---|
| `strict` (pre-registered, paper protocol) | 57/90 = **63.3%** | 53.0–72.6% | miss |
| `amended` (R1+R2+R3) | 66/90 = **73.3%** | 63.4–81.4% | pass |

Nine items flip: two by R1, four by R2, three by R3.

**Both numbers are reported wherever headroom is cited.** The strict number is the paper-protocol comparison and remains the primary figure for any claim about reproducing the original result.

## 7. What this does not fix

The re-check identified three categories of strict miss. This amendment addresses only the first.

- **Surface form (10 items)** — addressed, less the declined synonym case.
- **No answer attempted (6 items)** — the model restates the question rather than answering. Not a scoring problem. See §8.
- **Genuine reasoning or knowledge error (14 items)** — Mars `blue`, Saturn `4th`, most-populous capital `Tokyo`. No scoring change touches these, and they are the floor on what this model can do.

The amended 73.3% therefore still contains ~6 items the model never attempted, and ~14 it got wrong. A model of this size has a real error rate on two-hop factual reasoning, and that is what the number reflects.

## 8. Separate finding, not amended here

Nearly every generation terminates in `\nHypothesis:` or `\nQuestion:`. Qwen3.5-4B is treating `Fact: …` as a document template and continuing the document rather than answering. This is a prompt–model mismatch: the framing was designed for a substantially stronger model.

**Control A runs on these same prompts,** so this carries forward and becomes an alternative explanation for any effect measured there. Recorded here; no change made, because changing the prompt after seeing results would be a second and much larger post-hoc intervention.

## 9. Sign-off

☐ accepted ☐ modified ☐ rejected — accepted  **Date:** July 27, 2026
