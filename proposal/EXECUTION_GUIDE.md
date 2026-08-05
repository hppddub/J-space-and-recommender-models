# Execution Guide — R-Space Generalization Test

**Companion to:** `jspace_generative_recommenders_proposal.md` (referred to below as **the proposal**)
**Purpose:** operational instructions for executing the proposal without losing its distinctions.
**Target deadline:** ~August 29, 2026 (AoE)

---

## 0. How to use this document

The proposal is the source of truth for *what is being claimed and why*. This document is the source of truth for *how to run it*. Where the two conflict, the proposal wins — and this document should be corrected.

**The central failure mode this project is designed against is scope drift toward an unearned positive claim.** Every consideration in Section 4 of the proposal exists because a natural, tempting shortcut would collapse two separate claims into one. Under time pressure those shortcuts get very attractive. The discipline below is what prevents that.

### The re-read rule

**Before starting any phase, re-read the proposal sections listed in that phase's "Read first" block.** Not skim — read. Each phase below names 2–4 specific sections. This is not ceremony: the considerations are easy to nod along to when reading the plan and easy to forget when writing the actual ablation loop three weeks later.

### The three questions

At the end of every work session, answer these in the lab log (Section 2.3):

1. **Which claim does today's work support?** Name it as H1, H2, H3, or "none — infrastructure." If the answer is vague, the work was probably unfocused.
2. **Did I import any property of J-space by assumption today?** Specifically: did anything in today's code or notes treat the R-space as small, verbalizable, or legible *without* having measured it? (Proposal 4.1, 4.3, 4.7)
3. **Would this step still be defensible if the final result is null?** If a step only makes sense on the assumption of a positive result, it's a design leak.

---

## 1. Workspace setup

### 1.1 Repository structure

```
rspace/
  proposal/
    jspace_generative_recommenders_proposal.md   # read-only reference copy
    EXECUTION_GUIDE.md                            # this file
  preregistration/
    prereg_phase3.md          # written BEFORE Phase 3 runs
    prereg_phase4.md          # written BEFORE Phase 4 runs (see 4.4 below)
    amendments.md             # any deviation from prereg, timestamped + justified
  src/
    jlens/                    # toolchain: Anthropic's released code + adapters
    readout/                  # R-space identification (Phase 2)
    ablation/                 # ablation harness, incl. random-subspace baselines
    tasks/                    # easy/hard task construction
    probes/                   # nonlinear sensitivity probe (4.5)
  configs/                    # one config per experiment run, version-controlled
  results/
    raw/                      # unprocessed run outputs, never edited by hand
    figures/
  logs/
    lab_log.md                # dated running log, append-only
  paper/
```

### 1.2 Environment discipline

- Pin every dependency version. An ablation result that can't be reproduced isn't a result.
- Set and record random seeds for: model init/load, random-subspace draws, task sampling, any data shuffling. The random-subspace baseline (proposal 4.8) is meaningless if the draws aren't reproducible.
- Every run writes a config snapshot + git commit hash into its output directory. No exceptions.

### 1.3 Reference copies

Keep a read-only copy of the proposal in the repo. When a phase's "Read first" block sends you back to it, read the copy in the repo — not a remembered version of it.

---

## 2. Standing rules (apply to every phase)

### 2.1 Terminology discipline

**Always write "R-space," never "J-space," when referring to the structure in the recommender.** This is not pedantry — proposal 4.1 introduces the separate name specifically to block the silent import of J-space's other properties. If a draft sentence reads naturally with "J-space" substituted in, that sentence is probably assuming something that hasn't been shown.

Banned phrasings in code comments, logs, and drafts unless the corresponding hypothesis has actually been tested:
- "the workspace" (assumes the workspace interpretation — use "candidate subspace" or "R-space" until Phase 4 says otherwise)
- "verbalizable" applied to anything in the recommender (proposal 4.1 — explicitly not tested)
- "the small subspace" (assumes H2 — proposal 4.7)
- "what this direction represents" (assumes H3 — proposal 4.2)

### 2.2 The separation rule

H1, H2, and H3 are reported separately (proposal 4.3). In practice this means:
- Separate result files. Separate figures. Separate paragraphs in the paper.
- No composite metric that blends causal importance with compactness or legibility.
- If you find yourself writing a sentence that asserts two of them at once, split the sentence.

### 2.3 Lab log

Append-only, dated entries in `logs/lab_log.md`. Each entry: what was run, config hash, what the result was, the three questions from Section 0. Negative and broken runs get logged too — the diagnosis of a null (proposal 4.4) depends on knowing what was tried.

### 2.4 Pre-registration

Phases 3 and 4 are pre-registered before they run (details in those phases). This is the single most important defense for a null result: a pre-registered null is evidence, a post-hoc null is an anecdote.

---

## 3. Nuance ledger

Every consideration from proposal Section 4, where it gets enforced, and how to verify it wasn't dropped. **Check this table at every phase gate.**

| # | Consideration (proposal §) | Enforced in | Verification check |
|---|---|---|---|
| 1 | No verbalization channel — construct rewritten (4.1) | Phase 2; all writing | Grep the repo for "verbaliz" — every hit must be in a *disclaimer* context, never a claim |
| 2 | IDs → concepts needs external grounding (4.2) | Phase 5 | Legibility evidence traces to metadata that existed before this project. No researcher-generated labels in the evidence chain |
| 3 | Ablation ≠ three claims (4.3) | Phases 3, 4, 5 | Three separate result files exist; no figure asserts more than one H |
| 4 | Nulls need positive controls (4.4) | Phase 0 (Control A), Phase 3 (Control B) | Both controls have passing, logged results *before* any null is written up |
| 5 | Retrieval vs. reasoning; missed ≠ absent (4.5) | Phase 1 (task design), Phase 4 | Easy/hard task split defined and frozen before Phase 3 results are seen; nonlinear probe run as sensitivity check |
| 6 | Existence ≠ legibility (4.6) | Phase 6 gate; paper structure | Phase 6 not started unless both 0a and 0b passed. Paper's claims section shows the dependency explicitly |
| 7 | Smallness measured, not assumed (4.7) | Phase 3 | Results are a curve over *k*, not a verdict at one *k*. Knee analysis reported either way |
| 8 | Random matched-size baseline (4.8) | Phase 3 (and everywhere ablation appears) | Every ablation number in the paper has a matched random-draw distribution beside it |

---

## 4. Phase-by-phase execution

### Phase 0 — Toolchain validation (Control A)

**Read first:** proposal §1, §4.4 (Control A), §5 row 0.

**Objective:** confirm the J-lens pipeline reproduces the original paper's basic findings on a standard open LLM, *before* pointing it at a new domain. This is Control A. Without it, a later null is uninterpretable.

**Procedure:**
1. Obtain Anthropic's released J-lens code. Read its actual API and assumptions rather than reconstructing them from the paper or from memory — note where it hardcodes assumptions about vocabulary structure, tokenizer, or model architecture, since those are exactly the places Phase 2 will need adapters.
2. Select a small open LLM the code supports (or can be made to support with minimal modification). Document the choice and why.
3. Reproduce the core reported findings: identify the J-space subspace, and confirm that ablating it disproportionately degrades multi-step reasoning while leaving fluent generation comparatively intact.
4. Record the magnitude of the effect you reproduce, not just its direction. Phase 3 needs a sense of what a real positive effect looks like through this instrument.

**Guardrails:**
- If the replication only partially succeeds, **document exactly which parts did and didn't reproduce.** This bounds every downstream claim. Per-finding reporting is also the established practice for this result: the published external replication reported its own outcomes finding by finding rather than as a single verdict.
- Do not proceed to Phase 3 conclusions on the strength of a Control A that didn't actually pass. A failed Control A means the instrument is unvalidated and no null is diagnosable (proposal 4.4).

**Exit criteria:** documented replication attempt with explicit pass/partial/fail per finding, effect magnitudes recorded, adapter points for a non-language vocabulary identified.

**Failure modes:**
- *Code doesn't run on available compute* → downscale the LLM before downscaling the validation. A weaker Control A on a smaller model beats no Control A.
- *Replication fails outright* → this is a significant finding and changes the project. Stop and reassess: the honest paper may become "we could not reproduce X," which is publishable but is a different paper. Log it and make an explicit decision rather than quietly moving on.

---

### Phase 1 — Model and task setup

**Read first:** proposal §2, §4.5, §7, §5 row 1.

**Objective:** stand up an open generative recommender and — critically — define the easy/hard task gradient **before** any subspace analysis begins.

**Procedure:**

*1a. Model selection.* Start with the lightest viable option (proposal §7 recommends HSTU-BLaIR or GPTRec for compute reasons). Confirm before committing:
- It is genuinely autoregressive over a discrete token vocabulary (this is the whole architectural precondition — proposal §2).
- You can access intermediate activations and the output projection. If you can't, J-lens has nothing to work with.
- It trains or loads within your compute budget with time to spare for Phase 3's sweep, which is the expensive part.

*1b. Dataset.* Pick from proposal §7 (Amazon Reviews 2023 subsets, MovieLens-1M, Steam). Two selection criteria that matter later:
- **Item metadata must be pre-existing and rich enough for Phase 5.** Check this now, not in Phase 5. If the dataset has no independent category/tag/description metadata, H3 is untestable on it (proposal 4.2) and you should know that before you invest.
- Sequence lengths must support the hard-task construction below.

*1c. Task gradient — the important part.* Construct two task families (proposal 4.5):
- **Easy:** single-hop next-item prediction from recent history. Straightforward associative continuation.
- **Hard:** compositional or multi-step preference inference. Worked examples from the proposal: inferring a preference shift across a sequence containing distractor interactions; transferring an inferred taste across categories.

**Guardrails:**
- **Freeze the task definitions and commit them before running Phase 3.** Proposal §10 step 3 is explicit about this: if the easy/hard split is designed after seeing ablation results, Phase 4 is post hoc and its differential-impact signature means nothing.
- Validate the gradient is real *before* using it: confirm the base model performs measurably worse on hard tasks than easy ones. If the model is equally good (or equally bad) at both, the split isn't capturing a difficulty difference and Phase 4 can't distinguish anything.
- Match the task families on confounds where possible — sequence length, item popularity distribution, category coverage. Otherwise a differential ablation effect might just be tracking sequence length.

**Exit criteria:** model loaded with activation access confirmed; dataset chosen with metadata availability verified for Phase 5; easy/hard task sets constructed, validated for a real difficulty gradient, and committed to version control with a timestamp predating Phase 3.

---

### Phase 2 — Candidate R-space identification

**Read first:** proposal §4.1 (in full), §4.2, §5 row 2.

**Objective:** adapt the J-lens readout to an item-token vocabulary and produce a candidate subspace — while explicitly *not* claiming verbalizability.

**Procedure:**
1. Adapt the readout: J-lens projects intermediate activations onto the output vocabulary to find directions that make future tokens more likely. In this domain the vocabulary is semantic IDs / item tokens. Port the mechanism, and document every place the port required a judgment call.
2. Produce the candidate subspace as a **ranked set of directions**, not a fixed-size selection. Phase 3 needs to sweep over size (proposal 4.7), so Phase 2 must not commit to a *k*.
3. Sanity-check the readout produces structure rather than noise: e.g., do top directions correspond to *anything* systematic (frequency, category, recency)? This is a smoke test on the instrument, **not** evidence for H3 — do not let it become the legibility claim (proposal 4.2).

**Guardrails:**
- **This phase produces the R-space, not "the workspace."** The construct under test is defined in proposal 4.1 as: *a small subspace of activations with disproportionate causal influence on the model's future (item-token) output.* Nothing more is claimed at this stage — and "small" in that sentence is what Phase 3 measures, not something Phase 2 asserts.
- Write down, in the lab log, every adaptation decision and its alternative. If the readout later comes up null, these decisions are the first suspects (proposal 4.5's "readout too weak" branch), and reconstructing them from memory afterward isn't credible.
- Resist the urge to interpret directions. Every hour spent narrating what a code "seems to mean" is an hour producing evidence that proposal 4.2 rules inadmissible.

**Exit criteria:** working readout producing ranked directions; documented adaptation decisions; smoke test logged and explicitly labeled as a smoke test, not as H3 evidence.

**Failure mode:** *The readout is mathematically ill-defined for this architecture.* If the port requires assumptions that break the method's logic rather than merely adapting it, that is itself the paper's finding — a principled account of why the technique does or doesn't extend is a real methodological contribution. Escalate to an explicit scope decision rather than forcing a broken port through.

---

### Phase 3 — Existence testing (H1 + H2)

**Read first:** proposal §4.3, §4.4 (Control B), §4.7, §4.8, §5 row 3.

**Objective:** establish (or fail to establish) that the candidate R-space is causally important (H1) and measure whether it is compact (H2). This is the core of the minimum viable paper.

**Pre-register before running.** Write `preregistration/prereg_phase3.md` containing: the *k* values in the sweep, the number of random draws per *k*, the ablation method, the metrics, the statistical test, and the threshold that will count as H1 support. Commit it before the first real run. Deviations go in `amendments.md` with justification — deviating is allowed, hiding it is not.

**Procedure:**

*3a. Control B — domain-internal positive control (proposal 4.4).* Before testing the candidate subspace, ablate a component in the recommender you have independent reason to believe matters — a core embedding or attention layer — using the *exact same ablation harness*. Confirm the method detects that known importance. If it doesn't, the harness is broken and no result from this phase means anything. **Run this first. Do not defer it.**

*3b. Dimensionality sweep (proposal 4.7).* Run the ablation across a range of candidate subspace sizes/ranks — top-*k* directions for a spread of *k*. Do not test a single fixed size. The proposal is explicit that fixing a size in advance risks a self-fulfilling null.

*3c. Random matched-size baselines (proposal 4.8).* At **every** *k* in the sweep, run multiple random-subspace ablations of the same size. Report the resulting distribution, not a single draw. The candidate's impact must significantly exceed this distribution for H1 to hold. This is what distinguishes "this subspace is special" from "ablating anything of this size hurts."

*3d. Analysis.*
- **H1:** does candidate-subspace ablation impact significantly exceed the matched random distribution? Report effect size and the full baseline distribution, not just a p-value.
- **H2:** plot ablation impact as a function of subspace size. Look for a knee — a small size past which added dimensions contribute little. **A smooth, diffuse curve with no knee is a negative result for H2, and it is a real finding, not a failure to report.** Report the full curve either way (proposal 4.7).

**Guardrails:**
- H1 and H2 are separate results with separate figures (proposal 4.3). A single "the subspace matters and is small" conclusion is exactly the bundling the proposal exists to prevent.
- H1 passing with H2 failing is a legitimate, publishable outcome: *a causally important but diffuse subspace exists.* Proposal 4.3 says so explicitly. Do not treat it as a partial failure to be fixed by searching for a better *k*.
- Do not tune *k* to find a knee. If you find yourself extending the sweep after seeing results, that's an amendment — log it as one.

**Exit criteria:** Control B passing and logged; full sweep complete with matched random baselines at every *k*; H1 and H2 reported separately with the full curve; pre-registration deviations documented.

**This is the minimum viable paper boundary.** Per proposal §6, Phases 0–3 alone constitute a defensible standalone contribution — positive *or* null. If time runs short, stopping cleanly here with a well-diagnosed result is the plan, not a fallback to apologize for.

---

### Phase 4 — Task-gradient specificity test

**Read first:** proposal §4.5 (in full — including the nonlinear-readout note), §5 row 4.

**Objective:** determine whether the R-space is specifically reasoning-relevant, or just generically important. This is what separates a workspace interpretation from "we found some important directions."

**Pre-register before running** (`prereg_phase4.md`): the differential metric, and what magnitude of easy-vs-hard difference will count as support. The task sets themselves were frozen in Phase 1 — confirm they haven't been touched since.

**Procedure:**
1. Run the Phase 3 ablation separately on the frozen easy and hard task sets.
2. Test for a **differential**: is the performance drop from ablating the R-space larger on hard tasks than easy ones? Proposal 4.5 is precise that this differential — not overall ablation impact — is the signature that distinguishes a reasoning-relevant workspace from a generically important subspace.
3. Include the random matched-size baselines here too, per task family. A differential that also appears for random subspaces isn't evidence about the R-space.
4. **Nonlinear sensitivity check (proposal 4.5, "additional consideration"):** J-lens is a linearized readout. If the structure in the recommender is highly nonlinear, the linear method could return a false negative independent of whether a workspace exists. Train a simple nonlinear probe (e.g., a shallow classifier on candidate-subspace activations) as a check on whether nonlinear structure is being missed.

**Guardrails:**
- **If there is no differential, that is evidence against the workspace interpretation — regardless of how strong the overall H1 result was.** Proposal 4.5 states this directly. A strong H1 with no easy/hard differential means "important subspace, not a workspace," and the paper should say exactly that.
- The interpretive branch matters here. A null in Phase 3–4 could mean: (a) the phenomenon doesn't transfer, (b) the readout is too weak, or (c) the recommender does associative retrieval with no multi-step reasoning to support a workspace at all. Control A speaks to (b) at the pipeline level, Control B speaks to (b) within this domain, the nonlinear probe speaks to (b) at the method-linearity level, and the base model's own easy-vs-hard performance gap from Phase 1 speaks to (c). **Write the diagnosis explicitly against all four pieces of evidence** rather than reporting an unqualified negative (proposal 4.4).

**Exit criteria:** differential result reported with per-task-family random baselines; nonlinear probe run and reported; explicit null-diagnosis written against Controls A and B, the nonlinear probe, and the Phase 1 difficulty gradient.

---

### Phase 5 — Legibility testing (H3) — stretch goal

**Read first:** proposal §4.2 (in full), §4.6, §5 row 5, §6.

**Objective:** test whether the R-space maps to anything externally interpretable. **Explicitly a stretch goal** — proposal §6 states H3 is not required for a valid Stage 0 paper.

**Procedure:**
1. Use **only pre-existing external item metadata** — category labels, tags, descriptions that were attached to items independently of this project (proposal 4.2). Confirm provenance: metadata must predate and be independent of your analysis.
2. Assess via either quantitative correlation between subspace activation and known item attributes, or agreement between independent labelers working *from item metadata alone*.
3. Report agreement statistics, not selected examples.

**Guardrails — this phase has the highest risk of producing inadmissible evidence:**
- **No post-hoc researcher narrative may serve as sole evidence** (proposal 4.2). "This direction seems to capture nostalgia" is not a result. The bias problem is specific and real: different people rationalize the same code differently, so an interpretation that isn't externally anchored isn't checkable.
- If no reliable externally-grounded mapping can be established, **report legibility as unresolved or negative.** Do not force an interpretation. Proposal 4.2 is explicit that a causally-important-but-illegible subspace is a valid and reportable finding.
- Legibility failing does not retroactively weaken H1/H2. They are separate claims (proposal 4.3, 4.6).

**Exit criteria:** H3 reported as supported, unresolved, or negative, with the evidence chain traceable to pre-existing metadata.

---

### Phase 6 — Auditing application — conditional, likely out of scope

**Read first:** proposal §4.6, §6, §3 (Stage 1), §9.

**Gate — check before any work begins:** Phase 6 starts **only if both Stage 0a (H1 + H2) and Stage 0b (H3) passed.** Not 0a alone. Proposal 4.6 is explicit that moving from "we found a causally important subspace" to "we can audit it" presumes two separate things, and neither establishes the other.

**Default disposition:** per proposal §6, treat Phase 6 as **out of scope for the initial submission and mention it only as future work.** Presenting it as more than future work without its prerequisites would reproduce exactly the two-unproven-links jump the proposal was written to avoid.

**If the gate genuinely passes and time remains:** probe for hidden proxy-objective signals — engagement-correlated internal activity not present in the final output score. Keep it framed as an audit/transparency direction.

---

## 5. Decision gates

Explicit go/no-go points. Log the decision and its rationale at each (proposal §10 step 5).

| Gate | When | Question | If no |
|---|---|---|---|
| **G0** | After Phase 0 | Did Control A pass well enough to trust the instrument? | Reassess: the paper may become a replication-difficulty report. Decide explicitly |
| **G1** | After Phase 1 | Is there a real easy/hard difficulty gradient in base model performance? | Redesign hard tasks. Phase 4 is uninterpretable without it |
| **G2** | Before Phase 3 | Is `prereg_phase3.md` committed, and were tasks frozen before results were seen? | Do not run. Fix the ordering first |
| **G3** | After Phase 3 | Do we have enough for the minimum viable paper (§6)? | Stop and write. A clean Phase 0–3 result beats a rushed Phase 4 |
| **G4** | After Phase 3 | Time for Phase 4 without compromising Phase 3 write-up? | Skip Phase 4; note as future work |
| **G5** | After Phase 4 | Did both 0a and 0b pass? | Phase 5 stretch / Phase 6 out of scope. State as future work |

**On timeline:** proposal §6 anticipates the full six-phase pipeline is unlikely to complete before the deadline. That's the expected case, not the failure case. Phases 0–3 with a properly diagnosed null is described in the proposal as *arguably more useful to the field than an under-controlled positive result.* Plan the write-up around G3, and treat anything past it as upside.

---

## 6. Writing the paper

**Read first:** proposal §6, §8, §9 (in full).

**Claims structure.** Mirror proposal 4.6's staging explicitly in the paper's own structure — existence (0a), legibility (0b), auditing (Stage 1, conditional on both) — so a reader can see the dependency rather than infer composition.

**The honesty checklist (proposal §9) is a pre-submission checklist, not background material.** Before submitting, verify each of its nine items appears explicitly and prominently in the text:

1. J-space is a recent single-lab result on one text-only LLM, replicated in part on a second open-weight text model; both have natural-language token vocabularies
2. Verbalizability is **not** tested here — explicitly excluded (4.1)
3. Legibility claims depend entirely on external pre-existing metadata (4.2)
4. Causal importance, compactness, legibility reported as **three separate results** (4.3)
5. Nulls accompanied by both controls and diagnosed accordingly (4.4)
6. Linear readout acknowledged as a possible false-negative source (4.5)
7. No auditing/safety claim unless existence *and* legibility both established (4.6)
8. Subspace size measured by sweep, never assumed (4.7)
9. All ablations reported with matched-size random baselines (4.8)

**One framing point the proposal makes that belongs up front in the paper:** nobody outside these companies can inspect production systems, so "extending this to Meta/TikTok's pipelines" was never literally testable. The honest claim is that this was tested on an open architecture of the same class. Stating that substitution explicitly in the introduction pre-empts the obvious reviewer objection instead of letting them find it.

**Venue fit (proposal §8):** Interp4Discovery (Atlanta, Aug 29 deadline) is the strongest fit — the project is framed as using interpretability to investigate an open question rather than assuming a settled result. IAB fits if the recommender is framed as the agent under interpretation; ATTRIB is a secondary fit if the sweep/ablation methodology is emphasized as a general attribution technique. A negative or partial result should be framed as a methodological contribution — a properly controlled generalization test — and targeted at venues that value rigorous negative results.

---

## 7. Session-start checklist

Run this at the top of every working session:

- [ ] Which phase am I in? Have I read that phase's "Read first" sections **today**?
- [ ] Which hypothesis (H1/H2/H3) does today's work serve?
- [ ] Am I about to assume smallness, verbalizability, or legibility anywhere? (4.1, 4.3, 4.7)
- [ ] Does every ablation I run today have its matched random baseline? (4.8)
- [ ] Are my task definitions still the frozen Phase 1 versions? (4.5)
- [ ] Is any interpretation I'm forming traceable to pre-existing external metadata? (4.2)
- [ ] Would today's step still be defensible if the final result is null?
