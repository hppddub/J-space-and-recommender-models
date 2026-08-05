# Decision record — Phase 0 model change

**Supersedes:** `DECISION_phase0_model.md` (Qwen3.5-4B, recommended 2026-07-25)
**Drafted for sign-off; the decision is the user's** (AI collaboration guide §2)
**Date drafted:** 2026-07-28

---

## 1. Why this is being reopened

`DECISION_phase0_model.md` §6 listed four criteria for the Phase 0 model. Three were checked: the `LensModel` protocol is implementable, activations and the output projection are accessible, and it fits the compute budget. The fourth, two-hop headroom, was made into a measurable gate and run.

A fifth criterion — **an indexable, homogeneous residual stack** — was written into the *Phase 1* model criteria (`PHASE0_adapter_points.md` §4, requirement #1, added after reading the released code) and was never applied to the Phase 0 model. A Qwen was assumed to be a conventional transformer. That assumption was not checked, and it is wrong.

## 2. The finding

From `Qwen/Qwen3.5-4B`'s own config, read directly:

```
architectures            : Qwen3_5ForConditionalGeneration     (vision-language)
text_config.num_hidden_layers : 32
text_config.hidden_size       : 2560
full_attention_interval  : 4
mamba_ssm_dtype          : float32
mtp_num_hidden_layers    : 1
layer_types              : [linear_attention ×3, full_attention] × 8
```

**24 of 32 layers are linear-attention (SSM/Mamba-style).** Only 8 are full attention, at indices 3, 7, 11, 15, 19, 23, 27, 31 — a strict period-4 alternation. The checkpoint also carries a vision tower and a multi-token-prediction head.

Corroborating evidence already in the log, unrecognised at the time: the first headroom run emitted a `transformers` warning recommending `flash-linear-attention` and `causal-conv1d`.

## 3. Why this matters, stated as precisely as possible

It is **not** an argument that the J-lens fails on this architecture. The J-lens is a gradient method and applies to anything differentiable; Neuronpedia fitted a lens on this exact checkpoint successfully. Mechanically it works.

The objection is interpretive, and it lands on both remaining Phase 0 stages.

**Band derivation.** All four band statistics read structure across layer index and assume layers are comparable. A strict period-4 alternation of block types will very plausibly produce period-4 oscillation in those curves that is architectural in origin. Separating that from the sensory → workspace → motor transition the band is meant to capture is a research problem in its own right, and one this project has neither the time nor the mandate to take on.

**Control A.** Its sole purpose is to make a later null diagnosable by eliminating "broken instrument" as an explanation (proposal §4.4). A weak or absent effect on a hybrid SSM model would admit a third reading — instrument, model size, *or* the phenomenon not appearing in this architecture. Adding an explanation to the experiment whose function is elimination defeats it.

There is also a smaller point worth recording: the paper's finding is on a conventional transformer. A Phase 0 control run on an architecture unlike both the paper's model and the Phase 1 recommender candidates is a weaker control than one run on a conventional transformer.

## 4. Options considered

| Option | Assessment |
|---|---|
| **Stay with Qwen3.5-4B** | Headroom already measured. But the architecture confound propagates into the band, into Control A, and into every claim Control A bounds |
| **Switch to Qwen3-4B** | Conventional dense transformer, same size class, fits a T4 in fp16, pre-fitted lens in the same repo. Costs one repeated headroom run (~20 min, notebook exists) |
| Switch to Qwen3-8B or Llama-3.1-8B | Both conventional and both have pre-fitted lenses, but ~16 GB in fp16 does not fit a T4. Would require paid compute |
| Switch to Gemma-2-2B | Conventional and small, but a further step down in capability against a headroom result that already missed its threshold at 4B |

## 5. Decision

**Switch to Qwen3-4B**, conditional on the §7 verification passing.

**Sign-off:** ☐ accepted ☐ modified ☐ rejected — _______________ **Date:** ___________

## 6. The guard — this is the part that makes the switch honest

The switch is justified **on architectural grounds alone**, and that justification was reached without any knowledge of how Qwen3-4B scores on the headroom eval. To keep that true rather than merely asserted:

1. **The threshold does not move.** 70% on `exact`, exactly as committed in `THRESHOLD_headroom.md` on 2026-07-27.
2. **Amendment 001's rules do not move.** R1 numeral, R2 article, R3 compound-head, negator guard, no synonym list. Frozen as written.
3. **Both models' numbers are reported.** Qwen3.5-4B's 57/90 strict and 66/90 amended appear in the paper alongside Qwen3-4B's. The switch is not a way of discarding a result.
4. **This record is committed before the new run.** Its argument must stand on §2–§3 without reference to any Qwen3-4B score.

**If Qwen3-4B scores worse than Qwen3.5-4B, the switch still stands.** That outcome is anticipated here, in advance, precisely so it cannot later be treated as a reason to switch back. Reverting to Qwen3.5-4B *after* seeing that its number was higher would be selecting a model on its score while claiming an architectural rationale.

## 7. Verification required before the switch takes effect

Run against `Qwen/Qwen3-4B` and confirm all four:

- [ ] `layer_types` is absent, or uniform — no linear-attention or SSM blocks
- [ ] `architectures` is a plain causal LM, not `*ForConditionalGeneration` — no vision tower
- [ ] A pre-fitted lens exists at `qwen3-4b/jlens/Salesforce-wikitext/` and its `hf_model_name` is exactly `Qwen/Qwen3-4B`
- [ ] `d_model` in the lens matches the model config

If any fails, do not proceed on this record — reopen the decision.

## 8. Known open item, unchanged by this switch

The lens recipe. `config.yaml` shows `target_layer: null`, meaning the code default — the **final** layer — was used, against §A.7's penultimate. Every lens in the Neuronpedia repo was produced by the same script, so the Qwen3-4B lens will almost certainly carry the same deviation.

That decision remains open and is independent of the model choice: adopt the published lens with a documented recipe deviation, or fit our own with `target_layer=-2`. Note the published lens was fitted on a B200 with 179 GB at `dim_batch: 64`; a T4 has 16 GB, and fitting locally would run at roughly `d_model/dim_batch` backward passes per prompt with the graph retained.

## 9. What carries over, and what is repeated

**Unchanged — no work lost:**

- Proposal, execution guide, AI collaboration guide
- `DECISION_control_A.md` — the Control A specification is model-independent
- The ablation harness (`src/ablation/`), 15/15 tests passing — architecture-agnostic
- The band derivation module (`src/band/derive.py`) — architecture-agnostic
- `THRESHOLD_headroom.md` — threshold and primary metric unchanged
- Amendment 001 and `rescore.py` — rules frozen
- `headroom_check.py` and the Colab notebook — take `--model` as an argument
- All paper-reading artifacts (`PHASE0_adapter_points.md`, `PHASE0_paper_findings.md`, `PHASE0_appendices_A7_A9.md`)

**Repeated on the new model:**

- The headroom check — ~20 min, existing notebook, change one string
- The diagnostic generation pass and rescore
- The model-selection sign-off

**Retained as a result, not discarded:** Qwen3.5-4B's headroom numbers are a real measurement on a real model and are reported as such.
