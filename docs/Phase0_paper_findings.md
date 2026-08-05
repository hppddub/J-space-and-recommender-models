# Phase 0 Step 1b — Paper findings against the three open items

**Paper:** Gurnee, Sofroniew, … Lindsey (2026), *Verbalizable Representations Form a Global Workspace in Language Models*, Transformer Circuits Thread, 6 July 2026. arXiv:2607.15495v1 (16 July 2026).
**Companion to:** `PHASE0_adapter_points.md` (which this document corrects in one place — see §1).
**Sections read:** Methods (all), §The J-space acts as a Global Workspace (all), §The J-space's structure supports its function (all). **Not read:** appendices, alignment-auditing sections, counterfactual reflection training.

---

## 0. Headline

All three open items are resolved, and one of them reverses the recommendation in `PHASE0_adapter_points.md` §2b. **The ablation experiment is fully specified in the paper** — parameters, confound guard, layer bands, and a random-direction control. The gap identified in Session 03 was a gap in the *release*, not in the *method*. Control A is implementable to spec.

---

## 1. Item 1 — does `probe-swap` use a J-lens direction or a separate linear probe?

**Both, in a specific two-stage structure**, and the answer matters more than the question anticipated.

The probe is fit **without the J-lens**: for each two-hop prompt, the mean residual-stream activation over a set of prompts that imply the same intermediate through different surface cues and ask different questions about it, minus the mean over all intermediates. That probe is then **decomposed against the J-lens dictionary by gradient pursuit**, splitting it into a J-space component (a non-negative combination of k=25 J-lens vectors, typically ~10–15% of the probe's variance) and a J-orthogonal remainder carrying the rest. The swap is then run three ways: along the full probe, along the J-space component only, and along the non-J-space component only.

Results over n=90 two-hop prompts (Figure 16):

| Swap along | Target answer at top-1 |
|---|---|
| Probe's J-space component | 61% |
| Raw J-lens token vectors | 60% |
| Probe's non-J-space component | 28% |
| Non-J-space component, J-space coordinates clamped to clean-pass values | 6% |

So `probe-swap` is not a distractor — it is the paper's **privilege test**: most of the probe's variance lies outside the J-space, but the causal effect concentrates in the J-space component, and the residual effect is itself routed through the J-space.

**Consequence for the project, and it is not the one Session 03 expected.** The design worth importing here is not the prompt set but the *control structure*. Proposal §4.8 specifies a matched-size **random** subspace as the ablation baseline. The paper's control is stronger and complementary: **the complementary component of the same representation, rescaled to matched magnitude, plus a clamp on the other component to test for routing.** Both belong in Phase 3. The random baseline tests "is this subspace special among subspaces of this size"; the complementary-component baseline tests "is this subspace special within this representation." A candidate R-space that beats random draws but not its own complement has not earned H1.

---

## 2. Item 2 — how is the workspace band derived?

**Five converging measurements, four of which are J-lens-derived and therefore circular if ported naively.** The paper is explicit about that risk and answers it with a fifth that is not.

Layer indices below are on the paper's reindexed 0–100 scale (25 evenly spaced layers), Sonnet 4.5.

*Block structure.* Centered kernel alignment (CKA) between layers, over the matrices of pairwise similarities among J-lens vectors, gives a three-block structure: an early block (~first third), a long middle block, a small late block. The paper labels these **sensory / workspace / motor**.

*Four statistics, all converging on ~L38 → ~L92:*

| Signal | Behaviour | Marks |
|---|---|---|
| Top-k accuracy of J-lens at predicting the model's actual next token | ~0 early, ticks up at workspace start, rises slowly, jumps steeply in final layers | the **end** (motor onset) |
| Excess kurtosis of the J-lens readout logit distribution | ~0 through first third, rises from ~⅓ depth, falls in last few layers | the **start** |
| Autocorrelation of top-1 lens token across nearby positions, vs a position-shuffled null | near null early, rises sharply, peaks mid-band, falls late | persistence of abstract content |
| Effective linear dimensionality of `W_U J_ℓ` | small early (J-space collapses to a small subspace), rises sharply at onset, rises again at the motor transition | fan-out across the residual stream |

*The non-circular check — and the reason `ignition.json` matters.* The paper states plainly that because these metrics derive from the J-lens, the layer effects could be artifacts of the method rather than facts about the model — in particular, the absence of early content could mean the lens is degenerate at those depths rather than that nothing is there. The ignition experiment is the answer, and it uses **no J-lens at all**: replace a concept token's input embedding with a mixture `(1-α)·e_B + α·e_A`, sweep α, and measure where the activation sits along the line connecting that trial's pure-B to pure-A activation at the same position and layer. Early layers track the mixture smoothly and roughly proportionally; from ~L38 the activation instead sits near one endpoint or the other, switching sharply at a threshold α. That the onset layer identified without the lens matches the onset identified with it is what licenses the band.

**Consequences for the port, and this is the largest structural finding of the session.**

The band is a **prerequisite**, not a result: every released experiment reports over it, and Phase 3 cannot ablate "across a band of layers" without one. Deriving it for the recommender is a step that does not currently exist anywhere in the proposal or guide's phase structure. It belongs at the end of Phase 2.

Worse, three of the four statistics do not port cleanly. Next-token accuracy and autocorrelation both presuppose a token stream with the kind of local redundancy language has; an interaction sequence may have neither. Kurtosis and effective dimensionality are the two that transfer without reinterpretation.

Best news of the session: **the ignition method ports well.** Mixing two item embeddings in a carrier interaction sequence and sweeping α is directly constructible in a recommender, and `ignition.json`'s structure (40 carrier templates, 66 country pairs, plus idiom and scrambled controls) is a usable template. It would give a band derivation that is independent of the readout — which, given proposal §4.5's "readout too weak" branch, is worth more here than it was in the original paper.

---

## 3. Item 3 — which experiment produces the ablation collapse, and what exactly was ablated?

**Section: "J-space ablation leaves most capabilities intact while impairing internal reasoning."** Procedure, in full:

- At each token position, across a band of layers, identify the **k = 10** most strongly activated J-lens vectors and **zero out the residual stream's projection onto each**, then continue the forward pass.
- **Confound guard:** do not ablate any tokens that appear in the top-10 tokens of a clean forward pass — so the manipulation targets the J-space's role in internal reasoning rather than in report.
- Three strengths — **light, medium, heavy — differ in the range of layers** over which the ablation is applied, not in k.
- **A random-direction control at the medium layer range is reported alongside** (Figure 22).

Effect magnitudes:

- Controlled multi-hop reasoning eval (the 50-prompt two-hop set): unablated is near-ceiling; ablation significantly reduces accuracy, **heavy ablation to near zero**.
- Pretraining-like corpus: ablation perturbs next-token prediction substantially less. Reported as top-1 match with the unablated model.
- Fourteen-task battery. Essentially unaffected even under heavy ablation: MMLU, odd-one-out, SQuAD extractive QA, sentiment, CoLA. Degraded below unablated Haiku 4.5: Caesar-cipher decoding, analogy completion, summarization, TriviaQA, multi-hop reasoning, translation, sonnet writing.
- **GSM8K with explicit chain-of-thought is substantially more robust than the same problems answered directly** — read as the model externalizing onto the page what it would otherwise carry in the J-space.

### 3a. This reverses `PHASE0_adapter_points.md` §2b

That document recommended option (a) — adopt `probe-swap` as Control A — on the grounds that option (b), implementing ablation from the paper, would leave Control A "a reimplementation validated against nothing." **That reasoning was wrong, and the correction should be recorded rather than the document silently edited.** The ablation is specified to the level of k, the projection operation, the layer-band parameterisation, the clean-top-10 exclusion, and the control. A reimplementation is validated against the paper's reported magnitudes on named public benchmarks.

**Revised recommendation: option (b), with `probe-swap` retained as a secondary check.** Ablation is what proposal §4.4 actually names, what Phase 3 actually needs, and what the guide's §3a Control B runs through the same harness. Building the harness for a swap in Phase 0 and then a different harness for ablation in Phase 3 would defeat the point of Control A.

Open sub-item: the multi-hop *reasoning* set used for the ablation eval is 50 prompts, and no released file has n=50 (`probe-swap.json` is 90; `lens-eval-multihop.json` is 93 and is a readout-quality eval, not a causal one). The exact ablation eval set may not be released. Confirm before assuming a like-for-like replication.

### 3b. Three findings that change the downstream design

**The clean-top-10 exclusion is load-bearing and has a direct recommender analogue.** Without it, ablating the top-k directions at a position trivially suppresses whatever the model was about to output, and the resulting accuracy drop measures nothing. In a generative recommender the equivalent is: do not ablate directions corresponding to items already in the top-k of the clean next-item distribution. **Omitting this in Phase 3 would produce a large, meaningless H1 "confirmation"** — a positive result that is an artifact. This belongs in `prereg_phase3.md` explicitly.

**The paper fixed k and swept the layer band; the proposal sweeps k.** Ablation used k=10 throughout, with the three strengths varying layers. Occupancy analysis separately found ~25 as the plateau, and concept decomposition used k=16. So "small" was never established by a k-sweep in the original — it was measured by occupancy (the K at which marginal reconstruction improvement falls below a same-size random control) and by fraction of variance explained in excess of a same-size random control, never exceeding 10%. Proposal §4.7's sweep is therefore a genuine methodological strengthening on this axis, not merely a port. That is worth stating in the paper rather than leaving implicit. It also means Phase 3 has **two** axes it could sweep, k and layer band, and the prereg should say which — sweeping both multiplies runs and the compute budget in AI guide §1.4 assumed neither.

**"Workspace loading" is a diagnostic the project should adopt.** Swap failures concentrated where the source concept was weakly present in the lens beforehand; the paper defines a concept's workspace loading as the cosine similarity between the residual stream and that concept's lens vector, averaged over the relevant positions in the unmodified pass, and finds it predicts swap success. Number words load poorly and swap poorly — which the paper reads as either computation happening outside the workspace or the working representation simply not aligning with the lens vectors for those tokens.

That second reading is exactly proposal §4.5's "readout too weak" branch, appearing inside the original paper's own domain. **Measuring item workspace loading in the recommender before interpreting any null is now a required diagnostic**, not an optional one: a null with low loading is uninterpretable in precisely the way the paper already documents for number words.

**Bearing on Phase 4's task gradient.** The GSM8K-with-CoT result says the model offloads to the page when it can. A generative recommender has no page — no chain of thought, no externalisation channel. This removes a confound the original had to handle, but it also raises the bar on hard-task construction: the hard tasks must require inference that genuinely cannot be done in one associative hop, since there is no visible-reasoning condition to contrast against.

---

## 4. Remaining gaps

Not read this session, and each bears on a live decision:

1. **§A.9, extension to multi-token concepts** (template lens, oracle lens). Directly governs the single-token constraint flagged in `PHASE0_adapter_points.md` §4a and therefore the Phase 1 model choice. Read before the Phase 1 go/no-go.
2. **§A.7, methodological details and ablations** — variants including present-only vs. future token effects, frozen attention patterns, and number of averaging contexts. Bears on whether `skip_first=16` and `n_prompts=1000` have documented sensitivity analyses that could be reused instead of re-derived.
3. Whether the 50-prompt multihop reasoning set is released anywhere (§3a above).
