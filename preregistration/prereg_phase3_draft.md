# Pre-registration — Phase 3 (H1 + H2)

**File:** `preregistration/prereg_phase3.md`
**Status: PARTIAL DRAFT — not yet signable.**
**Gate G2 requires this committed before the first real Phase 3 run.**

`EXECUTION_GUIDE.md` §Phase 3 requires this document to contain: the *k* values in
the sweep, the number of random draws per *k*, the ablation method, the metrics,
the statistical test, and the threshold that counts as H1 support.

Sections **§1–§4 are fixed now**, because Phase 0 determined them and leaving
them open would invite settling them by whatever the harness makes convenient.
Sections **§5–§8 cannot be fixed until Phases 1–2 exist** — each says what
determines it and when.

Started 2026-08-02 following gate G0.

---

## 1. Ablation method — FIXED

Identical to Control A, using the identical harness (`src/ablation/`). Guide §3a
requires Control B to run through the same code path; Phase 0 built it to that
requirement from the first line.

| Parameter | Value | Source |
|---|---|---|
| Operation | Zero the residual stream's projection onto the selected directions | paper; `directions.project_out` |
| Projection mode | `subspace` | `sequential` removes strictly less for non-orthogonal vectors; recorded, not swept |
| Clean-top-k exclusion | 10, **never 0** | paper's confound guard; the only identified route to a **false-positive H1** |
| Effective rank | reported per condition | k J-lens vectors may span fewer than k dimensions |
| Seeds | recorded per random draw | guide §1.2; `AblationSpec` refuses an unseeded random selector |

**Recommender analogue of the confound guard — must be implemented explicitly:**
do not ablate directions corresponding to items already in the top-k of the clean
next-item distribution. Without it, ablation trivially suppresses whatever the
model was about to recommend and H1 is "confirmed" by an artifact.

## 2. The *k* sweep — DIRECTION FIXED, values pending §5

**Sweep k downward from 10, not upward.** Phase 0 finding, session 15: `next_k`
(ranks 11–20) reached 13.7% against the candidate's 6.8%, both far below the
~63% random cloud. Ranks 11–20 carry heavy causal load in the language model.

Two consequences:

1. **k = 10 is not a default.** It is what the original paper used for ablation
   on a different architecture. Proposal §4.7 requires size measured by sweep, and
   the guide forbids fixing a size in advance.
2. **The interesting region is below 10.** If k = 2 or k = 5 produces comparable
   degradation with less collateral disruption, that is both a better instrument
   and a stronger H2 result. If degradation only appears at large k, H2 fails —
   which is a real, reportable finding (proposal §4.3), not a failure to fix by
   searching for a better k.

**Provisional grid, to be finalised in §5:** k ∈ {1, 2, 3, 5, 10, 20, 50}, with
the upper end extending only if the curve has not flattened. **Extending the
sweep after seeing results is an amendment** and goes in `amendments.md`.

**Do not tune k to find a knee.**

## 3. Random matched-size baselines — FIXED

Proposal §4.8 requires matched random draws at **every** k, reported as a
distribution.

**19 draws per null, per k.** Phase 0 established the arithmetic: at 5 draws the
strongest attainable statement under exchangeability is p ≈ 1/6 = 0.167, which
cannot carry the load proposal §4.8 places on this control. 19 gives p ≤ 1/20 =
0.05 if the candidate beats all.

**Two nulls, reported separately, never pooled:**

- `random_lens` — random directions drawn from the lens dictionary. Asks "is it
  *these* lens directions, or any lens directions?"
- `random_iso` — isotropic random unit directions. The paper's own control.

They are different null distributions and are **not exchangeable with each
other**. A pooled p of 1/39 would be invalid. Phase 0 initially computed it that
way and it was corrected before any result was reported.

**`next_k` is run alongside as a complementary baseline** at every k — the
adjacent rank band, same lens, same size. A candidate that matters no more than
the next-k has not earned H1.

## 4. Intact side — FIXED in structure

Phase 0's single largest methodological lesson: **a sensitive and a coarse
intact-side measure can disagree, and either alone misleads.** At heavy ablation
WikiText top-1 match fell to 0.577 while MMLU was statistically unchanged
(z = −0.25). Reporting only one would have produced a materially wrong picture.

Phase 3 therefore measures **both**:

| Type | Purpose | Recommender instantiation |
|---|---|---|
| Sensitive | Registers any distributional shift | **§6 — pending** |
| Coarse | Constrained choice; only flips if a few candidates reorder | **§6 — pending** |

**Mandatory diagnostic** (`intact.diagnose`): an intact-side score near ceiling
*with no degrading-side effect* is **not** a preserved intact side — it is an
ablation that did nothing. Report the answer-flip rate against the random rate to
establish the intervention fired.

## 5. Sweep values, band, and layers — PENDING PHASE 2

Determined by: the recommender's depth, the derived band, and the timing probe.

- [ ] Final k grid, once d_model and the readout's rank profile are known
- [ ] Band, derived in Phase 2 — **not inherited.** L20–31 is Qwen3-8B's; the
      paper's is Sonnet 4.5's
- [ ] Whether the sweep axis is k, layer band, or both. Sweeping both multiplies
      runs. **Phase 0 flagged this repeatedly and it must not be settled by
      whatever the harness makes easy**
- [ ] Cost, from a timing probe on the actual model before committing

## 6. Metrics and task sets — PENDING PHASES 1–2

- [ ] Degrading-side metric (e.g. HR@k, NDCG@k, next-item accuracy) — Phase 1
- [ ] Sensitive intact measure — the recommender analogue of corpus top-1 match
- [ ] Coarse intact measure — the analogue of constrained multiple choice
- [ ] Confirmation that the Phase 1 easy/hard task sets are **unchanged since
      they were frozen**, with the timestamp predating this document (guide §7)

## 7. Statistical test and H1 threshold — PENDING §5, §6

- [ ] The threshold that counts as H1 support, in **relative** terms. Phase 0
      showed why: absolute point thresholds do not transfer between models with
      different clean baselines
- [ ] Whether "beats every random draw" is the H1 criterion, as in Control A, or
      a distributional test
- [ ] The H2 criterion — what counts as a knee, decided **before** the curve is
      seen

## 8. Control B — PENDING PHASE 1

Guide §3a: ablate a component with independent reason to matter — a core
embedding or attention layer — through the **exact same harness**, before testing
the candidate. **Run first. Do not defer.**

- [ ] Which component, and the independent reason it should matter
- [ ] What counts as the harness detecting it

**Carry forward from Phase 0:** Control A's clean condition returned an intact-side
top-1 match of exactly 1.000 and random ablations barely moved anything. That
pattern — clean is exactly unchanged, random is nearly unchanged, candidate moves
a lot — is what a working harness looks like. Control B should reproduce it.

---

## Sign-off — NOT YET

Cannot be signed until §5–§8 are filled. **G2 blocks Phase 3 until it is
committed**, and the tasks must have been frozen before any Phase 3 result was
seen.

**Signed:** _______________ **Date:** ___________
