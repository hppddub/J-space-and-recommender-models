# G0 — decision gate entry

Append to `logs/lab_log.md` after Session 16.

---

## [2026-08-02] GATE G0 — Did Control A pass well enough to trust the instrument?

**Gate source:** `EXECUTION_GUIDE.md` §5, gate table row G0.
**Scoring rule:** `prereg_controlA.md` §4 / `DECISION_control_A.md` §5 — **per
finding, not a single verdict**, because each criterion bounds a different
downstream claim.

### What the gate asks

Not "did Control A pass" and not "is the workspace hypothesis true." The guide's
question is whether the instrument can be trusted — i.e. whether a null in the
recommender domain will be **diagnosable**, distinguishing "the phenomenon isn't
there" from "the method can't see it" (proposal §4.4).

### Evidence

`results/raw/controlA_qwen3-8b/` (sessions 15, 16). Qwen3-8B bfloat16, published
lens n=479, k=10, band L20–31, 241 conditions, 19 random draws per null.

**Clean baseline: 50/73 = 68.5%** (strict, single-token subset, Amendment 002).

| # | Criterion | Threshold | Observed | |
|---|---|---|---|---|
| 1 | Substantial degradation | ≥50% relative | **90%** (68.5% → 6.8%) | PASS |
| 2 | Dose-response | heavy − light ≥10pp | **45.2pp** (61.7 vs 16.4) | PASS |
| 3 | Beats every random draw | at every strength | **38/38, all six strengths**, p ≤ 0.05 per null | PASS |
| 4 | Intact side | WikiText top-1 ≥0.90 | **0.577** | **FAIL** |

Supplementary (session 16, `DECISION_control_A.md` §4.5 tasks, run after
criterion 4 failed): MMLU 67.3% → 68.7% (z = −0.25, **intact**); SST-2 92.7% →
80.7% (z = +3.11, reduced but retaining 72% of above-chance performance). Answer
flip rates 4.3× and 3.6× the matched random rate, confirming the ablation fired
rather than doing nothing.

### Decision

**PARTIAL — proceed to Phase 1 with the bound below stated in the paper.**

☑ partial ☐ pass ☐ fail — **Signed:** _______________ **Date:** ___________

### Rationale

**Fail is not supported.** Fail required no differential between reasoning and
intact-side tasks, or the random control matching the candidate. Neither is
close: zero overlap between the candidate and 38 random draws at every one of six
band settings, and MMLU statistically unchanged.

**Pass is not available.** Criterion 4 failed on its pre-registered terms.
Calling it a pass would require either moving the threshold or substituting MMLU
for the pre-registered measure — both after seeing results.

**What each passing criterion licenses**, since they are not interchangeable:

- *Criterion 1* — the harness can produce a large effect where one exists. A null
  in Phase 3 cannot be attributed to a harness incapable of registering anything.
- *Criterion 2* — the effect scales with intervention magnitude. This is the
  strongest evidence against an artifact: a broken format or a degenerate code
  path would tend to be all-or-nothing, not a smooth 24% → 62% → 90% curve.
- *Criterion 3* — the *specific directions* matter, not the dimension count. This
  is the discriminating control and the direct analogue of what H1 requires.

**What the failure bounds, stated tightly:**

- **Cannot claim** that ablation leaves the model's next-token distribution on
  ordinary text intact. It does not — cross-entropy 3.12 → 6.98 nats, 42% of
  argmax positions flip. The paper's "leaves fluent generation intact" claim
  **does not replicate**.
- **Can claim** that ablating the top-10 J-lens directions across L20–31 collapses
  two-hop reasoning by 90% relative, beyond every one of 38 matched random draws
  at six band settings, while leaving MMLU statistically unchanged.

The failure therefore bounds a claim about *distributional preservation*, not
about selectivity as such.

**On the supplementary evidence.** It explains what the failure bounds; it does
not convert the failure into a pass. The write-up must present criterion 4 as
failed, with MMLU as the reason the bound is narrow — not the reverse ordering.
The coarse tasks were named in `DECISION_control_A.md` §4.5 before any result
existed and only the WikiText half was built, so running them completes an
under-delivery rather than shopping for a passing measure. **The ordering is
visible and the paper should raise it before a reviewer does.**

### Consequences for the paper

Three statements are now required in the write-up:

1. Control A is a partial replication. Three of four pre-registered criteria pass
   decisively; the fourth fails, and what it bounds is stated above.
2. Control A implements a protocol specified in the paper using released prompt
   data — **not** a replication using released code, which contains no
   intervention machinery (session 03).
3. The near-ceiling precondition the original ablation depends on is not
   reachable with affordable open models. Three models spanning 4B–8B and two
   architectures scored 63.3% / 55.6% / 64.4%; doubling parameters bought 1.1pp.

### Consequences for Phase 3

- **next-k is nearly as damaging as top-k** (13.7% vs 6.8% at heavy, both far
  below the ~63% random cloud). Ranks 11–20 carry heavy causal load. Sweep *k*
  **downward** from 10; do not treat 10 as a default. Recorded in
  `prereg_phase3.md`.
- **Measure both a sensitive and a coarse intact-side metric.** They disagreed
  here and either alone would have misled.
- **Effect magnitudes are on record**, which is what guide Phase 0 step 4 asked
  for: Phase 3 now knows what a real positive effect looks like through this
  instrument.

### Open items carried forward, not resolved by this gate

1. **Ignition experiment not implemented** — the paper's readout-independent band
   check. All four band statistics are lens-derived, so a layer effect could be
   an artifact of the method. Adequate for Phase 0; **required for Phase 2.**
2. **SST-2 non-monotonicity unexplained** — `medium` hurts it more than `heavy`
   (z = +6.17 vs +3.11). Outside noise. Reported unresolved.
3. **Lens recipe deviation** — every published Neuronpedia lens used
   `target_layer: null` (final layer); §A.7 says the paper used penultimate.
   Measured difference 2.4% of max magnitude. Documented, not corrected.

### Next

Phase 1 — model and task setup. Gate **G1**: is there a real easy/hard difficulty
gradient in base-model performance? Phase 4 is uninterpretable without one.

**Deadline check:** ~27 days to 29 August AoE. Pre-committed hard checkpoint
2026-08-18 (16 days) tied to Phase 2 progress. Decision this session: **do not
compress Phase 1 yet**; reassess at the 18 August checkpoint.
