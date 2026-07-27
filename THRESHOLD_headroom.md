# Headroom threshold — committed BEFORE the run

**Fill this in, commit it, and only then run the notebook.**

The point is simple: if you pick the threshold after seeing the number, you will pick one the number passes. Everybody does. That's why it goes in writing first, with a timestamp in the git history.

**Date committed:** July 27, 2026
**Model under test:** Qwen3.5-4B
**Eval:** 90 two-hop prompts, `data/experiments/probe-swap.json`, unablated, greedy decoding
**Governed by:** `DECISION_control_A.md` §4.6

---

## 1. Primary metric

Pick one. The script reports both, but only one counts for the decision.

- [ ] **`exact`** — the model's full generated continuation matches the answer. Strict, unambiguous. **Recommended.**
- [ ] `first_token` — only the answer's first token matches. Lenient: credits "Cal" for "California".

**Chosen:** exact

**Why it matters:** `first_token` will read several points higher than `exact` for no better reason than that some answers are multi-token. Choosing it after seeing both numbers would be picking the flattering one.

---

## 2. The threshold

**Sufficient headroom means the primary metric is at or above:** 70 %

### What constrains the choice

The paper's ablation result has the shape *near ceiling → near zero*. Control A tries to reproduce that shape. So the question is how much room there is to fall.

At n=90 the confidence intervals are wide, so a threshold with decimal places is false precision:

| If you measure | 95% CI | Interval width |
|---|---|---|
| 80% | 71–87% | 16 pts |
| 70% | 60–79% | 19 pts |
| 50% | 40–60% | 20 pts |
| 30% | 22–40% | 19 pts |

Rough guidance, not a rule:

- **70% and up** — you can honestly claim to have reproduced "near ceiling." Control A is a real replication.
- **~50–70%** — a drop would still be measurable, but you can't claim the paper's shape. Control A is **partial by construction**, and the write-up must say so and bound every downstream claim accordingly.
- **Below ~40%** — the intact-side comparison stops meaning anything, because you can no longer distinguish "ablation destroyed the reasoning" from "the model was guessing." Control A cannot do its job.

---

## 3. If the threshold is not met

**Decision made in advance:** 3

Options, in the order `DECISION_phase0_model.md` §4 recommends:

1. **Step up in model size.** Fit your own lens with `target_layer=-2` — §A.7 shows ten prompts already beat the baselines, so fitting is nearly free. Compute cost moves to the ablation evals.
2. **Accept a documented partial Control A**, and let it bound every claim downstream.
3. **Re-check the failures first.** If they're scoring artifacts rather than reasoning failures (see Cell 8), the real headroom is higher and the threshold may not actually have been missed.

**What is not an option:** downscaling the validation to fit the model. Guide Phase 0 says "downscale the LLM before downscaling the validation," but AI guide §1.4 adds the floor — below some size Control A stops being informative at all. A pass obtained from a model that cannot reason is worse than an honest partial.

---

## 4. Sign-off

**Threshold set by:** Stanley Zhou **Date:** Juily 27, 2026

*Committed before the run. Any change after this point is an amendment and goes in `preregistration/amendments.md` with a justification — changing it isn't forbidden, hiding the change is.*
