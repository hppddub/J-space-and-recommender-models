# Lab Log — R-Space Generalization Test

**Repo location:** `logs/lab_log.md`
**Governed by:** `EXECUTION_GUIDE.md` §2.3
**Rule: append-only.** Entries are added at the bottom. Nothing above is edited
after the fact. If something was wrong, a later entry corrects it — the wrong
version stays.

Consolidated 2026-08-02 from per-session drafts. **Consolidation preserved
wording; it did not edit content.** Where an entry was written after the fact it
says so in the entry itself.

---

## Index

| # | Date | Phase | Entry | Outcome |
|---|---|---|---|---|
| 01 | — | pre-0 | Project setup | infrastructure |
| 02 | 2026-07-25 | 0 | Step 0 — artifact availability | Ablation code **absent** from the release |
| 03 | 2026-07-25 | 0 | Step 1 — J-lens code inspection | Readout only confirmed; `LensModel` port boundary found |
| 04 | 2026-07-25 | 0 | Step 1b — paper read, 3 open items | Ablation protocol **is** fully specified in the paper |
| 05 | 2026-07-25 | 0 | Appendix retrieval **failed**; Control A spec drafted | §A.7/§A.9 unobtainable via fetch |
| 06 | 2026-07-25 | 0 | Appendices resolved from PDF · **GATE: Control A** | Template lens found; single-token constraint softened |
| 07 | 2026-07-25 | 0 | Pre-harness checks (first executed code) | Code default targets **final** layer, paper uses penultimate |
| 08 | 2026-07-25 | 0 | Model selection drafted; **ablation harness built** | 15/15 synthetic tests |
| 09 | 2026-07-27 | 0 | **ABORTED** — CUDA OOM | Two model copies will not fit a T4 |
| 10 | 2026-07-27 | 0 | Headroom, Qwen3.5-4B · **DECISION: model** | strict 63.3% — **missed** 70% threshold |
| 11 | 2026-07-28 | 0 | Model change; Qwen3-4B headroom | Qwen3.5-4B is a **hybrid SSM**; new model scores 55.6% |
| 12 | 2026-07-28 | 0 | Qwen3-8B headroom; Control A cost · **DECISION: model final** | 64.4% — scale buys 1.1pp; Control A ≈ 5 units |
| 13 | 2026-07-28 | 0 | Stage B — band derivation *(reconstructed)* · **prereg signed** | Band **L20–31**; kurtosis anomaly recorded |
| 14 | 2026-07-29 | 0 | Stage B2 — readout verification | Median rank **1** at L30; content from L10 |
| — | 2026-07-29 | 0 | **DECISION: Amendments 002 & 003** | Eval metric fixed; `heavy-paper` added |
| 15 | 2026-07-29 | 0 | **CONTROL A: the run** | 3/4 criteria PASS; intact side **FAIL** |
| 16 | 2026-07-29 | 0 | Control A — coarse intact tasks | MMLU **intact**; selectivity established |
| — | pending | 0 | **GATE G0** | not yet taken |

### Decision gates

| Gate | Status |
|---|---|
| Control A specification (step 0.3) | signed 2026-07-25 (session 06) |
| Phase 0 model selection | signed 2026-07-27, superseded 2026-07-28 (sessions 10, 12) |
| `prereg_controlA.md` | signed 2026-07-28 (session 13) |
| Amendments 002, 003 | signed 2026-07-29 |
| **G0 — did Control A pass well enough to trust the instrument?** | **OPEN** |
| G1–G5 | not reached |

### Templates

The entry, broken-run and decision-gate templates live in the original
`lab_log.md` preamble and are unchanged. Session 01 (project setup) is the
worked example there and is not duplicated here.

---

# Entries

<!-- Append below. Newest at the bottom. Do not edit entries above this line. -->

## [2026-07-25] Session 02 — Phase 0 Step 0: artifact availability verification

**Phase:** 0 (Step 0 — precondition check, no compute)
**Read-first sections re-read today:** proposal §1, §4.4 (Control A), §5 row 0; guide Phase 0 block; AI guide §1.4, §1.5, §3 (rows 10, 12)
**Hardware:** local CPU (desk research only) · **CU spent:** none

### What was run

- **Script / notebook:** none — no code obtained or executed this session
- **Config:** n/a
- **Git commit:** `<fill in — commit of this log entry>`
- **Seeds:** n/a
- **Runtime:** n/a

### Result

*Raw findings only. Sources listed so each claim is traceable.*

**Paper.** "Verbalizable Representations Form a Global Workspace in Language Models," Gurnee, Sofroniew, Lindsey et al. (16 authors), Anthropic. Published on Transformer Circuits Thread 6 July 2026; also on arXiv as 2607.15495. Available in full.

**Companion code.** `github.com/anthropics/jacobian-lens`, Apache-2.0, released alongside the paper. README states: *"Reference implementation. Not maintained and not accepting contributions."* Repository top level: `assets/`, `data/`, `jlens/`, `tests/`, `LICENSE`, `README.md`, `pyproject.toml`, `uv.lock`, `walkthrough.ipynb`. One commit on `main`.

Documented API surface in the README, in full:
- `jlens.from_hf(hf_model, tokenizer)` — wrap a HuggingFace causal LM
- `jlens.fit(model, prompts, checkpoint_path)` — fit a lens; `JacobianLens.merge()` to combine disjoint slices
- `JacobianLens.from_pretrained(repo, filename)` — load a pre-fitted `.pt` (one `[d_model, d_model]` matrix per layer)
- `lens.apply(model, prompt, positions)` → `(lens_logits, model_logits, _)`
- slice-visualisation rendering (layer × position grid, d3-based)

The estimator is documented in the `jlens.fitting` module docstring: `lens_l(h) = unembed(J_l @ h)`, `J_l = E[∂h_final / ∂h_l]`, with cotangents summed over current-and-future target positions then averaged over source positions.

**No ablation, steering, patching, or evaluation code is documented in the README.** Fit → apply → visualise is the whole documented surface. `data/experiments/` and `data/evaluations/` are described as holding "replication and lens-eval prompt sets," synthetic and Anthropic-authored, Apache-2.0. The `jlens/` package tree was not enumerated this session (GitHub blocked automated directory listing); the README's usage section is the basis for the above.

**Pre-fitted lens weights.** Hosted on the HuggingFace Hub and referenced from `walkthrough.ipynb` for at least `Qwen/Qwen3.5-4B` and `Qwen/Qwen3.6-27B`, both fitted at n=1000 prompts on a Salesforce-wikitext corpus. Paper's own lenses use 1000 sequences of 128 tokens; README states quality saturates quickly and ~100 prompts is usable. No model weights or corpora are bundled in the repo.

**Neuronpedia demo.** Interactive J-lens demo hosted at `neuronpedia.org/jlens`, zero-setup, running on open-weights models. Pre-fitted Qwen3.6-27B lens weights are publicly available via Neuronpedia (credited by a third-party port).

**Third-party reimplementations located (not evaluated).**
- `idhantgulati/j-lens` — minimal reimplementation on Qwen3.5-4B. README lists `interventions.py` (steering, ablation, lens-coordinate swaps) and `evals.py` (paper §A.6 pass@k evaluations, §4.1 workspace-band metrics). Downloads eval prompt data from the official Anthropic repo on first use.
- `WeZZard/jlens-qwen36` — Apple Silicon / MLX visualiser port, Qwen3.6-27B 4-bit. Notes readouts are noisy at 20 fitting prompts and research-grade needs 100+.

**Secondary reporting on the ablation result** (not the paper itself; to be checked against the paper before use): the strong ablation collapse is attributed to a controlled multi-hop reasoning eval, whereas on GSM8K chain-of-thought solving is reported to be substantially more robust to ablation than direct answering. Separately, the technique is reported to surface single-token concepts only, and J-space to appear at intermediate layers (roughly one-third to two-thirds depth).

### Reading of the result

Step 0's precondition is **partially satisfied, not satisfied.** Paper, readout code, pre-fitted lens weights, and a hosted demo all exist and are openly licensed. What is *not* evidenced is an ablation or intervention harness in the official release — and ablation is the load-bearing half of Control A, since proposal §4.4 defines Control A as confirming "ablation of the identified subspace disproportionately harms multi-step tasks," not as confirming the readout reproduces.

This does not show it is definitely absent. The definitive check is enumerating `jlens/` and reading the `data/experiments/` and `data/evaluations/` READMEs, which is Phase 0 Step 1 and has not been done. But two things point the same way: the README documents its usage surface completely and never mentions intervention, and a third party found it worth writing `interventions.py` and `evals.py` from scratch while still pulling prompt data from the official repo.

If confirmed, the consequence is that Phase 0 is part replication and part **construction**: the ablation harness has to be written. Per guide §3a that same harness is what Phase 3 runs against Control B and the candidate R-space, so the work is not wasted — but it moves earlier in the schedule than the guide's phase ordering implies, and design decisions taken under Phase 0 time pressure will propagate into every Phase 3 number.

Bears on no hypothesis. This is instrument availability, not evidence about anything.

### The three questions

1. **Which claim does today's work support?** None — infrastructure. Nothing today bears on H1, H2, or H3.
2. **Did I import any property of J-space by assumption today?** No — but a near miss to record. The session began from the assumption that "everything should be there," which is the same shape of error the project is built to catch, applied to tooling rather than to a claim. The assumption was partly wrong. Nothing in today's notes describes an R-space at all; the recommender was not touched.
3. **Would this step still be defensible if the final result is null?** Yes, and more so than most. Establishing what the instrument does and does not include is precisely what makes a later null diagnosable rather than ambiguous (proposal 4.4).

### Deviations

None from any pre-registration — none exist yet. One deviation from the proposal's literal text is now foreseeable and flagged early: proposal §4.4 specifies replicating "using Anthropic's released code." If the ablation harness is self-written or adapted from a third-party reimplementation, Control A is no longer purely a replication of released code, and the paper must say so plainly rather than let "we used Anthropic's released code" stand unqualified. Record the decision when it is made.

### Next step

Phase 0 Step 1: clone the repo and enumerate `jlens/` and `data/`; read `data/experiments/README` and `data/evaluations/README` to determine what the replication prompt sets actually cover. Settle definitively whether ablation code exists. Free tier, no GPU, no purchase (AI guide §1.5).

**Decisions left open:**
- Whether to write the ablation harness from scratch or adapt `idhantgulati/j-lens` as a reference. Bears on the §4.4 wording above.
- Whether the availability of pre-fitted n=1000 lenses for Qwen3.5-4B and Qwen3.6-27B changes the AI guide §1.4 compute budget, which assumed lens fitting as a cost driver. Fitting cost may be largely removable; the §1.4 concern that a small model has too little multi-step reasoning to degrade is untouched by this and still stands.
- Which eval Control A targets. The multi-hop-vs-GSM8K asymmetry above, if it holds in the paper, means the choice materially changes the effect size recorded in Step 5 — pick it deliberately in Step 3, not by default.

---

## [2026-07-25] Session 03 — Phase 0 Step 1: J-lens code inspection

**Phase:** 0 (Step 1 — read the released code's actual API and assumptions)
**Read-first sections re-read today:** proposal §1, §2, §4.4 (Control A), §4.5, §5 row 0; guide Phase 0 (procedure step 1, exit criteria); AI guide §1.3, §1.4, §4.3 (Phase 0 emphases)
**Hardware:** Claude sandbox, 1 CPU core, no GPU · **CU spent:** none

### What was run

- **Script / notebook:** none. `git clone --depth 1` + file reads + one grep. Nothing installed (`pip install -e .` deliberately not run), nothing executed from the repo, no model loaded.
- **Config:** n/a
- **Repo inspected:** `anthropics/jacobian-lens` @ `581d398613e5602a5af361e1c34d3a92ea82ba8e`, committed 2026-07-02, sole commit on `main`, Apache-2.0
- **Git commit (ours):** `<fill in — commit adding PHASE0_adapter_points.md>`
- **Seeds:** n/a
- **Runtime:** n/a

### Result

*Raw findings. Full detail in `proposal/PHASE0_adapter_points.md`.*

Repo is ~1,050 lines of library code across eight modules: `protocol.py` (52), `hooks.py` (74), `examples.py` (181), `hf.py` (211), `lens.py` (216), `fitting.py` (388), `vis.py` (515), `_logging.py` (53). Plus `tests/` (six files incl. `tiny.py`, 87 lines), `data/` (17 JSON prompt sets), `walkthrough.ipynb`.

Public API (`__all__`) in full: `ActivationRecorder`, `HFLensModel`, `JacobianLens`, `Layout`, `LensModel`, `configure_logging`, `fit`, `from_hf`, `jacobian_for_prompt`.

**Intervention machinery: absent.** Grep across all `.py` and `.ipynb` for `ablat|steer|intervene|intervention|clamp|patch|swap|zero_out|project_out|set_activation` → zero hits in library code (only `monkeypatch` fixtures in `tests/test_vis_modes.py`). `hooks.py` contains one class, `ActivationRecorder`, which registers forward hooks that store block outputs and never write back; there is no write-side hook in the package. `JacobianLens.apply()` is `@torch.no_grad()` and detaches recorded activations.

**Intervention protocols: present in prose.** `data/experiments/README.md` and `data/evaluations/README.md` define Swap (*"clamping a lens coordinate replaces one token's direction with another's at every band layer at the specified positions, then samples the continuation"*) and, under `verbal-introspection`, the steering-vector construction (unit-normalized transpose row for the token, scaled by the layer's mean residual norm times a strength scalar, added at every band layer over a span; strength 0 as control).

**No ablation protocol anywhere.** The two documented intervention types are swap and steering. Nothing in the release specifies zeroing or projecting out a subspace.

Released prompt sets: six `lens-eval-*` readout-quality evals (93–107 items each; pass@k over lens rank of `intermediates`, no intervention) and eleven `data/experiments/*` sets, of which `probe-swap.json` (90 two-hop factual items, `intermediate` / `swap_to` / `swap_answer`, per-category breakdown) is the only one structured as a causal test on multi-step reasoning.

**Port boundary is clean.** All architecture assumptions sit behind one `LensModel` Protocol (`n_layers`, `d_model`, `layers`, `tokenizer`, `encode`, `forward`, `unembed`). `tests/tiny.py` is a working 87-line from-scratch implementation. `protocol.py` states the tokenizer is used only by visualisation helpers and that *"Fitting and `apply()` never touch it."*

**Hardcoded constants:** `SKIP_FIRST_N_POSITIONS = 16` (`fitting.py:42`) is the only substantive one, exposed as `skip_first=` on `fit` and `jacobian_for_prompt`. Rationale in-source: early positions act as attention sinks with atypical residual statistics. Defaults: `max_seq_len=128`, `dim_batch=8`, `checkpoint_every=1`, `resume=True`, `force_bos=True`.

Other: `transport()` is `residual @ J.T`, `J_l` a single `[d_model, d_model]` fp16 matrix per layer; `apply(use_jacobian=False)` yields a logit-lens baseline; `merge()` requires matching `source_layers` and `d_model`; `from_pretrained` imports `huggingface_hub` lazily.

Every released experiment and eval scores single vocabulary tokens; `capacity.json` explicitly filters pools to words that tokenize to a single token under the target model.

### Reading of the result

Step 0's open question is settled: the ablation harness is not in the release, and the specific experiment proposal §4.4 names as Control A is not among the released protocols in any form. Phase 0 is therefore part replication and part construction, as anticipated at the end of Session 02.

Two things partially offset this. The swap and steering procedures are specified precisely enough to implement to spec rather than reconstruct. And `probe-swap` offers a released, prompt-backed causal test on two-hop reasoning that could serve as Control A directly — which would make Control A a genuine replication rather than a reimplementation validated against nothing. Whether that substitution is legitimate depends on whether probe-swap manipulates a J-lens direction or a separate linear probe; the README says linear probe, and the paper has to settle it.

The port itself looks less hazardous than the guide's framing assumed. The guide anticipated hardcoded vocabulary/tokenizer/architecture assumptions scattered through the code; instead there is a single Protocol and a worked example of implementing it. The tokenizer requires no port at all.

Against that, two risks surfaced that were not previously on the list, and both are more serious than anything the clean Protocol removes:

`skip_first=16` is tuned to LM sequence statistics. Recommender interaction sequences truncated at 20–50 would lose 30–80% of their positions under that default. Inheriting it unexamined is a plausible route to a null that looks genuine and isn't — proposal §4.5's "readout too weak" branch, self-inflicted.

The single-token constraint is a threat to the port's premise. If an item is represented by several semantic-ID tokens, then "read out an item" is not the operation this instrument performs. Proposal §2 established that generative recommenders have the right *output structure*; it did not establish that one item maps to one vocabulary token. That gap belongs in Phase 1 model selection.

Bears on no hypothesis. Instrument characterisation only.

### The three questions

1. **Which claim does today's work support?** None — infrastructure. Nothing bears on H1, H2, or H3.
2. **Did I import any property of J-space by assumption today?** No. The recommender was not touched and no R-space was described. One thing to watch going forward: the readout-quality evals (`lens-eval-*`) measure whether the lens *reads out* known intermediates, and it would be easy to let a good score there stand in for evidence about the R-space's contents. It is not — that is guide §2.1's "what this direction represents," i.e. H3, and these evals are a Phase 0 instrument check on a language model.
3. **Would this step still be defensible if the final result is null?** Yes. Characterising what the instrument does and does not do is what separates a diagnosable null from an ambiguous one (proposal §4.4). The `skip_first` finding in particular is only useful in the null branch.

### Deviations

None from any pre-registration. One proposal correction is now required rather than foreseeable: proposal §4.4 specifies Control A as replicating *"using Anthropic's released code"* and as testing *ablation*. Neither holds as written — the released code performs readout only, and no ablation protocol was released. Amend the proposal, or re-specify Control A around `probe-swap`, and state the substitution plainly in the paper rather than letting the original wording stand.

### Next step

Read the paper against the three open items in `PHASE0_adapter_points.md` §6, in this order:

1. Does `probe-swap` manipulate a J-lens direction or a separate linear probe? Determines whether Control A can be a released-protocol replication.
2. How is the **workspace band** derived? Every released experiment reports over it; nothing in the code computes it, and it will have to be derived for the recommender by a method not present in the release.
3. Which experiment produces the reported multi-hop ablation collapse, and what precisely was ablated? This is the effect magnitude Phase 0 Step 5 needs on record.

Free tier throughout; no GPU, no purchase (AI guide §1.5).

**Decisions left open:**
- Control A specification: adopt `probe-swap` (option a) or implement ablation from the paper (option b). Pending item 1 above.
- Whether to consult `idhantgulati/j-lens` as a reference implementation of `interventions.py` / `evals.py`. Not evaluated; bears on the §4.4 amendment either way.
- Phase 1 model selection now has a hard new criterion — item-to-token cardinality — alongside the guide's existing three. GPTRec's GPT-2 layout is already supported by `_LAYOUTS`; HSTU's block structure needs checking against requirement #1 before it is considered.

---

## [2026-07-25] Session 04 — Phase 0 Step 1b: paper read against the three open items

**Phase:** 0 (Step 1b — resolve the open items `PHASE0_adapter_points.md` §6 flagged as requiring the paper, not the code)
**Read-first sections re-read today:** proposal §1, §4.4, §4.5, §4.7, §4.8; guide Phase 0, Phase 3 (3a, 3b, 3c); AI guide §3 (rows 3, 8, 10), §4.3
**Hardware:** Claude sandbox, no GPU · **CU spent:** none

### What was run

- **Script / notebook:** none. Paper read: Transformer Circuits version (canonical) plus arXiv HTML 2607.15495v1. Sections read in full: Methods; "The J-space acts as a Global Workspace"; "The J-space's structure supports its function." **Not read:** appendices, alignment auditing, counterfactual reflection training.
- **Git commit (ours):** `<fill in — commit adding PHASE0_paper_findings.md>`
- **Seeds / runtime:** n/a

### Result

*Full detail in `proposal/PHASE0_paper_findings.md`. Raw findings only here.*

**Item 1 — probe-swap.** Two-stage. The probe is fit without the J-lens (mean residual-stream activation over prompts implying the same intermediate through different surface cues, minus mean over all intermediates), then decomposed against the J-lens dictionary by gradient pursuit into a J-space component (k=25, ~10–15% of probe variance) and a J-orthogonal remainder. Swap results, n=90: J-space component 61%, raw J-lens vectors 60%, non-J-space component 28%, non-J-space with J-space coordinates clamped 6%.

**Item 2 — workspace band.** Not one method. CKA between layers over pairwise J-lens vector similarities gives a three-block structure (sensory / workspace / motor). Four statistics converge on ~L38 → ~L92 on the paper's reindexed 0–100 scale: J-lens top-k accuracy at predicting the actual next token (marks the end), excess kurtosis of the readout logit distribution (marks the start), autocorrelation of the top-1 lens token across positions against a position-shuffled null, and effective linear dimensionality of `W_U J_ℓ`. The paper states that all four are J-lens-derived and could be artifacts of the method, and answers this with the ignition experiment, which uses no lens: input embedding replaced by `(1-α)·e_B + α·e_A`, α swept, activation's position measured along the line from that trial's pure-B to pure-A activation. Smooth and proportional early; from ~L38 it sits near one endpoint with a sharp threshold switch.

**Item 3 — the ablation.** Section "J-space ablation leaves most capabilities intact while impairing internal reasoning." At each token position across a band of layers, identify the k=10 most strongly activated J-lens vectors and zero the residual stream's projection onto each. Do not ablate tokens appearing in the clean forward pass's top-10. Light / medium / heavy differ in **layer range**, not k. A random-direction control at the medium layer range is reported alongside. Magnitudes: controlled multi-hop eval near-ceiling unablated, heavy ablation to near zero; pretraining-corpus next-token prediction perturbed substantially less; across fourteen tasks, MMLU / odd-one-out / SQuAD / sentiment / CoLA essentially unaffected at heavy ablation, while Caesar-cipher, analogy, summarization, TriviaQA, multi-hop, translation and sonnet writing fall below unablated Haiku 4.5. GSM8K with chain-of-thought substantially more robust than the same problems answered directly.

Other parameters recorded: ablation k=10; occupancy plateau ~25; concept decomposition k=16; J-space fraction of variance in excess of a same-size random control never exceeding 10%; lens fitted on 1000 prompts of 128 tokens.

### Reading of the result

**The Session 03 recommendation was wrong and is hereby corrected rather than edited away.** `PHASE0_adapter_points.md` §2b recommended adopting `probe-swap` as Control A on the grounds that implementing ablation would leave Control A "validated against nothing." The ablation is in fact specified in the paper to the level of k, the projection operation, the layer-band parameterisation, the clean-pass exclusion, and the control, with magnitudes reported on named public benchmarks. Option (b) is now the recommendation, with probe-swap kept as a secondary check. The gap Session 03 found was in the release, not in the method — those are different things and I conflated them.

Three findings change downstream design rather than merely informing it.

The **clean-top-10 exclusion** is a confound guard with an exact recommender analogue: do not ablate directions for items already in the top-k of the clean next-item distribution. Omitting it would make ablation trivially suppress what the model was about to recommend, producing a large H1 "confirmation" that is an artifact. This is the first thing found so far that could manufacture a *false positive*; everything previously flagged risked false negatives. It goes in `prereg_phase3.md` explicitly.

**Workspace loading** — cosine similarity between the residual stream and a concept's lens vector, averaged over relevant positions in the unmodified pass — predicts swap success, and the paper's own number-word failure case is read as either computation outside the workspace or the working representation not aligning with the lens vectors for those tokens. That is proposal §4.5's "readout too weak" branch occurring inside the original domain. Measuring item workspace loading before interpreting any recommender null is now required, not optional.

**The band is a prerequisite with no home in the current plan.** Every experiment reports over it; Phase 3 cannot ablate "across a band" without one; and deriving it is a step that appears nowhere in the proposal or the guide. It belongs at the end of Phase 2. Two of the four J-lens-derived statistics (kurtosis, effective dimensionality) port without reinterpretation; next-token accuracy and autocorrelation both presuppose a token stream with language-like local redundancy. The ignition method ports well and is readout-independent, which matters more here than it did in the original given §4.5.

One point in the project's favour, worth stating in the paper rather than leaving implicit: the paper fixed k=10 for ablation and swept the layer band. Smallness was established by occupancy and excess-variance measures against same-size random controls, not by an ablation sweep over k. Proposal §4.7's sweep is therefore a genuine strengthening on that axis. It also means Phase 3 has two candidate sweep axes, k and layer band; the prereg must say which, since sweeping both multiplies runs against a budget (AI guide §1.4) that assumed neither.

Bears on no hypothesis. Instrument and protocol characterisation only.

### The three questions

1. **Which claim does today's work support?** None — infrastructure. Nothing bears on H1, H2, or H3.
2. **Did I import any property of J-space by assumption today?** No, and one active resistance to record. Reading the paper's own results is the highest-risk moment for importing smallness by assumption, because the paper reports the J-space as small and it is tempting to carry "k=10 worked there" into the recommender as a default. It is not a default; proposal §4.7 requires it measured. The value k=10 is recorded here as *what the original did*, not as a setting to inherit. Same for the L38–92 band: that is Sonnet 4.5's band, and it is a number about a language model.
3. **Would this step still be defensible if the final result is null?** Yes, and the clean-top-10 finding is the first one that is *more* useful in the positive branch than the null branch — it is the guard that stops a false positive. The workspace-loading diagnostic is the mirror image, and only matters in the null branch.

### Deviations

None from any pre-registration. The proposal §4.4 amendment flagged in Session 03 still stands but its content changes: Control A can now be a faithful implementation of a fully specified published protocol, but still not "using Anthropic's released code," since the release contains no intervention machinery. Amendment text should say exactly that, and should not overclaim replication.

### Next step

Read the three remaining gaps, in this order:

1. **§A.9, extension to multi-token concepts** (template lens, oracle lens). Governs the single-token constraint and therefore Phase 1 model selection. Needed before the Phase 1 go/no-go, not after.
2. **§A.7, methodological details and ablations.** Check whether `skip_first` and the n=1000 averaging corpus have documented sensitivity analyses that could be reused rather than re-derived — bears directly on adapter point #6, currently the highest-risk item in the catalogue.
3. Whether the 50-prompt multihop reasoning set used for the ablation eval is released; no released file has n=50.

Free tier, no GPU, no purchase.

**Decisions left open:**
- Control A: option (b) recommended but not yet decided. Decide and log before Phase 0 Step 2 (model selection).
- Phase 3 sweep axis: k, layer band, or both. Prereg question; do not let it be settled by whatever the harness happens to make easy.
- Where band derivation lives. Recommend adding it as Phase 2 exit criterion; this is a change to the guide, so it needs an explicit decision rather than a quiet insertion.

---

## [2026-07-25] Session 05 — Phase 0: appendix attempt (partial fail) and Control A specification

**Phase:** 0 (steps 0.2 partial, 0.3 complete pending sign-off)
**Read-first sections re-read today:** proposal §2, §4.4, §4.7, §4.8, §7; guide Phase 0 (exit criteria, failure modes), Phase 3 (3a–3d); AI guide §1.4, §2, §3 (rows 4, 10)
**Hardware:** Claude sandbox, no GPU · **CU spent:** none

### What was run

- **Attempted:** retrieve paper appendices §A.7 (methodological details and ablations) and §A.9 (multi-token extensions).
- **Method:** `transformer-circuits.pub/2026/workspace/index.html` at 50,000 then 130,000 token limits; `arxiv.org/html/2607.15495v1` at 40,000; `arxiv.org/pdf/2607.15495v1`.
- **Git commit (ours):** `<fill in — commit adding DECISION_control_A.md>`
- **Seeds / runtime:** n/a

### Result

**Appendix retrieval: FAILED. Neither §A.7 nor §A.9 obtained in primary form.**

The transformer-circuits fetch returned identical content at 50k and 130k limits, truncating at the same point mid-sentence in "Using the J-lens for alignment auditing." Raising the limit 2.6× changed nothing, so the ceiling is in the retrieval path or the page, not in the request. The arXiv HTML truncates earlier still — MathML markup roughly triples its token cost per unit of prose. The arXiv PDF was refused on URL provenance grounds.

**What was established from primary text already held:**

- Main text on the single-token limitation: the J-lens "only identifies vectors associated with concepts that correspond to single tokens in the model's vocabulary, but many important concepts correspond to multiple tokens," with a pointer to §A.9 for extensions. A footnote in the broadcast-depth section repeats that J-lens vectors "are constrained to single tokens" and suggests the highest-kurtosis SAE features may approximate the true workspace directions more closely for that reason.
- Main text enumerating §A.7's contents: variants covering present-only versus future token effects, frozen attention patterns during Jacobian computation, and number of averaging contexts, with the claim that qualitative results are robust to these choices. **Position masking is not in that list.**
- From the Session 03 repo enumeration (primary, ours): `jlens/` contains no template-lens or oracle-lens module.
- From the repo README: lens quality "saturates quickly (§9.3); ~100 prompts is usable"; the paper's lenses use 1000.

**Control A specification (step 0.3): drafted, in `proposal/DECISION_control_A.md`, pending sign-off.** Decision recommended: implement the paper's ablation (option b) rather than adopt `probe-swap` (option a). Specification records k=10, projection zeroing, layer-band dose-response, the clean-top-10 confound guard, matched random-direction controls, pass/partial/fail criteria, proposal §4.4 amendment text, and two Phase 3 design requirements.

### Reading of the result

**On §A.9.** The residual gap is real but does not block the Phase 1 decision it was supposed to gate. Whatever A.9 specifies, it is not in the release — that is established from our own enumeration, not inferred. So choosing an architecture whose items span several semantic-ID tokens would mean implementing an appendix method *on top of* implementing the ablation harness, inside a timeline that already expects not to finish. The decision-relevant conclusion holds without the text: **prefer an architecture where one item maps to one vocabulary token.** Three secondary sources agree the extensions are partial and unreleased; that is corroboration, not evidence, and is recorded as such.

**On §A.7.** More useful than expected, by absence. The main text's enumeration of A.7's contents does not include position masking, and `SKIP_FIRST_N_POSITIONS` is a code constant rather than a paper variant. The hope in Session 04 was that A.7 might contain a `skip_first` sensitivity analysis reusable instead of re-derived; that hope is probably unfounded. Adapter point #6 — the highest-risk item in the catalogue — must be re-derived for the recommender. Treat this as likely-not-conclusive: it rests on the completeness of a parenthetical "e.g." list.

**On the Control A decision.** Two things in the specification are additions rather than transcriptions, and both should be visible as such.

The **pre-check** (spec §4.6) converts AI guide §1.4's qualitative worry — a small model may not do enough multi-step reasoning to have anything to degrade — into a measurable gate: unablated greedy accuracy on the 90 probe-swap prompts, with a headroom threshold recorded *before* the number is seen. Without it, a failed Control A cannot be attributed between instrument and model capability, which is the whole purpose of Control A.

The **probe-swap substitution** (spec §4.4) uses released prompts for a purpose other than their documented protocol: its 90 two-hop items carry an `answer` field and a documented greedy-next-token baseline, so they serve as a multi-hop accuracy eval even though the swap protocol is not being run. This is a substitution and the paper must name it, since the original n=50 set appears unreleased.

Bears on no hypothesis. Instrument specification only.

### The three questions

1. **Which claim does today's work support?** None — infrastructure.
2. **Did I import any property of J-space by assumption today?** No. One near-miss worth recording: the specification transcribes k=10 from the paper as *the value the original used for ablation*. It is not a default for the recommender. Proposal §4.7 requires k measured by sweep, and spec §7 flags that Phase 3 now has two candidate sweep axes precisely so this does not get settled by inheritance.
3. **Would this step still be defensible if the final result is null?** Yes. The clean-top-10 guard is the exception that matters more in the positive branch — it is what stops a false-positive H1 — and specifying it before any run is what makes that credible.

### Deviations

The proposal §4.4 amendment is now drafted rather than pending (spec §6). It states two departures: Control A is an implementation of a published protocol using released prompt data, not a replication using released code; and the n=50 multi-hop eval set is substituted with the 90 probe-swap prompts.

### Next step

1. **Sign off or modify `DECISION_control_A.md`.** Everything downstream in Phase 0 depends on it.
2. Retry §A.9 and §A.7 by another route if one is cheap — a mirror, the ar5iv rendering, or a manual download. **Do not block on it.** §A.9 is wanted for the Phase 1 go/no-go, and the fallback (prefer one-item-one-token) is already actionable. If still unobtainable at that gate, record it as a known unread section rather than letting it silently become "checked."
3. Proceed to step 0.4, Phase 0 model selection, now carrying an extra criterion from spec §4.6: the model must have measurable headroom on two-hop accuracy.

**Decisions left open:**
- Control A sign-off (above).
- Phase 3 sweep axis — k, layer band, or both. Prereg question; spec §7 flags it so the harness does not settle it by default.
- Whether to consult `idhantgulati/j-lens` as a reference implementation now that ablation is being built rather than adopted. Still not evaluated.

---

## [2026-07-25] GATE — Control A specification (step 0.3)

**Gate question:** which protocol does Control A implement, given that the released code contains no intervention machinery?

**Evidence considered:** `DECISION_control_A.md`; `PHASE0_adapter_points.md` §2; lab log Sessions 03–05; paper §"J-space ablation leaves most capabilities intact while impairing internal reasoning"; §A.7.

**Decision:** **Accepted as drafted — option (b).** Implement the paper's J-space ablation. `probe-swap` retained as an optional secondary check. Signed off by user, 2026-07-25.

**Rationale:** it is what proposal §4.4 names; it is what Phase 3 needs; guide §3a requires Control B to run through the identical harness, so a swap harness built now would have to be replaced. The protocol is specified in the paper to the level of k, operation, layer-band parameterisation, confound guard, and control, with magnitudes on named public benchmarks.

**Consequence for scope:** the ablation harness becomes the largest remaining Phase 0 task and is built to Phase 3 requirements from the first line — clean-top-k exclusion, matched random-direction controls with recorded seeds, layer-band parameterisation, resumability, k-sweep capability, complementary-component baseline. Proposal §4.4 is amended per `DECISION_control_A.md` §6. The n=50 multi-hop eval set is substituted with the 90 `probe-swap.json` prompts scored on greedy next-token accuracy.

**Deadline check:** ~35 days to 29 August AoE. Phase 0 has consumed six sessions of desk work and no compute. The minimum viable paper (proposal §6, Phases 0–3) remains reachable, but only if the harness starts now — it is the shared dependency of Control A, Control B, and the Phase 3 sweep, and nothing downstream can begin without it.

### Next step

Step 0.4 — Phase 0 model selection. Carries three criteria now: `LensModel` protocol implementable; measurable headroom on two-hop accuracy (`DECISION_control_A.md` §4.6); and fits compute, which is now a much weaker constraint given §A.7's corpus-size finding. Verify the penultimate-vs-final target-layer question at the same time.

---

## [2026-07-25] Session 07 — Phase 0: pre-harness checks (first executed code)

**Phase:** 0 (pre-0.4 checks)
**Read-first sections re-read today:** proposal §4.5, §4.7; guide Phase 0 (procedure step 1), §1.2; AI guide §1.3, §2
**Hardware:** Claude sandbox — 1 CPU core, ~3 GB RAM, no GPU · **CU spent:** none

### What was run

- **Repo:** `anthropics/jacobian-lens` @ `581d398613e5602a5af361e1c34d3a92ea82ba8e`
- **Env:** `torch 2.13.0+cu130` from PyPI, CPU only (`cuda.is_available() == False`); `pytest`. Note `--no-deps` install fails — torch 2.13 loads CUDA libs at import, so the full nvidia dependency set is required even for CPU use. Relevant for anyone reproducing on a constrained box.
- **Scripts:** `/tmp/e2e2.py` — fit/apply on `tests.tiny.TinyDecoder` (n_layers=8, d_model=16, vocab_size=32, seed=0), 10 synthetic prompts, `source_layers=[2,4,6]`, `skip_first=0`, `max_seq_len=48`.
- **Git commit:** `<fill in>` · **Seeds:** TinyDecoder seed=0; no random-subspace draws this session

### Result

**Repo test suite:** `tests/test_fitting.py`, `tests/test_ranks_of.py`, `tests/test_compute_slice.py` — **21 passed**, 2.13 s. (`test_hf_layout.py`, `test_vis_modes.py` not run; require `transformers`.)

**End-to-end fit → apply: works.** Lens fitted over layers [2,4,6], each `J_l` shape (16,16), dtype float32 in memory. `apply` returns a 3-tuple `(dict[source_layer → logits], Tensor, Tensor)`; per-layer logits shape (n_positions, vocab). `apply(..., use_jacobian=False)` logit-lens baseline also runs.

**Check 1 — target layer. Code default is FINAL, paper default is PENULTIMATE.**

- By inspection: `_check_layer_indices(None, None, 8)` returns `([0,1,2,3,4,5,6], 7)`. `target = n_layers - 1` when `target_layer is None`.
- Empirically: fitting with default vs `target_layer=-2` produces J matrices differing by max |Δ| = 0.025578, **2.40% of max magnitude**. Not numerically equivalent.
- The code's own docstring notes "In some cases, targeting the penultimate layer can give a better-conditioned `J_l`," but does not default to it.
- §A.7 states the paper's default takes z at the penultimate layer, omitting the last transformer block, because "including the last layer can sometimes increase the number of noisy artifacts in lens-readouts."

**Fix: pass `target_layer=-2`.** One kwarg. The parameter is exposed.

**`skip_first` illustrated:** on a 48-token sequence the default `skip_first=16` drops 33% of positions.

**Correction to an earlier session.** Session 03 recorded J-lens matrices as fp16. In memory they are float32; the on-disk dtype was not verified this session (the checkpoint key differs from what the probe assumed). Treat the fp16 claim as unconfirmed.

### Reading of the result

Check 1 resolves as a genuine code/paper divergence, not ambiguity in my reading. Anyone running the released code out of the box gets a different recipe from the one the paper reports — and per §A.7, a noisier one. Left undetected it would have degraded Control A in exactly the way that is hardest to attribute: a weaker-than-published effect, with no way to tell recipe from instrument from model. Cheap to fix, expensive to miss. **Set `target_layer=-2` in every fit from here, and record it in the Control A config.**

Check 2 is **partially** satisfied and must not be logged as complete. What is established: the package imports, its own tests pass, and `fit → apply` executes end-to-end against a from-scratch `LensModel` implementation with no HuggingFace involvement. That eliminates "the code does not run" as a failure cause before harness work begins, and confirms `tests/tiny.py` is a working template for the Phase 2 adapter.

What is **not** established: anything about whether the lens recovers meaningful content. `TinyDecoder` is random-weight, vocab_size=32, with linear residual blocks chosen so the Jacobian stays well-conditioned. It cannot show that readouts are interpretable, and no claim of that kind is made here. The real Check 2 — a supported open LLM on Colab, ~10 prompts per §A.7 — remains outstanding and is the user's to run.

Bears on no hypothesis. Instrument verification only.

### The three questions

1. **Which claim does today's work support?** None — infrastructure.
2. **Did I import any property of J-space by assumption today?** No. The relevant discipline today was the opposite one: a passing end-to-end run on a toy model is easy to write up as "the pipeline is validated," which would overstate it. The distinction between code-path validation and instrument validation is stated explicitly above so a later session cannot read this entry as the latter.
3. **Would this step still be defensible if the final result is null?** Yes, and the target-layer finding especially — a null obtained on the wrong recipe would have been undiagnosable.

### Deviations

None.

### Next step

Step 0.4, model selection, then the ablation harness. Carry forward into the Control A config: `target_layer=-2`; `skip_first` low (§A.7 shows position masking buys nothing); corpus ~10–100 prompts, not 1000.

**Decisions left open:** which open LLM for Phase 0; Phase 3 sweep axis (k, layer band, or both).

---

## [2026-07-25] Session 08 — Phase 0: model selection drafted; ablation harness built

**Phase:** 0 (step 0.4 drafted; harness complete and tested on synthetic data)
**Read-first sections re-read today:** proposal §4.3, §4.4, §4.7, §4.8; guide §1.2, §2.2, Phase 3 (3a–3d); AI guide §2, §4.1
**Hardware:** Claude sandbox — 1 CPU core, ~3 GB RAM, no GPU · **CU spent:** none

### What was run

- **`jlens/hf.py` `_LAYOUTS` read directly.** Covers Llama/Qwen/Mistral/Gemma/OLMo/StableLM via `Layout("model")`, multimodal wrappers, Phi, **GPT-2** (`transformer`/`h`/`ln_f`/`wte`), and Pythia (`gpt_neox`). `walkthrough.ipynb` references `Qwen/Qwen3.5-4B` and `Qwen/Qwen3.6-27B`, lenses under `neuronpedia/jacobian-lens`.
- **Ablation harness written** — `src/ablation/{directions,harness,sweep}.py`, ~500 lines.
- **Synthetic test suite** — `tests/test_ablation.py`, 15 tests, **15 passed in 64 s**, CPU, no model download.
- **Git commit:** `<fill in>` · **Seeds:** TinyDecoder seed=0; test seeds fixed inline

### Result

**Model selection (`DECISION_phase0_model.md`, pending sign-off):** Qwen3.5-4B recommended, gated on the two-hop headroom pre-check. 27B is out on compute (~54 GB fp16 exceeds even A100-40GB). GPT-2 layout confirmed present, which retroactively validates the GPTRec claim made in `PHASE0_adapter_points.md` from a partial read.

**Harness built to all six Phase 3 requirements:** clean-top-k exclusion; matched random controls with mandatory seeds; layer-band parameterisation; resumable checkpointing with config snapshot and git hash; k-sweep; next-k complementary baseline.

Tests passing include two that exist to catch silent failure rather than to demonstrate success:

- `test_guard_actually_changes_what_gets_selected` — asserts the clean-top-k guard is not a no-op on the test input. A control that cannot fail is not a control.
- `test_rank_deficiency_is_detected_not_hidden` — deliberately collinear direction set; asserts reported rank is 3, not 4.

Also verified: subspace projection leaves a residual orthogonal to every original direction; sequential mode removes no more than subspace mode; identical seeds reproduce bit-identical output; different seeds produce a distribution; `selector="none"` is bit-identical to the clean pass; `AblationSpec` raises on an unseeded random selector.

### Reading of the result

**Two design ambiguities surfaced during implementation that were not visible from reading.** Both are recorded in the README rather than resolved silently.

The paper's phrase "zero out the residual stream's projection onto each" does not distinguish removing the span of the k directions from removing each in turn. For orthogonal vectors these coincide; J-lens vectors are explicitly overcomplete and non-orthogonal (paper §2.3), so they do not. Sequential removal removes strictly less. `mode="subspace"` is the default because it removes the content the experiment is about; `mode="sequential"` exists so the choice is testable. Whichever is used goes in the config.

Relatedly, k J-lens vectors may span fewer than k dimensions. The harness reports the rank actually removed, because "we ablated k directions" is a false sentence if the span was smaller — and it is exactly the kind of false sentence that survives review unchallenged.

**On the harness being the Phase 3 harness.** The temptation under time pressure is a quick Control A script now and a proper harness later. Guide §3a forecloses it: Control B must run through the identical path, so a throwaway would be built twice. Building it once, to spec, is the cheaper option even inside a 35-day window — and the controls are what make it expensive to retrofit, not the ablation itself.

**One catch worth its own line.** The pre-fitted lens at `neuronpedia/jacobian-lens` may have been fitted with the code's default target layer (final) rather than the paper's (penultimate). If so, adopting it silently locks Control A into the non-paper, noisier recipe — in the one experiment whose entire purpose is to be uncontaminated. Check the fitting config; if undocumented, fit our own with `target_layer=-2`, which now costs almost nothing.

Bears on no hypothesis. Instrument construction only.

### The three questions

1. **Which claim does today's work support?** None — infrastructure. The harness is claim-neutral by construction: the same code path runs the candidate condition and every control, which is the point.
2. **Did I import any property of J-space by assumption today?** No, and the code was written to make that harder. `AblationSpec` refuses an unseeded random selector rather than warning. `build_conditions` emits matched controls alongside every candidate rather than as a separate pass that could be skipped. `summarise` deliberately returns candidate and control values as separate objects and computes no composite score (guide 2.2). Terminology discipline held: nothing in the source is called "the workspace."
3. **Would this step still be defensible if the final result is null?** Yes — more so than most. A null run through a harness with matched controls, recorded seeds, reported effective rank, and a config snapshot per run is evidence. The same null from an ad-hoc script is an anecdote.

### Deviations

None. Note that `PHASE0_adapter_points.md`'s GPT-2 claim is now confirmed rather than amended.

### Next step

1. **Sign off or modify `DECISION_phase0_model.md`.**
2. **Run the headroom pre-check** — base model only, no lens, no harness, one forward pass per prompt over the 90 `probe-swap.json` items, scored against `answer`. Record the threshold before looking at the number.
3. Check the pre-fitted lens's target layer; fit our own with `target_layer=-2` if undocumented.
4. Then Control A proper, through the harness.

**Decisions left open:** model sign-off; Phase 3 sweep axis (k, layer band, or both) — still a prereg question, and the harness supports either so it will not be settled by default; whether `mode="sequential"` gets run as a sensitivity check or only `"subspace"`.

---

## [2026-07-27] Session 09 — ABORTED: cell 6 CUDA OOM

**Phase:** 0 · **Hardware:** Colab free tier, T4 (14.56 GiB) · **Git commit:** `<fill in>`

**What was attempted:** the archival strict scoring run (`headroom_check.py`, all 90 prompts) after the in-notebook diagnostic had already completed.

**How it failed:** `torch.OutOfMemoryError` during `caching_allocator_warmup`. Tried to allocate 7.83 GiB; 6.41 GiB free; another process holding 8.05 GiB.

**Diagnosis:** two copies of the model on one GPU. The diagnostic cell loads the model into the notebook's own Python kernel and keeps it resident; `headroom_check.py` is invoked via `!python`, which is a separate process requiring its own full allocation. Not a bug in either — a consequence of mixing in-kernel and shell-invoked execution in one session.

**Ruled out:** not a model-size problem. Qwen3.5-4B in fp16 fits a T4 with ~6 GiB to spare when it is the only resident copy. Nothing about the model choice is implicated.

**Resolution:** `Runtime > Restart session`, then cell 6 alone. Cached weights, cloned repo, and `diagnostic_rows.json` all survive on disk; no re-download.

**Carry forward — this is the useful part.** A T4 holds exactly one copy of this model and no more. **Control A needs the model, a fitted lens, and the ablation harness resident simultaneously**, with two forward passes per prompt. Budget for that before the run rather than discovering it mid-sweep, and keep all execution in one process (either all in-kernel or all shelled out, not both).

---

## [2026-07-27] Session 10 — Headroom pre-check: strict miss, amended pass

**Phase:** 0 (step 0.4 — model selection pre-check)
**Read-first sections re-read today:** proposal §4.4; guide Phase 0, §2.4; AI guide §2, §3 (rows 9, 10, 12)
**Hardware:** Colab free tier T4 (runs) + local CPU (rescore) · **CU spent:** free tier

### What was run

- `headroom_check.py` — 90 prompts from `data/experiments/probe-swap.json`, unablated, greedy, `--dtype float16`. Output: `results/raw/headroom_qwen3.5-4b/{summary,rows}.json`
- Diagnostic cell — same 90 prompts with 6 extra generated tokens, three scoring criteria reported side by side. Output: `diagnostic_rows.json`
- `rescore.py` — offline re-scoring of the saved generations under Amendment 001. Output: `rescored_rows.json`
- **Git commit:** `<fill in>` · **Seeds:** greedy decoding, `do_sample=False`, `num_beams=1` — deterministic, no seeds required
- All three JSONs committed.

### Result

| Criterion | Score | 95% CI | vs 70% threshold |
|---|---|---|---|
| `strict` (pre-registered, paper protocol) | 57/90 = 63.3% | 53.0–72.6% | **miss** |
| `amended` (Amendment 001, R1+R2+R3) | 66/90 = 73.3% | 63.4–81.4% | pass |

Nine items flipped: two by numeral/word equivalence, four by article stripping, three by compound-head matching.

The 33 strict misses categorise as: 10 clear surface-form, 3 arguable, 6 no answer attempted, 14 genuine reasoning or knowledge error.

Nearly every generation terminates in `\nHypothesis:` or `\nQuestion:`.

### Reading of the result

The pre-registered comparison **missed**. That is the primary finding and it is not superseded by the amendment.

Amendment 001 was written after seeing the miss list and says so in its own §2. Its defence is not that it is unbiased — it isn't — but that its rules are general rather than item-specific, that the one rule which could only have been a list (synonyms, for `America` / `the United States`) was deliberately declined at a cost of one item, and that both numbers are reported everywhere.

The amended 73.3% is **not** "the model is fine." It still contains ~6 items the model never attempted and ~14 it got wrong: Mars is blue, Saturn is fourth from the sun, the most populous country's capital is Tokyo. No scoring rule reaches those, and they are the floor on what a 4B model does with two-hop factual reasoning.

Two findings that outlive this session:

**The `\nHypothesis:` pattern.** Qwen3.5-4B is treating `Fact: …` as a document template and continuing the document rather than answering. The framing was designed for a much stronger model. Control A runs on these same prompts, so this carries forward as a live alternative explanation for any effect measured there. Not changed — altering the prompt after seeing results would be a second and larger post-hoc intervention.

**A monotonicity bug, caught by testing rather than inspection.** The first rescore implementation scored the model's answer *phrase* while `strict` scores the *first token*. These are not nested: `North` is a strict pass against `" North America"`, but the phrase is `north america`. The initial version silently removed seven strict passes and returned 59/90. An amendment that takes away items it was never meant to touch is worse than no amendment. Monotonicity is now enforced in code.

Separately, adversarial testing found the compound rule crediting `not red` for `red` — two words, head `red`. No negation appears in the 90 items, so the dataset could never have caught it. Ablated output in Control A plausibly will. Negator guard added.

### The three questions

1. **Which claim does today's work support?** None — infrastructure. This is model selection, not evidence about H1, H2, or H3.
2. **Did I import any property of J-space by assumption today?** No. The live risk today was a different one and it was real: the amendment path leads directly from a missed threshold to a passed one, and the reasoning for each rule is individually plausible. The mitigations are recorded in Amendment 001 §2–§5 rather than relied on from memory.
3. **Would this step still be defensible if the final result is null?** Yes. Establishing that the base model answers roughly two-thirds of these correctly is what makes a later ablation drop interpretable at all — and the honest ceiling matters more in the null branch than the positive one.

### Deviations

Amendment 001 (`preregistration/amendments.md`), signed. Adds three normalisation rules to the headroom scoring criterion; retains and reports the strict number alongside. Explicitly post-hoc with respect to the rules, stated in the amendment itself.

### Next step

Sign `DECISION_phase0_model.md` (entry below), then build the Control A run: fit or verify the lens with `target_layer=-2`, derive the workspace band for this model, then ablate through the harness.

**Note on gate sequencing:** this is *not* G0. G0 asks whether Control A passed well enough to trust the instrument, and Control A has not run. This session closes the model-selection pre-check only.

---

## [2026-07-27] DECISION — Phase 0 model selection (step 0.4)

**Decision question:** does Qwen3.5-4B have sufficient two-hop headroom for Control A to be interpretable? (`DECISION_control_A.md` §4.6, `DECISION_phase0_model.md` §4)

**Evidence considered:** `results/raw/headroom_qwen3.5-4b/summary.json`; `diagnostic_rows.json`; `rescored_rows.json`; Amendment 001; `THRESHOLD_headroom.md` (committed 2026-07-27, before the run).

**The data:** strict 57/90 = 63.3% (missed the 70% threshold); amended 66/90 = 73.3%.

**Decision:** ☐ proceed with Qwen3.5-4B ☐ step up in model size ☐ other — _______________

**Rationale:** ___________

*Points that belong in whatever rationale is written:*

- `THRESHOLD_headroom.md` §2 pre-specified that **50–70% means "Control A is partial by construction, and the write-up must say so and bound every downstream claim accordingly."** The strict result falls in that band. That consequence was written before the run and applies on its own terms regardless of the amendment.
- Stepping up is the only option that addresses the 14 genuine errors. It costs money: 8B fp16 does not fit a T4, and 4-bit quantisation is methodologically dubious for a Jacobian method (AI guide §1.4).
- Proceeding costs nothing and preserves the timeline. ~33 days to 29 August AoE.
- 63.3% → near zero is still a large, measurable fall. What cannot be claimed is the paper's *"near ceiling → near zero"* shape.

**Consequence for scope:** ___________

**Deadline check:** 33 days to ~29 August AoE. Control A has not started; the harness is built and tested on synthetic data but has never touched a real model. The minimum viable paper (proposal §6, Phases 0–3) remains reachable, contingent on Control A running in the next week or so.

---

## [2026-07-28] Session 11 — Model change; Qwen3-4B headroom

**Phase:** 0 (step 0.4, reopened)
**Read-first sections re-read today:** proposal §2, §4.4; guide Phase 0, Phase 1 (1a); AI guide §1.4, §1.5, §2
**Hardware:** Colab free T4 · **CU spent:** free tier

### What was run

- Direct read of `Qwen/Qwen3.5-4B`'s config after `AutoConfig` raised `AttributeError: no attribute 'num_hidden_layers'`.
- Headroom re-run on `Qwen/Qwen3-4B`, 90 probe-swap prompts, greedy, fp16.
- `rescore.py` (frozen Amendment 001 rules) on the resulting generations.

### Result

**Qwen3.5-4B is not a conventional transformer.** `architectures: Qwen3_5ForConditionalGeneration`; `text_config.layer_types` = `[linear_attention ×3, full_attention] × 8` — **24 of 32 layers are linear-attention (SSM/Mamba-style)**, full attention only at indices 3, 7, 11, 15, 19, 23, 27, 31. Also carries a vision tower and `mtp_num_hidden_layers: 1`. Corroborated retrospectively by a `transformers` warning in the first headroom run recommending `flash-linear-attention` and `causal-conv1d`, which went unremarked at the time.

`Qwen/Qwen3-4B` verified as conventional: `Qwen3ForCausalLM`, 36 layers all `full_attention`, no vision config, d_model 2560, vocab 151,936. Pre-fitted lens `hf_model_name: "Qwen/Qwen3-4B"`, `source_layers` 0..34, `target_layer: null` (final-layer recipe, as with every lens in that repo).

Headroom, Qwen3-4B: **strict 50/90 = 55.6%** (CI 45.3–65.4%), amended 60/90 = 66.7%. Category `multihop` 44.8%.

### Reading of the result

A criterion written for Phase 1 model selection — an indexable homogeneous residual stack — was never applied to the Phase 0 model, because "a Qwen" was assumed to be a conventional transformer. That assumption was wrong and unchecked for three sessions.

The objection to the hybrid is interpretive, not mechanical. The J-lens is a gradient method and Neuronpedia fitted one on that checkpoint successfully. But every band statistic reads structure across layer index, and a strict period-4 alternation of block types would plausibly produce period-4 oscillation that is architectural; and Control A's whole function is to eliminate "broken instrument" as an explanation for a null, which is undermined by adding "the phenomenon may not appear in hybrid SSM architectures" as a third candidate.

Qwen3-4B scored **worse** than the model it replaced, by 7 items strict. `DECISION_model_change.md` §6 anticipated exactly this in advance and commits to the switch regardless — reverting on a lower score would mean selecting a model by its score while claiming an architectural rationale.

Item-level diff: 16 items lost, 9 gained. The losses are dominated by genuine knowledge failures, and one is diagnostic — `ex2-city-capital-Munich` asks for the capital of the country containing Munich and the model answered `Munich`. It did not perform the hop at all.

### The three questions

1. **Which claim does today's work support?** None — infrastructure.
2. **Did I import any property of J-space by assumption today?** No. The live risk was different and worth naming: a lower score on the new model creates pressure to revert, which would convert an architectural argument into a score-selection dressed as one. §6 was written before the number was seen precisely to remove that option.
3. **Would this step still be defensible if the final result is null?** Yes. An instrument validated on a hybrid SSM would have bounded every downstream claim in a way that could not be disentangled later.

### Deviations

`DECISION_model_change.md` supersedes `DECISION_phase0_model.md`. Threshold and Amendment 001 rules unchanged. Qwen3.5-4B's numbers retained and reported, not discarded.

---

## [2026-07-28] Session 12 — Qwen3-8B headroom; Control A cost measured

**Phase:** 0 (step 0.4 final; Stage C cost probe)
**Read-first sections re-read today:** proposal §4.4, §4.7, §4.8; guide Phase 0, Phase 3 (3a–3c); AI guide §1.2, §1.4, §1.5
**Hardware:** Colab Pro, **NVIDIA A100-SXM4-80GB** · **CU spent:** approx. 5–10

### What was run

- Verification of `Qwen/Qwen3-8B`: 36 layers, all `full_attention`, `Qwen3ForCausalLM`, d_model 4096. Lens `hf_model_name` matches, `source_layers` 0..34 → final-layer recipe again.
- Headroom, 90 prompts, greedy, **bfloat16**.
- `rescore.py`, frozen rules.
- Control A timing probe: model + pre-fitted lens loaded, real ablation conditions timed on a guessed 12-layer band at k=10.

### Result

**Headroom across all three models tested:**

| Model | Params | Arch | strict | amended | multihop |
|---|---|---|---|---|---|
| Qwen3.5-4B | 4B | hybrid | 63.3% | 73.3% | 51.7% |
| Qwen3-4B | 4B | dense | 55.6% | 66.7% | 44.8% |
| **Qwen3-8B** | **8B** | **dense** | **64.4%** | **74.4%** | **51.7%** |

Qwen3-8B strict 58/90 = 64.4% (CI 54.1–73.6%); amended 67/90 = 74.4%. `element-state` = 40% strict in **all three** models.

**Timing (A100-80GB, 12-layer band, k=10, one prompt):** model load 9 s, 16.4 GB; lens load 2 s, +1.2 GB; peak 17.6 GB. `build_cache` 0.065 s/prompt; conditions 0.163–0.207 s each; uncached topk 0.226 s → caching saves **1.4×**. Extrapolated full sweep (73 conditions × 90 prompts): **20 min ≈ 0.33 h ≈ 5 units.**

### Reading of the result

**Doubling parameters bought 1.1 percentage points.** Qwen3-8B is statistically indistinguishable from Qwen3.5-4B on strict, and the `multihop` subset is identical at 51.7%. Three models, two architectures, a 2× size range, none reaching 70%.

That is a reportable finding rather than a disappointment: it is evidence that the paper's near-ceiling precondition is not reachable with open models in this range, which converts "Control A is partial" from an unexplained weakness into a documented one.

`element-state` at exactly 40% strict in all three models is the `a gas` / `a liquid` article artifact reproducing identically — direct evidence that part of what `strict` measures is formatting rather than reasoning.

On the criterion committed on 2026-07-27, **64.4% misses the 70% threshold.** Amendment 001's rules were frozen before Qwen3-4B and Qwen3-8B were run, so 74.4% is a pre-specified secondary analysis rather than a post-hoc rescue — but the primary is the primary, and it missed. Per `THRESHOLD_headroom.md` §2, 50–70% means Control A is **partial by construction**.

**Compute is not the constraint.** The AI guide §1.4 anticipated Phase 0 as the most expensive phase; that held, but the expense was in discovery — no ablation code in the release, no band-derivation step anywhere in the plan, no affordable model at near-ceiling — not in GPU time. Control A itself is ~5 units.

Two caveats on the timing: it measured **one short prompt** (~16 tokens; some in the set are ~3× longer) and a **guessed** 12-layer band. A 20-layer band with longer prompts scales to roughly 1 h / 15 units. Still well inside budget.

### The three questions

1. **Which claim does today's work support?** None — infrastructure. No lens has yet been applied for any purpose other than cost measurement; the probe's ablations were discarded unexamined.
2. **Did I import any property of J-space by assumption today?** No. The timing probe used a guessed 12-layer band centred in the stack. That band is **not** a result and must not be cited as one — Stage B derives the real band.
3. **Would this step still be defensible if the final result is null?** Yes. The headroom series is the evidence that makes a partial Control A diagnosable rather than merely weak.

### Deviations

None. Threshold and amendment rules unchanged across all three models.

### Assistant calibration note

Claude's compute estimates have been high three times running: "37× redundant work" from caching, then "2–2.5×", against a measured **1.4×**. Consistent under-weighting of the irreducible ablated forward pass. Discount future estimates from that source and prefer measurement.

---

## [2026-07-28] DECISION — Phase 0 model, final

**Question:** which model does Control A run on?

**Evidence:** headroom on three models (above); `DECISION_model_change.md`; `THRESHOLD_headroom.md`; timing probe.

**Decision:** ☐ Qwen3-8B ☐ other — _______________ **Signed:** ___________

**Rationale (to complete):** ___________

*Points belonging in it:*
- Qwen3-8B has the best strict score of the three (64.4%) and a conventional architecture.
- It misses the pre-registered 70% threshold, so Control A is **partial by construction** — a pre-registered outcome, not an improvisation.
- Scale is not the lever: 4B → 8B gained 1.1 points. Testing 14B or 32B is affordable in units (both fit an A100-80GB) but the trend is weak evidence against it, and the real cost is days against a ~31-day deadline.
- Control A costs ~5 units. Compute does not constrain this decision.

**Consequence for scope:** every downstream claim bounded by a Control A validated under partial headroom. The paper states the three-model headroom series explicitly as the reason.

**Deadline check:** ~31 days to 29 Aug AoE. Remaining Phase 0: Stage B (band), Stage C2 (intact-side eval, not yet built), Stage C (Control A run), G0.

---

## Open item recorded — Stage C2 does not exist

`DECISION_control_A.md` §4.5 specifies the **intact side** of Control A: pretraining-corpus top-1 match plus public tasks the paper found unaffected (MMLU, SQuAD, sentiment, CoLA). **No code has been written for it.**

It is not optional. The paper's claim is *selective* degradation — if everything falls, that is damage rather than J-space ablation, and without an intact-side measurement the two are indistinguishable. Recorded here so it is not discovered at the moment Stage C is run.

Minimum credible version: wikitext top-1 agreement between clean and ablated passes. No external benchmark, no extra downloads, and it is what the paper reports.

---

## [2026-07-28] Session 13 — Stage B: workspace band derivation *(reconstructed 2026-07-29)*

**Phase:** 0 (Stage B) · **Reconstruction note:** written from
`results/raw/band_qwen3-8b/band_stats.json` and the session transcript one day
later. Contents are traceable to the committed artifact; the delay is recorded
because the compliance guide (§5, gap 5) flags unlogged sessions as an
evidentiary gap, and a reconstruction acknowledged as such is admissible where a
backfill presented as contemporaneous is not.

**Read-first sections re-read:** proposal §4.4, §4.7; guide Phase 0; AI guide §4.3
**Hardware:** Colab Pro, A100-80GB · **CU spent:** ~2

### What was run

`derive_band.py` — four J-lens-derived statistics across all 35 lens layers of
Qwen3-8B, on 20 WikiText passages via `jlens.examples.load_wikitext_prompts`.
`skip_first=4`, `max_seq_len=128`, seed 0, bfloat16, published lens (n=479).
Output: `results/raw/band_qwen3-8b/{band_stats.json,band_curves.png}`.

**Corpus choice:** WikiText, not the probe-swap prompts. Deriving the band on the
eval about to be ablated would contaminate it; WikiText also matches what the
published lens was fitted on.

### Result

| Statistic | Onset | Character |
|---|---|---|
| autocorrelation | L18 at half-peak | gradual from L15; peaks L24 |
| effective dimensionality | L19 (1.6×), then L22 (2.9×) | second jump sharp |
| top-k accuracy | L20 leaves floor | gradual |
| excess kurtosis | minimum L21 | flat-bottomed L15–22 |

End unambiguous: `topk_acc` crosses 0.5 at L31, accelerating hardest 31→34
(+0.12, +0.12, +0.15); kurtosis peaks exactly at L31; eff_dim begins its final
climb there. **Band L20–31**, 57%–89% of depth.

**Kurtosis does not match the paper's description.** Paper: "~0 through the first
third, rising from ~⅓ depth." Observed: 3.74 at L0, peaking 4.44 at L3, minimum
0.80 at L21, then rising to 1.94 at L31.

### Reading of the result

Three of four statistics converge on a start of L18–L22; the fourth is inverted
at early layers. The band-relevant half of kurtosis (minimum then rise) is
consistent with the other three, so the anomaly is an *additional* early feature
rather than a contradiction. Two untested explanations: early layers dominated by
token identity producing a peaked readout for a trivial reason, or the
final-layer lens recipe (§A.7 warns it "can sometimes increase the number of
noisy artifacts"). Reported either way.

Our band is 33% of the stack against the paper's 54%, entirely at the bottom —
narrower and starting later. Recorded as a comparison, not corrected for.

**Claude's `propose_band()` heuristic returned L0–31 and its start is wrong.** The
threshold logic takes the first layer exceeding 25% of peak kurtosis, which
assumes a rising curve; the early spike satisfies it at L0. Read manually
instead. The heuristic was not retuned to this data.

**All four statistics are lens-derived**, so a layer effect could be an artifact
of the method. The paper answers this with the ignition experiment, which uses no
lens; not implemented. Accepted as adequate for Phase 0, explicitly not adequate
for Phase 2.

### The three questions

1. **Which claim?** None — infrastructure. The band is a prerequisite for Control A.
2. **Any J-space property imported by assumption?** No. The band is measured, and
   the timing probe's earlier 12-layer guess is explicitly not a result.
3. **Defensible if the final result is null?** Yes — a null obtained over an
   unmeasured band would be uninterpretable.

### Deviations

None. Band derivation is a step absent from both the proposal and the execution
guide; adding it is a gap being filled, not a departure.

---

## [2026-07-28] DECISION — `prereg_controlA.md` signed

**Decision:** band L20–31 accepted; nesting shared-start accepted; band
sensitivity conditions accepted; §4 criteria accepted; **19 random draws** per
null accepted. Signed Stanley Zhou, 2026-07-28.

**Rationale for shared-start nesting:** the paper fixes k=10 and varies the layer
range, and its one documented sub-range is "the first third of the workspace
range" — the bottom of the band. Shared-start is the only nesting with a
counterpart in the paper, and Control A is a replication. A shared-*end* nesting
would plausibly show a stronger effect at narrow widths, and choosing it for that
reason would be selecting a design by its expected result.

**Rationale for 19 draws:** at 5 draws the strongest attainable statement under
exchangeability is p ≈ 0.167, which cannot carry proposal 4.8's load-bearing
control. 19 gives p ≤ 0.05 against each null, at ~15 units instead of ~5.

**Pre-registered prediction logged (§2.1):** under shared-start nesting, `light`
(L20–23) leaves eight downstream layers in which content may be re-established,
so it may show little effect even if the workspace is real. A flat
light→medium→heavy curve is therefore *weak* evidence against the workspace under
this nesting.

---

## [2026-07-29] Session 14 — Stage B2: readout verification

**Phase:** 0 (Stage B2, a step added mid-phase)
**Read-first sections re-read:** proposal §4.1, §4.2, §4.5 (in full); guide §2.1;
AI guide §3 (rows 1, 2, 8), §4.3
**Hardware:** Colab Pro, A100-80GB · **CU spent:** ~1

### Why this session exists

Control A ablates the top-10 J-lens directions and expects two-hop reasoning to
collapse. That inference requires those directions to *contain* the unspoken
intermediate. Nothing had checked it. Prompted by the user asking where J-space
actually sits in the pipeline — the honest answer was that it was being computed
in `build_cache`, used, and discarded unread.

### What was run

`verify_readout.py` — for each of the 90 probe-swap prompts, the rank of the
`intermediate` token in the lens readout and its workspace loading (cosine
similarity between residual stream and the intermediate's lens vector), at 24
layers spanning L0–L34. Best rank taken across positions, `skip_first=4`.

**Foil control:** every measurement repeated for a randomly chosen *other*
prompt's intermediate, seed 20260728. Without it a good rank could mean the lens
favours common words.

**Data property verified first:** all 90 intermediates are single words and
**none appears anywhere in its own prompt**, so this tests unspoken content
rather than an echo of the input.

Output: `results/raw/readout_qwen3-8b/{readout_records.json,readout_summary.json,readout_curves.png}`.

### Result

**Verdict: READOUT SURFACES INTERMEDIATES.**

| Layer | true top-10 | foil | gap | median rank | loading ratio |
|---|---|---|---|---|---|
| L8 | 3.3% | 0.0% | +3.3% | 955 | 2.19 |
| L10 | 21.1% | 1.1% | +20.0% | 72 | 2.59 |
| L12 | 34.4% | 1.1% | +33.3% | 57 | 2.96 |
| L18 | 38.9% | 1.1% | +37.8% | 19 | 2.15 |
| L20 (band start) | 36.7% | 2.2% | +34.4% | 20 | 1.82 |
| L26 | 67.8% | 3.3% | +64.4% | 5 | 2.16 |
| **L30** | **90.0%** | 8.9% | **+81.1%** | **1** | 2.70 |
| L31 (band end) | 85.6% | 8.9% | +76.7% | 2 | 2.83 |
| L34 | 82.2% | 10.0% | +72.2% | 2 | 2.57 |

Loading peaks 0.129 at L30 and collapses to 0.063 at L34. Foils remain 0.024–0.052
throughout. Mean gap: +15.0% below the band, +55.6% inside, +73.9% above.

### Reading of the result

At L30 the median rank of a token that never appears in the prompt is **1**. This
is a clean replication of the paper's readout claim on an open 8B model, and it
is a reportable positive result independent of whether ablation succeeds. Foils
near zero rule out the lens simply favouring frequent tokens.

**Two structural findings bear on the band.**

*Content begins around L10–12, ten layers below the pre-registered band start.*
Gap ≥20% from L10, ≥30% from L12. Ablating only L20–31 therefore leaves the
intermediate represented at L10–19 in 21–39% of prompts, available for
re-establishment downstream — the under-ablation false negative prereg §3
anticipated.

*This converges with the paper's own proportions.* The paper's band was 38%–92%
of depth; scaled to 36 layers that is **L13–L32**. The readout onset at L10–12 is
much closer to that than to the L20 our aggregate statistics gave. So two
independent lines — the paper's proportions and task-specific readout — point
lower than the four Stage B statistics do.

That disagreement has a plausible reading rather than being a contradiction:
kurtosis, autocorrelation, effective dimensionality and top-k accuracy measure
*general* processing structure, while this measures *task-specific* content.
There is no reason those must share a lower boundary. Recorded as a finding.

*The band end is independently confirmed.* Loading collapses immediately after
L31 — from a measure that played no part in deriving the band.

One caveat on interpretation: `best_rank` is the minimum across positions, so
these numbers say "the intermediate is strongly represented at *some* position at
this layer." That is the right question for scratchpad content, but it means the
persistence at L32–34 is not necessarily output convergence.

### The three questions

1. **Which claim does today's work support?** None of H1/H2/H3 — this is Phase 0
   instrument verification on a language model. It supports the *premise* Control
   A rests on, which is a different thing and must not be written up as evidence
   about the recommender domain.
2. **Did I import any property of J-space by assumption today?** No, and the
   temptation was live: a median rank of 1 is a striking number and invites
   treating the workspace interpretation as established. It is not. This shows
   the lens surfaces intermediates; it says nothing about whether that content is
   causally load-bearing, which is what Control A tests. Guide §2.1 terminology
   held — no readout result is described as "the workspace".
3. **Defensible if the final result is null?** Yes, and more than most. If Control
   A shows nothing, this session distinguishes "the readout never found the
   content" from "the content was there and ablating it did not matter." Without
   it those are indistinguishable (proposal §4.5).

### Deviations

Stage B2 is a step present in neither the proposal nor the execution guide.
Added because the premise Control A depends on was unverified. Its result
motivates Amendment 003.

### Next step

Sign Amendments 002 and 003; patch `STRENGTHS` in `run_control_a.py`; run
Control A. Still **not** G0 — G0 asks whether Control A passed, and it has not run.

---

## [2026-07-29] DECISION — Amendments 002 and 003

**Both committed before the first ablation on a real model.**

**002 — Control A primary eval.** The prereg specified "90 probe-swap prompts,
strict scoring", clean 58/90 = 64.4%. `strict` was defined by *generating*
`len(answer_tokens)` tokens; the harness performs a single forward pass and
cannot score a multi-token answer. 17 of 90 answers are multi-token. Primary
becomes **strict on the 73 single-token items, clean 50/73 = 68.5%** — exactly
`strict` on that subset, and consistent with the paper's own practice
(`capacity.json` filters to single-token entries; §A.9 states the J-lens
represents only single-token concepts). First-token on all 90 (63/90 = 70.0%)
reported as secondary.

Consequence carried through: n falls 90 → 73, binomial SE rises 5.3pp → 5.9pp,
so the 10pp dose-response threshold remains ~2 SE and is **not** changed. The
absolute degradation target moves from ≤32.2% to ≤34.3%.

**003 — additional band start.** Stage B2 found the unspoken intermediate
represented from L10–12, ten layers below the band start, and the paper's band
scaled to 36 layers is L13–32. `heavy-paper` (L13–31) **added**; nothing removed
and the primary band unchanged. Moving the primary band on the strength of
Stage B2 would be changing the target after seeing data — defensible, but adding
a condition tests the same question without moving anything.

Pre-registered prediction: if under-ablation is real, effect grows monotonically
as the start moves down — `heavy-late < heavy < heavy-early < heavy-paper`. A
flat curve means the band start is not load-bearing, which is the stronger
outcome. Grid: 201 → 241 conditions.

**Signed:** _______________ **Date:** ___________

---

## [2026-07-29] Session 15 — CONTROL A: the run

**Phase:** 0 (Stage C) · **Hardware:** Colab Pro, A100-80GB · **CU spent:** ~18
**Read-first sections re-read:** proposal §4.3, §4.4, §4.7, §4.8; guide Phase 0,
Phase 3 (3a–3d); `prereg_controlA.md` in full; AI guide §3 (rows 2, 3, 9, 12)

### What was run

`run_control_a.py`, 241 conditions: 6 strengths × (candidate + next_k + 19
random_lens + 19 random_iso) + clean baseline. Degrading side = 73 single-token
probe-swap items, strict scoring (Amendment 002). Intact side = 20 WikiText
passages on 21 of the 241 conditions. Qwen3-8B bfloat16, published lens (n=479,
final-layer recipe), k=10, `mode=subspace`, `exclude_clean_top=10`,
`skip_first=4`, base seed 20260728.

Outputs: `results/raw/controlA_qwen3-8b/` — one JSON per condition, plus
`_summary.json` and `dose_response.png`.

### Result

**Degrading side.** Clean 50/73 = 68.5%.

| Strength | Layers | Candidate | Rel. reduction | next_k | Beats all 38 randoms |
|---|---|---|---|---|---|
| light | L20–23 | 52.1% | 24% | 57.5% | yes |
| medium | L20–27 | 26.0% | 62% | 37.0% | yes |
| **heavy** | **L20–31** | **6.8%** (5/73) | **90%** | 13.7% | yes |
| heavy-early | L15–31 | 4.1% (3/73) | 94% | 11.0% | yes |
| heavy-late | L24–31 | 12.3% (9/73) | 82% | 21.9% | yes |
| heavy-paper | L13–31 | 4.1% (3/73) | 94% | 11.0% | yes |

All 38 random draws at every strength fell between 0.51 and 0.70 — no overlap
with any candidate anywhere. p ≤ 0.05 against **each** null separately
(random_lens and random_iso are different null distributions and are not
exchangeable, so no pooled p is reported).

**Intact side, WikiText.** heavy candidate top-1 match **0.577**; top-5 overlap
0.532; mean KL 3.04; cross-entropy 3.119 → 6.979 (**+3.86 nats**). Matched
randoms at the same layers: top-1 0.876–0.906, CE delta +0.11 to +0.97.

**Band-start dose-response.** Monotonic, spread 12%. heavy-late 82% < heavy 90%
< heavy-early 94% = heavy-paper 94%.

**Pre-registered criteria (prereg §4):**

| Criterion | Threshold | Observed | |
|---|---|---|---|
| Substantial degradation | ≥50% relative | 90% | PASS |
| Dose-response | heavy − light ≥10pp | 45.2pp | PASS |
| Beats every random draw | at every strength | all 38, all 6 | PASS |
| Intact side | WikiText top-1 ≥0.90 | 0.577 | **FAIL** |

`diagnose()` verdict: **DAMAGE — both sides degraded.**

### Reading of the result

The harness is demonstrably working, and this is worth stating before anything
else: clean returns top-1 match of exactly 1.000, and random ablations of
identical size at identical layers move the corpus by ~11% and reasoning by
3–7pp. The effect is not an artifact of the machinery.

The degrading side is not marginal. A 90% relative reduction with clean
separation from 38 matched draws at six band settings is about as strong as this
design can produce.

**The intact criterion failed and that is a real failure, not a technicality.**
+3.86 nats is a large disruption. The candidate is more selective than random —
selectivity ratio (reasoning drop ÷ corpus disruption) 1.46 against 0.29 for
random_lens and 0.69 for random_iso, so 2–5× — but 42% of argmax positions
changing is far from "essentially unaffected".

**Amendment 003's prediction held, with a qualification.** Monotone as predicted,
spread 12%. But `heavy-early` (L15) and `heavy-paper` (L13) are *identical* at
3/73 — the effect **saturates at L15**, so going below adds nothing. Under-
ablation was real but modest: the pre-registered L20–31 captured 90% of a 94%
ceiling. Reported as saturation rather than as unlimited monotonicity, because
the prediction as written did not anticipate a plateau.

**Prereg §2.1's prediction about `light` was directionally right and
quantitatively wrong.** `light` was the weakest strength as predicted, but at 24%
relative reduction it showed a clear effect and beat all 38 random draws.
Re-establishment across eight downstream layers attenuates but does not cancel.
Recorded because the prereg framed a flat `light` as the expected outcome.

**`next_k` is nearly as damaging as `topk` everywhere.** At heavy: 13.7% against
6.8%, both far below the ~63% random cloud. Ranks 11–20 of the lens carry
substantial causal weight. This is evidence **against compactness at k=10** in
this model, and it directly foreshadows H2 in Phase 3. It is not something this
phase set out to measure and it should not be over-read, but it is the single
most Phase-3-relevant thing this run produced.

**Recorded limitation of the run, not of the phenomenon.**
`DECISION_control_A.md` §4.5 specified the intact side as corpus top-1 match
**plus** public tasks (MMLU, SQuAD, sentiment, CoLA — "two is enough"). Only the
corpus half was built. The pre-registered criterion was therefore evaluated on
the most *sensitive* of the specified measures alone. This is an under-delivery
by the assistant, recorded as such.

### The three questions

1. **Which claim does today's work support?** None of H1/H2/H3 — Control A is
   instrument validation on a language model. It bears on whether a later null in
   the recommender domain would be diagnosable, not on the recommender domain.
2. **Did I import any property of J-space by assumption today?** No. The live
   risk was the opposite of the usual one: a 90% collapse is a striking number and
   invites declaring Control A a pass on three criteria while treating the fourth
   as a technicality. It is not a technicality — the intact side is what
   distinguishes workspace removal from damage, and it failed as pre-registered.
3. **Would this step still be defensible if the final result is null?** Yes. The
   effect magnitudes are recorded, which is what Phase 3 needs in order to know
   what a real positive effect looks like through this instrument.

### Deviations

Amendments 002 and 003, both committed before the run. No deviation from the
grid, thresholds, seeds, or criteria as signed.

### Next step

Run the coarse-output intact tasks specified in §4.5 and never built. They do not
change the pre-registered criterion; they establish whether its failure bounds a
narrow claim or a broad one.

---

## [2026-07-29] Session 16 — Control A: coarse-output intact tasks

**Phase:** 0 (Stage C, completing §4.5) · **Hardware:** A100-80GB · **CU spent:** ~8
**Read-first sections re-read:** `DECISION_control_A.md` §4.5; `prereg_controlA.md`
§4; AI guide §3 (rows 9, 12)

### What was run

`run_intact_tasks.py` — MMLU (150 items, 4-way, chance 25%) and SST-2 (150 items,
binary, chance 50%), scored by **constrained choice**: logits compared only at
the first token of each candidate answer, not argmax over the full 151,936-token
vocabulary. 18 conditions: clean, candidates at all six strengths, `heavy|next_k`,
and 5 random_lens + 5 random_iso at heavy. Seed 20260729.

**Headroom gate applied first.** MMLU clean 67.3% vs 25% chance; SST-2 92.7% vs
50%. Both passed and neither was excluded. Had either sat near chance it would
have been excluded automatically — a preserved score at chance is not evidence of
preservation.

### Result

| Measure | clean | candidate (heavy) | randoms | z | |
|---|---|---|---|---|---|
| probe-swap two-hop | 0.685 | 0.068 | 0.575–0.699 | — | collapse |
| WikiText top-1 | 1.000 | 0.577 | 0.876–0.906 | — | disrupted |
| **MMLU** | 0.673 | **0.687** | 0.653–0.687 | −0.25 | **intact** |
| SST-2 | 0.927 | 0.807 | 0.887–0.940 | +3.11 | reduced |

MMLU retention above chance 1.03; SST-2 0.72. `heavy|next_k`: MMLU 71.3%
(z = −0.75, noise), SST-2 82.0% (z = +2.81).

**Answer flip rate — the check that makes MMLU's intactness meaningful:**

| | candidate | random mean | ratio |
|---|---|---|---|
| MMLU | 0.140 | 0.033 | 4.3× |
| SST-2 | 0.173 | 0.049 | 3.6× |

**Unresolved anomaly.** On SST-2, `medium` (L20–27) is *worse* than `heavy`
(L20–31): 65.3% vs 80.7%, z = +6.17 vs +3.11. Ablating four additional layers
partly restores performance. Outside noise, non-monotonic, and unexplained.
Reported unresolved.

### Reading of the result

MMLU is completely unaffected — the candidate sits at the very top of the random
range. The paper named MMLU specifically among tasks essentially unaffected at
heavy ablation, and it replicates.

**The flip-rate diagnostic is what makes that claim admissible.** An unaffected
MMLU is equally consistent with the ablation not firing on those prompts. It
fired: answers flip 4.3× more often than under a matched random subspace, and net
accuracy does not move, so flips go both ways in equal measure. That is
"perturbs without destroying competence", not "nothing happened". Without this
check the MMLU result would have been uninterpretable in the same way a
near-1.0 corpus top-1 is.

**What replicates:** multi-hop collapses 90% relative while MMLU holds at 100%
and sentiment retains 72% of above-chance performance. Selectivity is
established; this is not general damage.

**What does not replicate:** the paper's claim that ablation leaves *fluent
language output* intact. WikiText CE +3.86 nats and 42% argmax flips describe a
substantially degraded language model. The combination is coherent and specific —
**the ablation reshapes the fine-grained output distribution while leaving
constrained-choice competence intact.** MMLU needs only the right ordering among
four tokens; fluent generation needs the whole distribution.

**The ordering caveat, stated before a reviewer states it.** These tasks were run
*after* the pre-registered criterion failed. They were named in the signed spec
§4.5 from the outset and only WikiText was built, so this completes an
under-delivery rather than shopping for a passing measure — and the pre-registered
criterion still failed and is reported as failed. But the sequence is visible in
the log and belongs in the paper explicitly. The runner writes the caveat into
its own output file so it travels with the data.

`next_k` again behaves like `topk` on every measure, reinforcing the session 15
finding against compactness at k=10.

### The three questions

1. **Which claim does today's work support?** None of H1/H2/H3. This bounds what
   Control A's failed criterion does and does not license.
2. **Did I import any property of J-space by assumption today?** No. The
   temptation here was specific and strong: MMLU intactness is exactly the result
   that would let the intact criterion be quietly reframed as passed. It is not
   passed. The pre-registered measure was WikiText top-1 ≥0.90 and it failed at
   0.577; these tasks are supplementary and are labelled as such in the data file
   itself, not only in prose.
3. **Would this step still be defensible if the final result is null?** Yes. The
   sensitive-vs-coarse gap is a fact about the ablation's shape that Phase 3 needs
   regardless of direction — and it establishes that a recommender intact side
   will need both kinds of measure, not one.

### Deviations

None from the pre-registration. This completes `DECISION_control_A.md` §4.5,
which was specified and under-implemented rather than amended.

### Next step

**G0.** Score per criterion, not as a single verdict — three pre-registered
criteria pass decisively, the fourth fails on the most sensitive measure while
the paper's own named tasks largely replicate. The call is the user's
(prereg §4, AI guide §2 row 12). Then Phase 1.

---
