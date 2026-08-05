# Testing (Not Assuming) Whether a J-Space-Like Structure Exists in Generative Recommenders

**Working proposal — NeurIPS 2026 workshop track**
**Status: draft research plan, pre-experimentation**

---

## 1. Background

In July 2026, Anthropic published "Verbalizable Representations Form a Global Workspace in Language Models," introducing a technique called the **Jacobian lens (J-lens)**. For every word in Claude's vocabulary, the J-lens identifies the internal activation pattern that makes the model more likely to say that word at some future point. The subspace of activations this technique surfaces — called **J-space** — is reported to:

- hold only a few dozen concepts at a time, accounting for less than 10% of the model's overall activity
- carry most of the work behind deliberate, multi-step reasoning (ablating it collapses multi-step reasoning while leaving fluent language output intact)
- be legible: its contents correspond to things the model could report if asked, framed against Global Workspace Theory from cognitive science
- have safety-relevant applications: surfacing deception, eval-awareness, and hidden objectives before they appear in visible output

The J-space result was published in July 2026 by a single lab, established primarily on one text-only language model. It shipped with solicited external commentary, one of which included an independent replication on an open-weight model: the core claims reproduced, two experiments did not, and the multi-hop replication was confounded by a dataset whose intermediate and answer terms were linearly related. Every model on which the construct has been established shares a natural-language token vocabulary — the property this project removes. It should be treated as a claim to test, not a fact to build on.

## 2. Original motivating idea

The initial idea behind this project was to ask whether J-space's existing framing — useful for training, verification, and safety monitoring in LLMs — could be extended to content-ranking algorithms (e.g., systems used by Meta, TikTok, and similar platforms), on the theory that both domains involve inferring "meaning" from content and using it to drive downstream behavior.

That framing runs into a structural problem on inspection: **J-lens requires a model with an autoregressive, token-vocabulary output** — it works by projecting intermediate activations onto the model's vocabulary to see which future outputs become more likely. Most production recommendation systems (two-tower embedding models, gradient-boosted trees, wide-and-deep networks) have no such output structure, so J-lens has no meaningful target there — not merely "unconfirmed," but architecturally inapplicable.

However, a real and growing class of architectures **does** have the right shape: **generative recommenders**, which reframe ranking as autoregressive sequence generation over discrete tokens (usually called "semantic IDs"). Examples include:

- **HSTU** (Meta) — a trillion-parameter sequential transducer using hierarchical temporal units, demonstrating NLP-like scaling laws for recommendation
- **TIGER** (Google) — compresses item vocabularies via multi-code vector quantization
- **MTGR** (Meituan) — extends the autoregressive paradigm to industrial-scale generative retrieval using semantic-ID tokenization
- **OneRec**, **GPTRec**, and other open reimplementations (e.g., HSTU-BLaIR) trained on public datasets

These are open, published, reproducible architectures — not access to any real platform's production system (which no outside researcher can obtain regardless) — but they are the correct reference class for testing whether anything J-space-like exists outside pure text LLMs.

## 3. Core research question (staged, not assumed)

**Stage 0 — the actual contribution of this paper:**
Does anything resembling a small, causally load-bearing subspace — analogous to J-space — emerge in an open generative-recommender architecture, when probed with a J-lens-style causal readout? This is framed explicitly as a **replication/generalization test**, with a genuine possibility of a negative result.

**Stage 1 — conditional, out of scope unless Stage 0 succeeds:**
If such a subspace is found to exist *and* is legible, does it carry information useful for auditing the recommender for hidden proxy objectives (e.g., internal representation of outrage, engagement-bait, or other signals never surfaced in the final ranking score)?

Stage 1 is not assumed to follow from Stage 0 automatically — see Section 4.6.

---

## 4. Methodological considerations

The following eight considerations were raised in review of the original idea and materially reshape the experimental design. Each is treated as a distinct, separately-testable issue rather than folded into a single bundled claim — because that bundling is precisely the mistake the original J-space paper could get away with (its findings happened to co-occur in one architecture) but which cannot be assumed to transfer.

### 4.1 The method as originally stated may not be definable in this domain

**The issue:** Generative recommenders output the next item ID, not natural language. There is no channel to ask the model what it's representing, and nothing to "verbalize" in the sense the original paper means. As stated, "does a verbalizable workspace exist in a recommender" is not just unproven — it may be a category error, since there is no verbalization channel to test in the first place.

**Resolution:** Rewrite the target construct so it is actually testable in this domain. Drop "verbalizable" from the hypothesis entirely. The construct under test becomes:

> A small subspace of activations with disproportionate causal influence on the model's future (item-token) output.

This is a structural analogue to J-space, not a claim that the recommender's subspace is verbalizable — that property is explicitly not being tested here, and the paper should say so directly rather than let a reader assume it's implied. To avoid confusion with the original term, this candidate structure is referred to throughout this proposal as the **R-space** (recommender workspace) — a deliberately distinct name to prevent the temptation to silently import J-space's other properties (smallness, verbalizability) by association.

*Stretch/alternate path (not the core plan given time constraints):* If a verbalization channel is wanted, choose a hybrid architecture with a text side-channel — e.g., an LLM-based recommender that generates natural-language justifications, or a review-generation head — which reopens an actual "ask the model" channel instead of removing the claim. This is noted as future work, not part of the minimum viable design.

### 4.2 Item IDs cannot be objectively translated into concepts

**The issue:** Even if a causally important subspace is found, semantic IDs are outputs of a learned vector-quantization scheme with no inherent meaning. Labeling a direction as "this represents nostalgia" or "this represents outrage" is a researcher-imposed narrative unless tied to something external — and different people could rationalize the same code differently. This directly threatens any claim that the subspace is "legible enough to audit."

**Resolution:**
- Use only **pre-existing, external item metadata** (category labels, tags, textual descriptions attached to items independently of this project) as the basis for any interpretability claim — never a post-hoc researcher reading of what a code "seems to mean."
- Explicitly separate **causal importance** (can be established objectively via ablation, see 4.3) from **legibility** (requires independent, externally-grounded validation — e.g., agreement between labelers working from item metadata alone, or quantitative correlation between subspace activation and known item attributes).
- If no reliable, externally-grounded mapping can be established, **report legibility as unresolved or negative** rather than force an interpretation. A causally-important-but-illegible subspace is still a valid and reportable finding — it just cannot support any auditing claim (see 4.6).

### 4.3 Ablation alone conflates three separate claims

**The issue:** The original J-space paper bundles causal importance, compactness ("small"), and verbalizability into one narrative because in that architecture, they happened to co-occur. A single ablation test in a new architecture cannot establish all three at once — each must be demonstrated independently.

**Resolution:** Split into three explicit, separately-reported sub-hypotheses:

| Hypothesis | What it tests | How it's tested |
|---|---|---|
| **H1 — Causal importance** | Does knocking out the candidate subspace degrade task performance more than expected? | Ablation, with random-matched-size control (see 4.8) |
| **H2 — Compactness** | Is the subspace actually small/low-rank, or diffuse? | Measured directly via a dimensionality sweep (see 4.7), not assumed |
| **H3 — Legibility** | Can the subspace be mapped to something externally interpretable? | External metadata correlation / independent labeler agreement (see 4.2) |

A result confirming H1 alone — without H2 or H3 — is still a legitimate, publishable finding ("a causally important but diffuse or illegible subspace exists"). The paper should be structured so partial success is reportable on its own terms, rather than needing all three to say anything.

### 4.4 A null result needs to be diagnosable, which requires positive controls

**The issue:** If the experiment finds nothing, there are at least three very different explanations — the phenomenon doesn't transfer to this domain, the readout technique is too weak to detect it, or there was nothing analogous to find in the first place — and an undiagnosed null cannot distinguish between them.

**Resolution:** Two tiers of positive control, both required before any null result is reported as meaningful:

- **Control A — toolchain validation.** Before touching the recommender, replicate J-lens on a standard open LLM using Anthropic's released code and confirm the basic reported findings (e.g., ablation of the identified subspace disproportionately harms multi-step tasks). This confirms the pipeline itself works correctly, independent of the new domain.
- **Control B — domain-internal positive control.** Within the recommender itself, ablate a component already known or expected to matter (e.g., a core embedding or attention layer) using the exact same ablation methodology, and confirm the method detects that known importance.

With both controls passing, a null result on the actual candidate R-space becomes interpretable: the pipeline works (Control A), the methodology can detect importance within this domain (Control B), and the specific candidate subspace still showed nothing — genuine negative evidence, not a broken instrument.

### 4.5 Associative retrieval vs. multi-step reasoning — and telling "no workspace" apart from "workspace missed"

**The issue:** J-space's causal importance was demonstrated specifically on multi-step reasoning tasks, with minimal impact on fluent, non-deliberate output. If a recommender is doing something closer to associative pattern-matching or nearest-neighbor retrieval rather than anything resembling multi-step reasoning, there may be no analogous workspace to find at all — a real absence, not a detection failure. Critically, this needs to be distinguishable from the alternative explanation that a workspace exists but the readout simply failed to find it.

**Resolution:**
- Construct a **task-difficulty gradient** within the recommender evaluation: easy tasks (single-hop next-item prediction from recent history) vs. hard tasks (compositional or multi-step preference inference — e.g., inferring a preference shift across a sequence with distractor interactions, or transferring inferred taste across categories).
- Test whether ablating the candidate R-space produces a **differentially larger performance drop on hard tasks than on easy tasks**. This differential pattern — not just "ablation hurts performance somewhere" — is the actual signature that would distinguish a reasoning-relevant workspace from a generically important subspace. If no such differential exists, that is evidence against a workspace interpretation regardless of any overall ablation impact.
- **Additional consideration beyond the original eight:** J-lens is a *linearized* (Jacobian-based) readout. If whatever structure exists in a recommender is highly nonlinear, J-lens could produce a false negative purely from a methods mismatch, independent of whether a workspace exists. As a sensitivity check, supplement the linear readout with a simple nonlinear probe (e.g., a shallow classifier trained on candidate-subspace activations) to check whether nonlinear structure is being missed by the linear method alone.

### 4.6 Existence does not imply legibility — two unproven links before any auditing claim

**The issue:** Moving from "we found a causally important subspace" to "we can audit it for hidden signals" silently presumes two separate things are both true: that the subspace exists, and that it is legible enough to read reliably. Neither is established by the other.

**Resolution:** The paper's claims structure should make this dependency explicit rather than implicit:

- **Stage 0a (existence):** H1 + H2 above.
- **Stage 0b (legibility):** H3 above, validated externally per Section 4.2.
- **Stage 1 (auditing):** explicitly conditional on **both** 0a and 0b succeeding — not on 0a alone. If legibility fails, auditing is out of scope regardless of how strong the existence result is, and the paper should say so rather than imply the two findings compose automatically.

### 4.7 Smallness should not be assumed for continuous, distributed preference signals

**The issue:** "Small" was an empirical finding specific to discrete, symbolic (word-level) representations in the original paper. User taste and preference signals are plausibly continuous and highly distributed, with no prior reason to assume they compress into a small subspace. Fixing an assumed subspace size in advance risks a self-fulfilling null: searching the wrong size and concluding "no workspace" when the actual answer is "wrong size searched."

**Resolution:** Treat dimensionality as a variable to measure, not an assumption baked into the design:

- Run the causal-importance analysis across a **sweep of candidate subspace sizes/ranks** (e.g., top-*k* directions for a range of *k* values), rather than testing a single fixed size.
- Plot ablation impact as a function of subspace size. A genuine compact workspace should show a "knee" — a small size beyond which additional dimensions add little further causal importance. A smoothly scaling, diffuse importance curve with no knee is itself evidence against compactness (H2 fails even if H1 succeeds).
- Report the full curve, not a single yes/no verdict at one assumed size.

### 4.8 Ablation needs a random-subspace-of-matched-size control

**The issue:** Without this control, "ablating the candidate subspace hurts performance" could simply mean that ablating *any* subspace of that size hurts performance in an over-parameterized or diffusely-represented model — it doesn't establish that the specific J-lens-identified subspace is special.

**Resolution:** This is standard practice in causal-tracing interpretability work and should be built into the design from the start rather than added after the fact. For every ablation of the candidate (J-lens-identified) subspace, run matched-size **random-subspace ablations** as a baseline — multiple random draws, reporting the resulting distribution of performance impact. The candidate subspace's ablation impact must significantly exceed this random baseline distribution to support any claim of special importance. This control should be applied throughout the dimensionality sweep in 4.7, not just at a single size.

---

## 5. Consolidated experimental design

| Phase | Goal | Key controls / checks |
|---|---|---|
| **0 — Toolchain validation** | Replicate J-lens on a standard open LLM using Anthropic's released code | Confirms pipeline correctness before touching a new domain (4.4, Control A) |
| **1 — Model & task setup** | Select an open generative-recommender architecture (e.g., HSTU-BLaIR, TIGER, or GPTRec reimplementation) trained on a public dataset (Amazon Reviews 2023 subsets, MovieLens-1M, or Steam) | Define both easy (single-hop) and hard (multi-step/compositional) task variants (4.5) |
| **2 — Candidate subspace identification** | Apply a J-lens-style causal readout adapted for an item-token vocabulary, without assuming verbalizability (4.1) | Construct explicitly named R-space, distinct from J-space terminology |
| **3 — Existence testing (H1 + H2)** | Ablation across a dimensionality sweep, with random-matched-size controls at every size | Domain positive control (4.4, Control B); random-subspace baseline (4.8); dimensionality sweep (4.7) |
| **4 — Task-gradient specificity test** | Compare ablation impact on easy vs. hard tasks | Differential-impact signature distinguishes reasoning-relevant structure from generic importance (4.5); optional nonlinear-probe sensitivity check |
| **5 — Legibility testing (H3)** | Map candidate subspace to external, pre-existing item metadata; assess via independent agreement or quantitative correlation | No post-hoc researcher narrative permitted as sole evidence (4.2) |
| **6 — Auditing application (conditional, stretch goal)** | Only attempted if Phases 3–5 succeed: probe for hidden proxy-objective signals (e.g., engagement-correlated activity not present in the final output score) | Explicitly gated on both existence and legibility (4.6) |

---

## 6. Minimum viable paper (fallback scoping)

Given the realistic timeline before the ~August 29, 2026 (AoE) submission deadline shared by most relevant workshops, the full six-phase pipeline is unlikely to be completable end-to-end. The design above is structured so that a partial result is still a legitimate, honest contribution:

- **Phases 0–3 alone** already constitute a defensible standalone paper: *"Testing, Rather Than Assuming, Whether a J-Space-Like Structure Exists in Generative Recommenders."* A properly controlled existence test (with random-subspace baselines and a dimensionality sweep) is a real contribution whether the result is positive or negative.
- **Adding Phase 4** substantially strengthens the paper by distinguishing a reasoning-relevant structure from generic subspace importance — worth prioritizing if time allows after Phase 3.
- **Phase 5 (legibility)** is valuable but explicitly a stretch goal — not required for a valid Stage 0 paper, since existence and legibility are separable claims (4.6).
- **Phase 6 (auditing)** should be treated as out of scope for the initial submission and mentioned only as future work, gated on Phases 3–5 succeeding. Presenting it as anything more than future work without those prerequisites would reproduce exactly the two-unproven-links jump flagged in 4.6.

If time is very limited, a paper reporting **Phase 0–3 with a null result, properly diagnosed against both controls**, is still a genuine and citable contribution — arguably more useful to the field than an under-controlled positive result.

---

## 7. Candidate models and datasets

- **HSTU-BLaIR** — lightweight open configuration of Meta's HSTU architecture (four transformer blocks, four attention heads), evaluated on Amazon Reviews 2023 subsets (Video Games, Office Products, Musical Instruments)
- **GPTRec** — GPT-2-based sequential recommender with SVD tokenization, evaluated on MovieLens-1M
- **TIGER-style reimplementations** — semantic-ID generative recommenders via residual vector quantization
- Public interaction datasets: Amazon Reviews 2023, MovieLens-1M, Steam dataset

All of these are open, reproducible, and independently runnable — avoiding any reliance on access to a real platform's production system, which would not be obtainable regardless of framing.

---

## 8. Fit with NeurIPS 2026 workshops

Based on the current (provisional, subject to change) NeurIPS 2026 workshop guide:

- **Interp4Discovery** ("Interpretability for Discovery") — Atlanta, submission deadline August 29, 2026 — strong fit, since this project is explicitly framed as using an interpretability technique to investigate an open empirical question rather than assuming an established result.
- **IAB** ("Interpreting Agent Behavior") — a fit if the recommender is framed as the "agent" under interpretation.
- **ATTRIB** ("Attributing Model Behavior at Scale") — a secondary fit, particularly if the dimensionality-sweep/ablation methodology is emphasized as a general attribution technique.

A negative or partial result should be framed explicitly as a methodological contribution (a properly controlled generalization test), which fits workshop venues that value rigorous negative results, rather than venues expecting a positive application.

---

## 9. Honesty checklist for the paper itself

The following should be stated explicitly and prominently, not left implicit:

- J-space is a recent single-lab result, established on one text-only language model. It has since been replicated in part on a second, open-weight text model; both models share the property this project removes, a natural-language token vocabulary.
- This project does **not** test verbalizability in the recommender domain — that property is explicitly excluded from the hypothesis (4.1).
- Any legibility claims are provisional and depend entirely on external, pre-existing metadata — not researcher interpretation (4.2).
- Causal importance, compactness, and legibility are reported as **three separate results**, not one bundled claim (4.3).
- All null results are accompanied by both toolchain and domain-internal positive controls, and are diagnosed accordingly rather than reported as unqualified negatives (4.4).
- The linear (Jacobian-based) nature of the readout method is acknowledged as a possible source of false negatives if the true underlying structure is nonlinear (4.5).
- No auditing or safety claim is made unless both existence and legibility are independently established (4.6).
- Subspace size is measured via a sweep, never assumed in advance (4.7).
- All ablation results are reported alongside matched-size random-subspace baselines (4.8).

---

## 10. Immediate next steps

1. Set up and run Phase 0 (toolchain validation) using Anthropic's released J-lens code on a small open LLM.
2. Select and stand up one candidate generative-recommender architecture (recommend starting with HSTU-BLaIR or GPTRec for lighter compute requirements) on a public dataset.
3. Define the easy/hard task split concretely for the chosen dataset before any subspace analysis begins, so the task-gradient test (Phase 4) is not designed post hoc around whatever result Phase 3 produces.
4. Draft the random-subspace-baseline and dimensionality-sweep pipeline once the candidate R-space identification (Phase 2) is working, so Phases 3 and 4 can run together.
5. Revisit scope against the timeline after Phase 3 results are in, and make an explicit go/no-go decision on Phases 5 and 6 rather than letting them expand implicitly.
