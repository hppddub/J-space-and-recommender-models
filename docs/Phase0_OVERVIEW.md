# Phase 0 — code overview

Everything built for Phase 0 (toolchain validation / Control A), with what each
piece does, why it exists, and which lab log session produced it.

**Companion:** `docs/Phase0_LAB_LOG_consolidated.md` — sessions 02–16.
**Status:** Phase 0 complete pending the **G0** decision.

---

## Layout

```
rspace_phase0/
  src/ablation/     the ablation machinery — reused unchanged in Phase 3
  src/band/         instrument characterisation (band, readout)
  tests/            53 tests, CPU only, no model downloads
  scripts/          runnable entry points
  notebooks/        Colab wrappers; each embeds its scripts, nothing to upload
  docs/             decisions, pre-registrations, paper-reading artifacts
```

**Import convention.** Nothing is pip-installed. `PYTHONPATH` carries
`jacobian-lens` and the repo root — an editable install of `jlens` failed in
Colab and, more importantly, `!python` subprocesses do not inherit `sys.path`
edits made in a notebook kernel. `os.environ["PYTHONPATH"]` *is* inherited.
(session 13 preamble)

---

## `src/ablation/` — the harness

Built to Phase 3 requirements from the first line, because `EXECUTION_GUIDE` §3a
requires Control B and the Phase 3 sweep to run through the **identical** code
path. A Phase 0 throwaway would have been built twice.

| File | What it does | Why it exists | Session |
|---|---|---|---|
| `directions.py` | Builds J-lens vectors (`W_U J_l` rows), selects top-k / next-k / random directions, orthonormalises, projects out | Separating *selection* from *projection* is what makes proposal 4.8's matched controls cheap: same projection, different selector | 08 |
| `harness.py` | Two-pass ablation — clean pass, then ablated pass — plus `build_cache` and `prepare_lens` | Two passes are forced by the confound guard: you must know the clean output before choosing what to ablate | 08, 12, 14 |
| `sweep.py` | Resumable condition sweep; config snapshot + git hash per run | Colab sessions die. `build_conditions` emits matched controls *alongside* every candidate so a result without a baseline is structurally hard to produce | 08 |
| `intact.py` | Intact side — WikiText top-1 match, top-5 overlap, KL, cross-entropy; `diagnose()` | If everything degrades, that is damage, not workspace ablation. `diagnose()` exists to stop a no-op ablation being written up as a preserved intact side | 15 |
| `tasks.py` | Coarse-output tasks (MMLU, SST-2) by constrained-choice scoring, with a headroom gate | WikiText next-token is the most *sensitive* intact measure. A 4-way choice only flips if four specific tokens reorder — which is why the paper's tasks survived | 16 |

### Three things in here that are easy to lose

**Clean-top-k exclusion** (`directions.clean_top_mask`). Never set it to 0. Without
it, ablation suppresses whatever the model was about to say and H1 gets
"confirmed" by an artifact. The only identified route to a **false positive**.

**`prepare_lens` moves device only, never dtype.** `JacobianLens.__init__` forces
float32 and `apply()` casts residuals to match. An earlier version cast the
Jacobians to the model's dtype and broke Stage B outright. Activations taken
straight from `ActivationRecorder` are in the *model's* dtype and must be
`.float()`-ed before `transport` — that is why those casts are in `build_cache`.

**Effective rank is reported.** k J-lens vectors may span fewer than k dimensions;
they are overcomplete and non-orthogonal. "We ablated k directions" is false if
the span was smaller.

---

## `src/band/` — instrument characterisation

| File | What it does | Why it exists | Session |
|---|---|---|---|
| `derive.py` | Four per-layer statistics — excess kurtosis, top-k accuracy vs the model's own argmax, top-1 autocorrelation against a shuffled null, participation ratio of `W_U J_l` — plus a first-pass band proposal | The paper's band is Sonnet 4.5's. Every experiment reports over the band and **nothing in the released code computes one**. This step appears in neither the proposal nor the execution guide | 13 |
| `readout.py` | Rank and workspace loading of the *unspoken intermediate*, with a foil control | Control A assumes the top-k directions contain the intermediate. Nothing had checked. Foils are the actual evidence — a good rank alone could just mean the lens likes common words | 14 |

**`propose_band()` was wrong on real data and was not retuned.** Its threshold
logic assumes a rising kurtosis curve; Qwen3-8B's is U-shaped with an early
spike, so it returned L0–31. The band was read from the curves instead. Fixing
the heuristic *to this data* would have been tuning a measurement to its result.

**All four statistics are lens-derived**, so a layer effect could be an artifact
of the method. The paper answers this with the ignition experiment, which uses no
lens — **not implemented**. Adequate for Phase 0; explicitly **not adequate for
Phase 2** in the recommender domain.

---

## `scripts/` — entry points, in execution order

| # | Script | Purpose | Session | Key result |
|---|---|---|---|---|
| 1 | `step0_verify_model.py` | Four architecture checks on a candidate model and its published lens | 11 | Caught Qwen3.5-4B as a **hybrid SSM** — 24 of 32 layers linear-attention |
| 2 | `headroom_check.py` | Unablated two-hop accuracy — is there room to fall? | 10 | Qwen3.5-4B 63.3%, Qwen3-4B 55.6%, Qwen3-8B 64.4% |
| 3 | `rescore.py` | Re-scores saved generations under Amendment 001's three rules | 10 | Frozen after session 10; unchanged across all three models |
| 4 | `derive_band.py` | Stage B — the workspace band | 13 | **L20–31** (57–89% of depth) |
| 5 | `verify_readout.py` | Stage B2 — does the readout surface the intermediate? | 14 | **Median rank 1 at L30**, 90% top-10 vs 8.9% foils |
| 6 | `run_control_a.py` | Control A — 241 conditions, degrading + intact | 15 | 3/4 criteria pass; intact **fails** at 0.577 |
| 7 | `run_intact_tasks.py` | Coarse-output intact tasks | 16 | MMLU **intact**; selectivity established |

`headroom_check.py` is superseded by the consolidated version embedded in
`notebooks/headroom_qwen3-4b.ipynb`, which runs the check and diagnostic in one
process. Kept because it produced the Qwen3.5-4B results on record.

---

## `notebooks/` — Colab wrappers

Each embeds its scripts via `%%writefile`. **Nothing to upload alongside.** Your
repo remains the source of truth; if you change a module, re-copy.

| Notebook | Stage | Session |
|---|---|---|
| `headroom_qwen3-4b.ipynb` | Headroom, single process (fixes the session 09 OOM) | 11 |
| `pro_session_qwen3-8b.ipynb` | Qwen3-8B headroom + Control A cost probe | 12 |
| `stageA_inspect_lens.ipynb` | Published lens provenance and recipe | 12 |
| `stageB_derive_band.ipynb` | Band derivation + four curves | 13 |
| `stageB2_verify_readout.ipynb` | Readout verification + foil curves | 14 |
| `controlA_run.ipynb` | Control A, 241 conditions, ~70 min | 15 |
| `controlA_intact_tasks.ipynb` | MMLU + SST-2 | 16 |

**Keep everything in one process.** Session 09 aborted on CUDA OOM because a
notebook-kernel model load and a `!python` subprocess load coexisted on one T4.

---

## `tests/` — 53 passing, 1 skipped

CPU only, no downloads. `python -m pytest tests/ -q`

| File | Covers |
|---|---|
| `test_ablation.py` | Projection, rank deficiency, seeding, resumability, cache equivalence, dtype invariants |
| `test_intact.py` | Metric correctness, the selectivity conflation guard |
| `test_readout.py` | Rank/loading measurement, the foil-gap guard |
| `test_tasks.py` | Token collision, headroom gate, retention arithmetic |

The skip is GPU-only: CPU `layer_norm` rejects bf16 parameters, so the
end-to-end bf16 path is verified by invariant plus reasoning, **not** by an
end-to-end CPU run.

### Four tests that exist to catch silent failure

- `test_guard_actually_changes_what_gets_selected` — asserts the clean-top-k
  guard is not a no-op on the input. A control that cannot fail is not a control.
- `test_selective_requires_both_sides_not_just_degradation` — regression. An
  earlier `diagnose()` labelled heavy corpus disruption "SELECTIVE" as long as
  reasoning had dropped: the exact conflation the module exists to prevent.
- `test_no_gap_over_foils_is_flagged_even_when_topk_looks_good` — a high top-10
  rate with no foil gap is the lens favouring common words, not a readout.
- `test_retention_above_chance_is_stricter_than_raw` — a destroyed 4-way model
  scores 25%, not 0%. Raw retention would call that 40% preserved.

---

## Phase 0 in one table

| Stage | Question | Answer | Session |
|---|---|---|---|
| Step 0–1b | What did Anthropic actually release? | Readout only; the ablation protocol is in the **paper**, not the code | 02–06 |
| Step 0.4 | Which model? | Qwen3-8B, after Qwen3.5-4B was found to be a hybrid | 10–12 |
| Headroom | Is there room to fall? | 64.4% — three models all **miss** 70%; scale buys 1.1pp | 10–12 |
| Stage B | Where is the band? | L20–31; kurtosis anomaly recorded | 13 |
| Stage B2 | Does the readout find the intermediate? | Yes — median rank **1** at L30 | 14 |
| Control A | Does ablation collapse reasoning? | Yes — 90% relative, beating all 38 random draws at six band settings | 15 |
| Intact | Is it selective? | MMLU **intact**; WikiText **not** — criterion failed | 15–16 |
| **G0** | Trust the instrument? | **open** | — |

---

## Carried into Phase 3

- **The harness is the Phase 3 harness.** Control B runs this identical path.
- **next-k is nearly as damaging as top-k** (13.7% vs 6.8% at heavy, both far
  below the ~63% random cloud). Ranks 11–20 carry heavy causal load — direct
  evidence against compactness at k=10, and a reason to take the H2 sweep
  seriously rather than assume a small k. Belongs in `prereg_phase3.md`.
- **Measure both a sensitive and a coarse intact side.** They disagreed here, and
  either alone would have misled.
- **The band statistics do not port.** Only kurtosis and effective dimensionality
  transfer without reinterpretation; top-k accuracy and autocorrelation presuppose
  a token stream with language-like local redundancy. Phase 2 needs a
  readout-independent check (the paper's ignition experiment) that is not built.
- **Compute is not the constraint.** Control A cost ~18 units. Phase 1 models are
  two orders of magnitude smaller.

## Known gaps

1. **G0 not taken.**
2. **Ignition experiment not implemented** — the paper's readout-independent band
   check. Required for Phase 2, not for Phase 0.
3. **SST-2 non-monotonicity unexplained** — `medium` hurts it more than `heavy`
   (z = 6.17 vs 3.11). Outside noise. Reported unresolved.
4. **Lens recipe deviation.** Every published lens in the Neuronpedia repo used
   `target_layer: null` (final layer); §A.7 says the paper used penultimate.
   Measured difference 2.4% of max magnitude. Documented, not corrected.
5. **Coarse intact tasks ran after the pre-registered criterion failed.** They
   were named in `DECISION_control_A.md` §4.5 from the start, so this completes an
   under-delivery rather than shopping for a passing measure — but the ordering is
   what a reviewer will look at, and the paper should say so first.
