# Decision record — Control A specification

**Phase 0, step 0.3.** Drafted for sign-off; the decision is the user's (AI collaboration guide §2).
**Date drafted:** 2026-07-25
**Supersedes:** `PHASE0_adapter_points.md` §2b, which recommended the opposite and was based on incomplete information.

---

## 1. The problem

Proposal §4.4 specifies Control A as: replicate J-lens on a standard open LLM **using Anthropic's released code**, and confirm that **ablation of the identified subspace disproportionately harms multi-step tasks**.

Neither half holds as written:

- The released code performs readout only. No intervention machinery exists in `anthropics/jacobian-lens` (verified: full-repo grep, plus `hooks.py` containing only a read-side `ActivationRecorder`).
- The released *data* documents swap and steering protocols, but no ablation protocol.
- The paper, however, **fully specifies the ablation**.

So the gap is in the release, not in the method. Those are different things, and conflating them is what produced the earlier wrong recommendation.

## 2. Options

**(a) Adopt `probe-swap` as Control A.** Released prompts, released protocol. But it is a *swap*, and it tests J-space *privilege* (J-space component vs. complementary component), not suppression. Building a swap harness in Phase 0 and an ablation harness in Phase 3 defeats guide §3a, which requires Control B to run through the *exact same* harness.

**(b) Implement the paper's ablation.** Specified to the level of k, the operation, the layer-band parameterisation, the confound guard, and the control, with magnitudes reported on named public benchmarks.

## 3. Decision

**Option (b).** Implement the paper's J-space ablation. Retain `probe-swap` as a secondary check if time allows, not as Control A.

Rationale: it is what §4.4 actually names; it is what Phase 3 needs; it is what Control B runs through; and it is validated against published magnitudes on public benchmarks rather than "against nothing." The harness built here *is* the Phase 3 harness — this is the single largest piece of Phase 0 work and it is not throwaway.

**Sign-off:** ☐ accepted ☐ modified ☐ rejected — _______________

---

## 4. Specification

All parameters below are from the paper (§"J-space ablation leaves most capabilities intact while impairing internal reasoning") unless marked **[ours]**.

### 4.1 The ablation operation

At each token position, across a band of layers:

1. Identify the **k = 10** most strongly activated J-lens vectors at that (position, layer).
2. **Zero the residual stream's projection onto each.**
3. Continue the forward pass.

**Confound guard — mandatory.** Do not ablate any tokens that appear in the **top-10 of a clean forward pass** at that position. Without this, the ablation suppresses what the model was about to output and the resulting degradation measures nothing. This is the first identified failure mode in this project that manufactures a *false positive*; everything previously flagged risked false negatives.

### 4.2 Dose-response

Three strengths, differing in **layer range only** — k stays at 10. The paper's bands are on a 0–100 reindexed scale with workspace ≈ L38–92 for Sonnet 4.5; the experiential-report variant used L38–54, described as "the first third of the workspace range."

**[ours]** Since the band is model-specific, the Phase 0 model's band must be derived before ablation, using the four lens-derived statistics (next-token top-k accuracy, excess kurtosis, top-1 autocorrelation vs. position-shuffled null, effective dimensionality of `W_U J_ℓ`). Light / medium / heavy are then defined as proportional sub-ranges of *that* band, not as literal L38–54 / L38–92.

### 4.3 Controls

- **Random-direction control at matched size and matched layer range.** The paper reports this at the medium range; **[ours]** run it at all three, since Phase 3 needs the baseline distribution across the sweep anyway.
- Multiple random draws with recorded seeds, reported as a distribution rather than a single draw (proposal §4.8).
- **[ours]** `apply(use_jacobian=False)` gives a logit-lens readout at no cost. Worth recording as a second reference point.

### 4.4 Evaluation — the degrading side

The paper used a 50-prompt controlled two-hop set. **No released file has n=50**; it appears unreleased.

**[ours] Substitute `data/experiments/probe-swap.json`.** Its 90 two-hop items carry an `answer` field and its documented baseline is "greedy next-token == `answer`" — so the prompts are directly usable as a multi-hop *accuracy* eval even though we are not running its swap protocol. Released, Apache-2.0, and structurally the right task. Score: greedy next-token accuracy, clean vs. ablated, per layer band.

### 4.5 Evaluation — the intact side

Selectivity is as much the finding as the degradation. If everything degrades, that is damage, not J-space ablation.

- Pretraining-corpus **top-1 match**: fraction of positions at which the ablated model's most-likely next token agrees with the unablated model's.
- Public tasks the paper found essentially unaffected at heavy ablation: **MMLU, SQuAD extractive QA, sentiment classification, CoLA.** Any subset is adequate; two is enough.

**Do not use GSM8K-with-chain-of-thought as a reasoning probe.** The paper shows it is substantially more robust than the same problems answered directly, because the model externalises intermediates onto the page. A weak effect there would mean nothing.

### 4.6 Pre-check before Control A means anything

**[ours]** The paper's degrading result depends on the unablated model being **near ceiling** on the multi-hop set. A small open model may not be, and then there is nothing to degrade — producing a failed Control A caused by model selection, exactly the AI guide §1.4 worry.

**Gate: measure unablated greedy accuracy on the 90 probe-swap prompts first.** If it is not high enough to leave clear headroom, Control A cannot distinguish a broken instrument from a model that cannot do the task, and the model choice must be revisited before proceeding. This converts §1.4's qualitative "too small to reason" concern into a measurable go/no-go — record the threshold before looking at the number.

---

## 5. Pass / partial / fail

Scored **per finding**, not per phase (guide Phase 0 exit criteria).

**Pass** — all of: multi-hop accuracy drops substantially under ablation; the drop is monotone across the three layer bands; the matched random-direction control shows a clearly smaller drop at every band; intact-side tasks remain near baseline.

**Partial** — degradation occurs but at least one of: no dose-response across bands; random control not clearly separated; intact-side tasks also degrade, i.e. the effect is not selective. Document *which*, since each bounds a different downstream claim.

**Fail** — no differential between multi-hop and intact-side tasks, or the random control matches the candidate.

**Record magnitudes, not directions** (guide Phase 0, step 4). Phase 3 needs to know what a real positive effect looks like through this instrument.

---

## 6. Proposal §4.4 amendment text

> Control A was specified as replicating J-lens "using Anthropic's released code" and confirming that ablation of the identified subspace disproportionately harms multi-step tasks. The released code (`anthropics/jacobian-lens`, Apache-2.0) implements readout only — lens fitting, application, and visualisation — and contains no intervention machinery; the released prompt sets document swap and steering protocols but no ablation protocol. The ablation is, however, fully specified in the paper. Control A is therefore a faithful implementation of a published protocol using released prompt data, **not** a replication using released code, and the paper must say so plainly. The multi-hop evaluation set used in the original ablation experiment (n=50) does not appear to be released; the 90 two-hop prompts of `data/experiments/probe-swap.json` are substituted, scored on greedy next-token accuracy against their `answer` field.

---

## 7. What this locks in for Phase 3

The harness built here is the Phase 3 harness. From the first line it must have: clean-top-k exclusion, matched random-direction control with recorded seeds, layer-band parameterisation, and resumability. Two further pieces are needed for Phase 3 but not for Control A, and should be designed in now rather than bolted on:

- **k-sweep capability** (proposal §4.7). The paper fixed k=10 and swept the band; the proposal sweeps k. Phase 3 therefore has two candidate sweep axes and `prereg_phase3.md` must state which — sweeping both multiplies runs against a budget that assumed neither.
- **Complementary-component baseline** (from the probe-swap design). Proposal §4.8 specifies matched-size random subspaces; the paper's control is the complementary component of the same representation at matched magnitude, plus a clamp to test for routing. Both belong in Phase 3. A candidate R-space that beats random draws but not its own complement has not earned H1.
