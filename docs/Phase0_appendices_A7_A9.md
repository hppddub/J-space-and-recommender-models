# Phase 0 Step 1c — Appendices §A.9 and §A.7 (resolved from primary text)

**Source:** uploaded PDF, 141 pages, browser-rendered from the Transformer Circuits version. Text layer clean, extracted with `pdftotext -layout`.
**Resolves:** the two gaps recorded as unretrievable in Session 05.
**Amends:** `PHASE0_adapter_points.md` §4a (single-token constraint) and adapter point #6 (`skip_first`). Both risk ratings change.

---

## 1. §A.9 — multi-token concepts. **This reopens the Phase 1 model constraint.**

### 1.1 What the template lens actually is

Not a variant of the J-lens. A different construction that **never touches the vocabulary or the unembedding.**

For each word *w* in a predefined vocabulary (~12,700 common words):

1. Generate short passages written so that *w* is the natural continuation, ending just before *w* would appear — varying topic, frame, and register, never using *w* itself.
2. Run the model over them; average the residual stream at the final position → a per-word mean activation `μ_w(ℓ)` at each layer.
3. Center against the mean of all other words' vectors and whiten:

   `t_w(ℓ) = (Σ_ℓ + λI)⁻¹ (μ_w(ℓ) − μ(ℓ))`

This is the linear discriminant direction separating contexts where the model is about to say *w* from those where it isn't. Templates are then used **exactly as J-lens vectors are, excluding the unembedding step**: decode by projecting activations onto templates at the same layer; steer by adding or subtracting; the lens-coordinate swap of §2.5 works unchanged.

The paper motivates the correspondence via Stein's lemma — for Gaussian *x* and differentiable *g*, `E[∇g(x)] = Σ⁻¹E[g(x)(x−μ)]`, whose left side approximates what the J-lens computes for single-token *w* and whose right side is the template. It states plainly that the assumptions don't hold exactly: activations are non-Gaussian and *g* depends on more than *x*.

### 1.2 Performance

On multi-hop prompts with intermediates of one to four tokens (n=126 readout, n=112 swap pairs, 53 single-token / 59 multi-token):

- **J-lens** decodes single-token intermediates well and **degrades sharply as the intermediate lengthens.** Averaging J-lens scores over the word's constituent tokens does not help. Swap performance drops significantly for multi-token concepts.
- **Template lens** holds roughly constant across all lengths, for both readout and swap.
- On single-token concepts the two are comparable — template slightly worse on readouts, modestly better on swaps.

### 1.3 Why this matters here, and it is not a small point

The Phase 1 criterion added in Session 03 — *item-to-token cardinality must be 1* — was derived from the J-lens's vocabulary restriction. **The template lens dissolves that restriction**, and its precondition maps onto the recommender domain unusually well:

| Template lens needs | Recommender supplies |
|---|---|
| An enumerable concept vocabulary | The item catalogue, by construction |
| Contexts where concept *w* is the natural continuation, ending just before it | **Every real interaction sequence ending just before item *i*.** Naturally varied across users and contexts |
| Residual-stream access at a chosen layer | Same requirement as the J-lens |
| No vocabulary/unembedding involvement | Semantic-ID multi-token encoding becomes irrelevant |

The step that is expensive and awkward in the language domain — having a model write hundreds of passages per word — is **free in the recommender domain**, because the dataset already contains exactly those sequences. This is the one place so far where the port is *easier* than the original rather than harder.

### 1.4 The counterweight, which is serious

The paper is direct that the template lens **is not a pure extension of the J-lens** — it "has some properties more similar to the tuned lens, and inherits some related pathologies." Documented shortcomings:

1. **It sometimes "skips to the answer" prematurely in early layers** rather than surfacing intermediates — the same pathology the paper identifies in the tuned lens, and attributes to both being fitted linear predictors of output rather than causal measurements.
2. Final-layer readouts are less reliable than the J-lens's. When the next sampled word is in the template vocabulary, it appears in the top ten only **67%** of the time.
3. A small set of words appear spuriously often; mitigated by filtering them out, which the paper calls effective but unprincipled.
4. Vocabulary must be enumerated in advance.
5. More expensive per concept: a few hundred forward passes per word, versus one set of backward passes per layer for the whole J-lens.

**Shortcoming 1 is the one that bears on this project's central risk.** Proposal §4.1 defines the construct under test as a subspace with *disproportionate causal influence*. The template lens is correlational by construction. A readout that skips to the predicted next item, rather than surfacing an intermediate, would produce directions that look causally important but are partly just the output — a **false-positive route for H1**, and the second one identified so far after the clean-top-k guard.

### 1.5 Oracle lens — out of scope, recorded for completeness

Removes the enumerate-in-advance requirement by training a reconstructor (subject model fine-tuned to map a phrase to the preceding residual-stream activation, cosine loss in the whitened template metric) and then an RL-trained oracle proposing phrases whose template vectors sparsely reconstruct the activation. Requires fine-tuning two auxiliary models. **Substantially more expensive than either other lens, and not remotely feasible on this project's compute.** Do not consider it.

### 1.6 Consequence for Phase 1

The item-to-token cardinality criterion moves from **hard constraint** to **conditional**:

- If a candidate architecture has one item = one vocabulary token → J-lens applies directly. Preferred, because the instrument is causal.
- If items span multiple semantic-ID tokens → not disqualifying any more, but the fallback is a **correlational** instrument that carries a documented false-positive pathology, and implementing it means building the template pipeline on top of the ablation harness.

Recommendation unchanged in direction, weaker in force: still prefer one-item-one-token, but for instrument quality rather than feasibility.

---

## 2. §A.7 — methodological details. **Adapter point #6 downgrades.**

### 2.1 Position masking was tested, and barely matters

Under *Data → Distribution*: they experimented with masking which positions contribute to the within-prompt average, including **excluding the first several tokens to let the model "burn in,"** and excluding positions whose next token is non-alphanumeric. **"None of these yielded a meaningful improvement over the default."**

Separately, under aggregation: within a prompt they average over positions but consider excluding outlier-norm positions "as well as the first several positions of each sequence, to reduce early context artifacts."

**Consequence.** `SKIP_FIRST_N_POSITIONS = 16` is a low-sensitivity knob in the language domain — the exclusion doesn't *help*. That is not the same as showing it doesn't *hurt* when it removes most of the data, which is what it would do on 20–50-length interaction sequences. But it removes the reason to preserve it: since skipping buys nothing measurable, **set `skip_first` low or zero for the recommender and record the choice**, rather than treating it as a parameter needing re-derivation.

Adapter point #6 risk: **highest → moderate.** Resolve by choosing low, not by sweeping.

### 2.2 Ten prompts, not a thousand

Under *Data → Amount*: the default uses 1000 sequences of 128 tokens, swept from 1 to 1000. **"J-lens beats the logit lens and tuned lens baselines with as few as 10 prompts, with modest improvements coming from additional data."**

Consistent with the README's "quality saturates quickly; ~100 prompts is usable," but far stronger. Lens fitting is close to free. **The AI guide §1.4 compute budget, which treated fitting as a cost driver, is wrong in the conservative direction** — the expensive part is the ablation evals, not the lens.

### 2.3 A possible code/paper discrepancy worth checking

§A.7 states the default lens computes `∂z_t′/∂h_ℓ,t` with **z taken at the penultimate layer**, because "including the last layer can sometimes increase the number of noisy artifacts in lens-readouts" — the final block being specialised for calibrating next-token predictions and carrying less semantic content.

The released `jlens/fitting.py` module docstring gives `J_l = E[∂h_final/∂h_l]`. **Check whether the released default targets the final or penultimate layer before running Phase 0.** If it targets final, the code default differs from the paper default and Control A should use the paper's.

### 2.4 Other recipe findings

Variants tested: injection at all positions at the final layer; the same at second-to-last; the same with stop-grads on QK; future-positions-only; present-position-only — each with mean and median aggregation. Results are "fairly consistent among these design choices," with mean aggregation at penultimate a small improvement for extracting intermediates, and **QK stop-grads able to increase the causal effect.**

Note also that the paper maintains a standard **causal-ablation eval** used to compare recipes (Figure 58). Worth mirroring: it is the natural place to report Control A's recipe sensitivity if time allows.

---

## 3. One thing *not* found, recorded so it isn't assumed later

Secondary sources reported an invited external review and an independent partial replication by a DeepMind team. **The paper text does not state this.** Neel Nanda appears once, in a long acknowledgments list alongside many others, and otherwise only in the bibliography.

**Proposal §9 honesty item 1 — "not yet independently replicated even within its original domain" — therefore stands unamended.** Do not weaken it on secondary-source evidence. If an external review exists as a separate document, cite that document or nothing.
