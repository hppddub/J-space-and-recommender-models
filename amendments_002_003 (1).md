# Amendments 002 and 003 — append to `preregistration/amendments.md`

Amendment 001 (headroom scoring rules R1/R2/R3) is already recorded. Both
amendments below are made **before any ablation has run on a real model**, so
neither is post-hoc with respect to Control A's results. Both are nonetheless
departures from a signed pre-registration and are logged as such.

---

## Amendment 002 — Control A primary eval

**Date:** 2026-07-29
**Amends:** `prereg_controlA.md` §4 (clean baseline) and §5 (degrading eval)
**Status:** ☐ accepted ☐ modified ☐ rejected — accepted

### What is being changed

The pre-registration specifies *"90 probe-swap prompts, strict scoring"* with a
clean baseline of **58/90 = 64.4%**.

`strict` was defined in `headroom_full.py` as: generate `len(answer_tokens)`
tokens greedily, decode, and compare to the answer string. **The ablation harness
performs a single forward pass** and returns logits — it cannot score a
multi-token answer at all. 17 of the 90 answers tokenise to 2 or 3 tokens.

The primary eval becomes **`strict` on the 73 single-token-answer items**, clean
baseline **50/73 = 68.5%**. First-token match on all 90 (clean 63/90 = 70.0%) is
reported as a secondary, since it costs nothing.

### Why this resolution rather than the alternatives

| Option | Clean baseline | Assessment |
|---|---|---|
| strict, all 90 | 64.4% | Not computable from one forward pass |
| first-token, all 90 | 70.0% | Computable, but lenient on the 17 multi-token items — credits a correct first token followed by a wrong completion |
| **strict, 73 single-token items** | **68.5%** | Exactly `strict` on that subset; one forward pass; unambiguous |

The chosen option also matches the paper's own practice: `capacity.json`
explicitly filters its word pools to entries that tokenise to a single token
under the target model, and §A.9 states the J-lens "only identifies vectors
associated with concepts that correspond to single tokens".

### Consequences

- n drops from 90 to 73. Binomial SE at p≈0.5 rises from ~5.3pp to ~5.9pp. The
  §4 dose-response threshold of 10pp remains roughly 2 SE and is **not** changed.
- The §4 "substantial degradation" criterion (≥50% relative reduction) is
  unchanged in form; the absolute target moves from ≤32.2% to **≤34.3%**.
- Both numbers are reported wherever Control A's degrading side is cited.

### What this does not change

The threshold, the criteria, the band, the nesting, the number of random draws.
This is a change of measurement instrument, not of the bar.

---

## Amendment 003 — additional band-start sensitivity condition

**Date:** 2026-07-29
**Amends:** `prereg_controlA.md` §3 (band sensitivity)
**Status:** ☐ accepted ☐ modified ☐ rejected — accepted

### What is being changed

One condition is **added**: `heavy-paper` at **L13–31** (19 layers). Nothing is
removed and the primary band is unchanged.

### Evidence prompting it

Stage B2 (`results/raw/readout_qwen3-8b/`, logged session 14) measured where the
unspoken intermediate is actually represented:

- Gap over matched foils reaches **+20.0% at L10** and **+33.3% at L12** — ten
  layers below the pre-registered band start of L20.
- Median rank of the intermediate at L18 is already 19, and 20 at L20.
- Peak at L30: median rank **1**, 90.0% top-10 against 8.9% for foils.
- Loading collapses immediately after L31, independently confirming the band end.

Separately, the paper's band was 38%–92% of depth. Scaled to 36 layers that is
**L13–L32**. So two independent lines — the paper's own proportions, and
task-specific readout on this model — place the lower boundary near L13, while the
four aggregate Stage B statistics placed it at L20.

**That disagreement is recorded as a finding, not resolved by fiat.** The Stage B
statistics measure general processing structure; the Stage B2 readout measures
task-specific content. There is no reason those must share a lower boundary.

### Why add a condition rather than move the band

Moving the primary band after seeing Stage B2 would be changing the target on the
strength of new data — even though that data is readout rather than ablation, and
even though the change would be defensible. The pre-registered band was derived
from independent evidence and stays primary.

Adding a condition tests the same question without moving anything, and turns
band-start sensitivity into its own dose-response:

| Condition | Layers | Width | Start depth |
|---|---|---|---|
| heavy-late | L24–31 | 8 | 69% |
| **heavy (primary)** | **L20–31** | **12** | **57%** |
| heavy-early | L15–31 | 17 | 43% |
| heavy-paper | L13–31 | 19 | 37% |

### Pre-registered prediction

**If under-ablation is real — if the primary band leaves recoverable content
below L20 — the effect should grow monotonically as the start moves down:**

    heavy-late  <  heavy  <  heavy-early  <  heavy-paper

**If the curve is flat across all four, the band start is not load-bearing**, and
that is the stronger result: it can be stated with four starts spanning 69%→37%
of depth rather than defended at one.

Recorded before the run so that either outcome is a prediction tested rather than
a pattern narrated afterwards.

### Note on an existing width control

`medium` (L20–27) and `heavy-late` (L24–31) are both 8 layers with different
starts. That pair isolates start position from width, which no other pair in the
design does. Unchanged by this amendment, restated here because it is easy to
lose.

### Cost

40 additional conditions (1 candidate + 1 next_k + 19 random_lens + 19
random_iso), taking the grid from 201 to **241**. Approximately 11 extra minutes
and 3 extra units on an A100. The random-draw count and every §4 criterion are
unchanged.

---

## Sign-off

**Amendment 002:** ☐ accepted ☐ modified ☐ rejected --accepted
**Amendment 003:** ☐ accepted ☐ modified ☐ rejected --accepted

**Signed:** Stanley Zhou  **Date:** July 29, 2026

*Both committed before the first ablation on a real model.*
