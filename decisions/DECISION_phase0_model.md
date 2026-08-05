# Decision record — Phase 0 model selection (step 0.4)

**Drafted for sign-off; the decision is the user's** (AI collaboration guide §2).
**Date:** 2026-07-25

---

## 1. What the code actually supports

From `jlens/hf.py`, `_LAYOUTS`, read directly rather than recalled:

```
Layout("model")                                                  # Llama/Qwen/Mistral/Gemma/OLMo/StableLM
Layout("model.language_model") / Layout("language_model")         # multimodal wrappers
Layout("model", norm="final_layernorm")                           # Phi
Layout("transformer", layers="h", norm="ln_f", embed="wte")       # GPT-2
Layout("gpt_neox", norm="final_layer_norm", embed="embed_in",
       lm_head="embed_out")                                       # Pythia
```

Broad coverage, and it resolves the Phase 1 question early: **GPT-2 is supported**, so a GPTRec-style recommender inherits a working layout. That claim was made in `PHASE0_adapter_points.md` from a partial read and is now confirmed.

`walkthrough.ipynb` references exactly two models — `Qwen/Qwen3.5-4B` and `Qwen/Qwen3.6-27B` — with pre-fitted lenses under `neuronpedia/jacobian-lens`.

## 2. Candidates

| Model | Fits a T4 (16 GB)? | Pre-fitted lens | Verdict |
|---|---|---|---|
| **Qwen3.5-4B** | Yes — ~8 GB fp16, comfortable headroom | Yes | **Recommended** |
| Qwen3.6-27B | No — ~54 GB fp16, exceeds even A100-40GB | Yes | Out on compute |
| Something else via HF | Depends | No — fit your own | Fallback only |

## 3. Decision

**Qwen3.5-4B, gated on the headroom pre-check.**

**Sign-off:** ☐ accepted ☐ modified ☐ rejected — _______________

**Rationale.** It is the walkthrough's own model, so the path is known-good and least likely to fail for reasons unrelated to the science — which matters disproportionately for an instrument-validation phase, where an ambiguous failure is the expensive outcome. A pre-fitted lens exists, removing fitting from the critical path for the first run. And fitting your own is now cheap anyway (§A.7: ten prompts beat the baselines), so the pre-fitted lens is a convenience rather than a dependency.

**The one real risk is unchanged and now measurable.** AI guide §1.4 worried that a small model may not do enough multi-step reasoning to have anything to degrade, producing a failed Control A caused by model selection rather than by a broken instrument. 4B sits squarely in that zone of doubt. `DECISION_control_A.md` §4.6 converts the worry into a gate.

## 4. Run this first — it needs no lens and no harness

**Measure unablated greedy next-token accuracy on the 90 `probe-swap.json` prompts, scored against the `answer` field.**

This is the cheapest decisive step available: base model only, no lens fitting, no ablation, no harness. It takes one forward pass per prompt and it decides the model.

**Record the headroom threshold before looking at the number.** The paper's ablation result depends on the unablated model being near ceiling; if accuracy is low, there is nothing for ablation to remove and Control A cannot distinguish a broken instrument from a model that cannot do the task.

**If headroom fails, step up, not down.** Guide Phase 0's failure mode says "downscale the LLM before downscaling the validation," but AI guide §1.4 adds the floor: below some size Control A stops being informative at all. A pass obtained from a model that cannot reason is worse than an honest partial. Options in order: a larger Qwen (fit your own lens — cheap), or accept a documented partial Control A and let it bound every downstream claim.

## 5. One thing to check about the pre-fitted lens

**Was `neuronpedia/jacobian-lens` fitted at the final or the penultimate layer?**

The released code defaults to the final layer (`target = n_layers - 1`); §A.7 says the paper's default is penultimate. Verified empirically: the two recipes produce J matrices differing by 2.4% of max magnitude. If the published lens was fitted with the code default, **using it silently locks Control A into the non-paper recipe** — and per §A.7 the noisier one.

If the fitting configuration is not documented alongside the artifact, fit your own with `target_layer=-2`. At ten to a hundred prompts this costs almost nothing, and it removes an uncontrolled variable from the one experiment whose entire purpose is to be uncontaminated.

## 6. Criteria this satisfies

| Criterion | Source | Status |
|---|---|---|
| `LensModel` protocol implementable | guide Phase 1a | Yes — `HFLensModel` + `Layout("model")` |
| Activations and output projection accessible | guide Phase 1a | Yes — `lm_head.weight` for `W_U` |
| Fits compute with room for the sweep | AI guide §1.4 | Yes, and the constraint relaxed once fitting turned out near-free |
| Measurable two-hop headroom | `DECISION_control_A.md` §4.6 | **Unknown — this is the gate** |
