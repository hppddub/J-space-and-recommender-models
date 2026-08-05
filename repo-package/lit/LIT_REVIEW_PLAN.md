# Literature Review — Concept Shortlist, Practices, and Execution Plan

**R-Space Generalization Test · drafted 2026-08-04 · Claude draft, Stew owns**
**Status:** proposal. Nothing here is committed until signed.
**Governs:** the literature-review work block designated for the travel period.

---

## 0. Session frame

Per `AI_COLLABORATION_GUIDE.md` §4.1, run before anything else.

| | |
|---|---|
| **Phase** | Writing track / Phase 1 preparation. Not an experimental phase. |
| **Which hypothesis does this serve?** | **None — infrastructure.** No literature finding is evidence for or against H1, H2 or H3. Literature can only (a) tell you what has already been established, (b) tell you what a reviewer will object to, and (c) supply *pre-existing* design choices that make your own evidence more defensible. |
| **What does a "null" look like here?** | The search finds that a small causally load-bearing subspace is already a known generic property of transformers, published under other names. That would not invalidate the project, but it would **change what H1 is worth**, and the paper would have to say so. This is the outcome to search *for*, not against. See §2.A and §4. |
| **Nuance-ledger rows in play** | Row 1 (no verbalization), Row 2 (metadata provenance — Cluster G), Row 5 (difficulty gradient — Cluster D). |
| **Compliance items in play** | C6 (every citation verified against primary source), C8 (dataset licences and deprecation), C9 (model/code licences), C13 (CFP re-fetch). |

**One flag before we start.** `LIT_REVIEW_PROTOCOL.md` exists in the repo but is **not attached to this Project** — it was not in the file set for this session. This document was written without seeing it. Before adopting anything below, reconcile the two; where they conflict, the protocol wins, since it was signed and this is a draft.

---

## 1. What this literature review is actually for

It has three consumers, and they want different things. Confusing them is how a literature review becomes a month of reading with no output.

**Consumer 1 — the related-work paragraph.** The CFP caps main text at five pages. Related work gets roughly a **half page, twelve to twenty lines**. It cannot be a survey. Its only job is to place the contribution and pre-empt "this is already known."

**Consumer 2 — the reviewer's objection list.** Larger consumer, and mostly invisible in the final text. What will a reviewer at an interpretability workshop already believe about ablation evidence, lens-family readouts, and recommender models? Every one of those beliefs is a possible desk-level objection, and each one is answerable in one sentence *if you know it exists*.

**Consumer 3 — decisions that are still open right now.** This is the time-critical consumer and the reason to start today rather than during the write-up. Specifically:

- Which generative recommender to stand up (Phase 1, G1 is next).
- Whether one-item-one-token is achievable, which determines whether the template lens has to be implemented (`Phase1_HANDOFF.md` §4).
- What the easy/hard task split is, which must be frozen before Phase 3 and is far more defensible if the difficulty axis comes from existing literature rather than from you.
- Dataset licence and metadata-provenance facts (C8; Phase 5 requires metadata that provably predates the project).

**Practical consequence:** read for Consumer 3 first, then Consumer 2, then Consumer 1. That inverts the intuitive order. Do it anyway — Consumer 3 unblocks GPU work, and reading during travel is the only cheap time it has.

---

## 2. Concept shortlist

Seven clusters. Each is a set of **questions**, not a set of papers. Per protocol, Claude does not supply citations; you populate the ledger from primary sources.

Priority column: **P1** = blocks a decision in the next two weeks. **P2** = shapes the paper. **P3** = cheap, do last.

---

### A. Is R-space a rediscovery? *(P2 — but it is the highest-stakes cluster)*

**Why it matters.** The whole project asks whether a small, causally load-bearing subspace exists in a new architecture. If the interpretability literature has already established that *most* transformers contain small sets of directions whose removal disproportionately damages complex behaviour, then finding one in a recommender is close to uninformative on its own, and H1 alone carries very little. The weight would shift entirely onto H2 (compactness measured against a matched random baseline **and** against next-k) and onto Phase 4's task differential.

**This is not hypothetical.** The Control A result already points this direction: next-k directions were nearly as damaging as top-k (13.7% vs 6.8% at heavy, against a ~63% random cloud). If the literature independently says "important low-dimensional structure is generic," those two facts jointly reframe the paper.

**Questions:**
1. Under what other names has "ablating a small set of directions disproportionately damages multi-step behaviour" been reported? Search framings to try, independently of each other: subspace ablation, causal mediation analysis, activation patching, circuit discovery, sparse feature circuits, low-rank task structure, single-direction behavioural results, attention-head ablation for reasoning tasks.
2. Where such results exist, what baseline did they use? Specifically: did they compare against matched-size *random* subspaces, or only against no-ablation? A literature that lacks random baselines makes your §4.8 control a contribution rather than hygiene.
3. Is the J-space claim's novelty located in the **existence** of the subspace, or in the **lens construction** that finds it, or in the **legibility/verbalizability** property? These have different implications for what porting the method proves.
4. Has anyone reported the *converse* — that ablating random directions of matched size produces comparable damage — in any architecture? That would be a direct threat.

**What a bad outcome looks like:** finishing this cluster with only supportive references. If nothing in it threatens the framing, the search was too narrow.

---

### B. Current status of the J-space result *(P2)*

**Why it matters.** `COMPLIANCE_GUIDE.md` §5 flags this explicitly: the proposal's "single-lab, ~1 month old" framing was written at design time and is now stale. Repeating stale framing reads to a reviewer as inattention, not caution. Separately, your criterion-4 failure needs to be positioned against what others have found.

**Questions:**
1. As of the submission date, what is the replication status? Is the in-progress open-model replication now public? Published, preprint, blog, or still in progress? Result?
2. Has any independent group reported the intact-side finding — that ablation leaves fluent generation intact — and with what measure? Your failure was on WikiText top-1; MMLU was intact. **If others also fail the distributional-preservation claim, your partial replication is corroborative rather than anomalous, and the write-up changes.** If nobody has looked, say that.
3. What exactly does the original claim about the intact side, in its own words, and against which measure? Criterion 4's status hinges on whether your pre-registered measure was the paper's measure or a stricter proxy for it.
4. Any published critique of the Global Workspace Theory framing, or of the inference from "ablation collapses reasoning" to "this is a workspace"?
5. Have the template-lens pathologies documented in the appendix (premature skip-to-answer, 67% final-layer top-10 hit rate, spurious high-frequency words) been discussed or extended by anyone since?

**Standing caution:** the J-space paper postdates my training cutoff. I am not a source on any of this and should not be used as one, including for "roughly what it says."

---

### C. Generative recommender architectures *(P1 — blocks Phase 1)*

**Why it matters.** Phase 1 is next. The model choice determines whether the instrument works at all.

**Questions, to be answered per candidate architecture** (the proposal names HSTU, HSTU-BLaIR, TIGER, MTGR, OneRec, GPTRec — treat that list as a starting point, not a closed set, and verify each name against a primary source since it currently comes from your own earlier draft):

1. **Are weights released, or only code?** Training from scratch inside the remaining budget is a different project. This alone may decide it.
2. **How many tokens per item?** Residual vector quantization typically emits several codes per item. `Phase1_HANDOFF.md` §4 makes the consequence concrete: multi-token semantic IDs push you onto the template lens, which means implementing an appendix method and accepting weaker H1 evidence in a nameable way. **A one-item-one-token architecture is worth real effort to find.** Does GPTRec's SVD tokenization give it? Does any MovieLens-scale model treat items as atomic vocabulary entries?
3. **Depth.** Control A's band saturated at L15 of a 36-layer model. A four-block model may not have enough depth for a layer band to be a meaningful object. What is the depth of each candidate, and is there any published layer-wise analysis of these models at all?
4. **Access.** Is the residual stream reachable, and is there an output projection over a discrete vocabulary? This is the architectural precondition (proposal §2) and it should be verified from code, not from the paper's description.
5. **Benchmarking practice.** Sequential recommendation has a documented history of evaluation and reproducibility disputes — sampled-metric issues, weak baselines, inconsistent splits. Find out what the current consensus protocol is, because Control B's design depends on being able to say "this model performs as published on its own benchmark."

---

### D. Is there anything reasoning-like in a recommender? *(P1 — feeds G1)*

**Why it matters.** `EXECUTION_GUIDE.md` Phase 4 names interpretive branch (c): the recommender may do associative retrieval with no multi-step reasoning at all, in which case there is no workspace to find and a null means something quite specific. The Phase 1 difficulty gradient is the evidence that speaks to (c), and G1 gates on it.

**Questions:**
1. What is the strongest published evidence of compositional or multi-step behaviour in sequential recommenders? What is the strongest published evidence *against* it?
2. **What difficulty axes already exist in this literature?** Candidates to check: cold-start vs warm items, long-tail vs head, sequence length, repeat consumption vs exploration, within-category vs cross-category transitions, session-boundary effects. Using an axis that already exists in published work is substantially more defensible than inventing one, because the freeze then rests on something external.
3. For whichever axis you pick: is there a published base-rate performance gap on it? That gives you a prior for what G1 should expect, before you measure it yourself.
4. Has anyone framed a recommendation task as explicitly multi-hop? If someone has, that is the closest analogue of Control A's two-hop prompts and a candidate Control B design.

---

### E. Method critiques — the null-diagnosis armoury *(P2)*

**Why it matters.** If Phase 3 returns a null, the diagnosis has to be written against four evidence sources. Two of them (Control A, Control B) you generate. The other two — "the readout may be too weak" and "the method may be too linear" — are strengthened enormously by knowing what the field already says about these failure modes.

**Questions:**
1. What pathologies are documented for the lens family generally (logit lens, tuned lens and successors)? J-lens inherits from this family; the appendix already admits the template lens shares tuned-lens pathologies. What else is known?
2. **Ablation methodology.** Zero-ablation vs mean-ablation vs resample-ablation: what is the current argument? Zeroing directions pushes activations off-distribution, and there is a real literature on whether the resulting damage is evidence about the direction or about distributional shift. **A reviewer will raise this.** Know the answer before they do.
3. What is standard practice for random/matched controls in subspace-importance claims? Is 19 draws considered adequate, and against what statistic?
4. Interpretability illusions: what is documented about probing and ablation results that turned out to be artifacts of the method? This belongs in the limitations paragraph regardless of outcome.
5. The ignition experiment carried forward as open item 1 from G0 — is there a readout-independent band-localisation method in the literature you could adopt rather than build? This is required for Phase 2 and currently unimplemented.

---

### F. Auditing, proxy objectives, dual use *(P3 — cheap, do last)*

**Why it matters.** Feeds the introduction's motivation and the mandatory responsible-use statement (C3). **Explicitly not a source of claims** — nothing here is evidence for R-space.

**Questions:**
1. What does the recommender-auditing literature currently assume is possible from the outside, and what does it say is impossible? This grounds the proposal's honest substitution: nobody outside these companies can inspect production systems, so this was tested on an open architecture of the same class.
2. Has anyone demonstrated an internal engagement-correlated signal not present in a model's final ranking score? If so, that is the closest prior work to the Stage 1 framing and must be cited — and it also means Stage 1 is less novel than the proposal assumes.
3. For the dual-use paragraph: is the "a method to find it is a method to target it" symmetry already discussed anywhere in an interpretability-safety context? Citing an existing framing is stronger than asserting your own.

---

### G. Datasets — licences, deprecation, metadata provenance *(P1 — compliance, C8)*

**Why it matters.** Two hard requirements and one Phase 5 precondition. This is bookkeeping, not scholarship, but it is desk-reject-adjacent and it is cheap during travel.

**Questions, per dataset** (MovieLens-1M, Amazon Reviews 2023 subsets, Steam):
1. Exact licence terms and citation requirements, from the source, recorded verbatim in the repo.
2. Is it on the NeurIPS deprecated-datasets list?
3. **Metadata provenance and date.** Phase 5 requires metadata that provably predates and is independent of this project. Record when each metadata field was created and by whom. Do this now — it is much harder to establish retroactively.
4. PII exposure: Amazon Reviews carries real review text and reviewer identifiers. What appears in any figure or appendix, and what justifies it?

---

## 3. Best practices

Eleven, ordered roughly by how much trouble ignoring them causes.

**1. Question-first, never topic-first.** A topic ("interpretability of recommenders") has no completion condition and expands to fill available time. A question ("does any open generative recommender emit one token per item?") is answered or not. Every ledger row starts as a question from §2.

**2. One claim per ledger row, with a location anchor.** A row is: the claim, the source, the section or page it appears in, whether you read the method or only the abstract, the date you read it, and which of your paper's sentences it supports. If you cannot name the sentence it supports, you probably do not need the row.

**3. Two-tier reading, with a hard budget on the deep tier.** Triage tier: title, abstract, figures, limitations — five minutes, decision to promote or drop. Deep tier: method and limitations read properly — forty-five minutes. **Budget eight to twelve deep reads total.** At five pages you cannot use more, and a deep read you did not need is time taken from Phase 1.

**4. Record the negative search.** Keep `searches_log.md`: query strings, where you searched, the date, and what you did *not* find. This is the only thing that licenses the phrase "to our knowledge, no prior work has…" — and that phrase is doing real load-bearing work in this paper's novelty claim. A reviewer who finds the thing you missed will treat an unlogged search as carelessness and a logged one as an honest miss. It is the same discipline as the append-only lab log, applied to reading.

**5. No citation enters from recall — mine, yours, or anyone's.** C6 and the Handbook LLM policy make hallucinated citations a Code of Conduct matter, not a style issue. **I will not propose citations, and if I name a paper in conversation, treat it as a lead to verify, never as a reference.** Every `.bib` entry gets opened at the primary source and checked field by field before it is written.

**6. Snowball both directions, and record where you stopped.** From a small seed set, walk references backward and citing works forward. Stop when two consecutive expansions surface nothing new — that is saturation — and write down that you stopped there and why.

**7. Read limitations sections first, in the closest works.** Authors of adjacent papers have already written the objection a reviewer will make to you. It is the cheapest source of Consumer-2 material in existence.

**8. The ledger has a threat column, and it must not be empty.** Every source gets classified as supporting the framing, threatening it, or neutral. **If cluster A finishes with no threats, the search failed** — not the hypothesis. This is the literature-review analogue of the random baseline: a control that cannot fire is not a control.

**9. Date-stamp every claim about the state of the field.** Cluster B in particular. The paper describes the field as of late August, not as of design time. A dated ledger makes the final pass mechanical instead of a re-read.

**10. Log lit-review sessions in the lab log like any other session.** Same three questions. "Which claim does today's work support?" will be "none — infrastructure" most days, and that is the correct answer, but asking it is what keeps a reading day from quietly becoming a framing day.

**11. Time-box against the experimental schedule, not against the reading.** Reading is comfortable, unbounded, and always feels productive. See §5.

---

## 4. Execution plan

Five passes. Days are working blocks, not calendar days.

### Pass 0 — Setup *(half a day, before travel)*

- Reconcile with the signed `LIT_REVIEW_PROTOCOL.md`.
- Create `lit/claim_ledger.md`, `lit/searches_log.md`, `lit/candidates.md`.
- Write inclusion criteria down: what makes a source worth a deep read. Doing this before you start reading is the same move as pre-registration — it stops the criteria from drifting toward whatever you happen to find.
- Fix the deep-read budget as a number. Write it down.

**Deliverable:** three empty-but-structured files and a written inclusion criterion.

### Pass 1 — Triage, breadth *(≈2 days, travel)*

Work clusters in priority order: **C and G first** (they unblock Phase 1), then **D**, then **A** and **E**, then **B**, then **F**.

Abstracts and figures only. Populate `candidates.md` with promote/drop and a one-line reason for each. Populate `searches_log.md` as you go, not afterward — reconstructing a search log is exactly the sin the lab log rules exist to prevent.

**Deliverable:** candidate list with triage decisions; searches log; Cluster G fully closed (licences and metadata provenance are triage-tier facts, not deep-read facts).

### Pass 2 — Deep reads *(≈2 days, travel)*

Eight to twelve sources, method and limitations sections read properly. Ledger rows written as you read, with location anchors.

Order within this pass is **C → D → A → E → B → F**, so that if you run out of time the losses fall on the clusters that shape the paper rather than the ones that unblock the experiment.

**Deliverable:** populated claim ledger with the threat column non-empty in clusters A and E.

### Pass 3 — Adversarial pass *(half a day)*

Paste the ledger to me. My role, per the protocol: **reviewer, not researcher.** Specifically I will —

- Attack the novelty claim using only what is in your ledger.
- Identify which of your intended paper sentences have no supporting row.
- Identify rows that support a *stronger* claim than the one you are making, which is the quiet form of overclaim.
- Name the clusters where the threat column is empty and say what that implies about the search.
- Check no row imports an unverified J-space property by assumption.

I will not add sources, fill gaps from memory, or tell you a paper exists.

**Deliverable:** a written objection list, and a short list of gaps to close in a targeted Pass 1b.

### Pass 4 — Drafting *(during write-up, not now)*

Related-work paragraph, the limitations paragraph, and the grounding for the responsible-use statement, drawn only from ledger rows. If a sentence has no row, it does not go in.

**Deliverable:** ≤20 lines of related work, budgeted against `PAGE_BUDGET.md`.

### Pass 5 — Verification *(≈26–28 August, hard gate)*

Every reference opened at the primary source and checked one by one: authors, title, venue, year, and that the paper actually says what the row says it says. C6 signed off. No exceptions, no sampling.

**Deliverable:** signed C6 line in the compliance ledger.

### Proposed checkpoint

I would suggest a named checkpoint at the end of Pass 3 asking: **"Does the literature change what H1 is worth?"** If cluster A establishes that small important subspaces are generic in transformers, the paper's contribution shifts from H1 toward H2 and the task differential, and that shift needs to be a logged decision rather than something that happens silently during drafting.

Whether that becomes a numbered gate is your call — adding to the gate structure is a governance decision and I should not make it by proposing one.

---

## 5. Risks specific to this work block

**1. The inverted incentive on novelty.** Cluster A is the one cluster where finding something is *expensive* — a strong prior result weakens the paper. That is precisely the incentive structure that produces a shallow search, and it will not feel like a shallow search from the inside; it will feel like the literature being sparse. Mitigation: the threat column requirement (§3.8), and the negative search log (§3.4) making the shallowness visible if it happens.

**2. Reading as avoidance.** Sixteen days to the 18 August checkpoint, Phase 1 not started, and literature review is the one activity that is legitimately schedulable during travel *and* infinitely expandable. The failure mode is arriving at 18 August with an excellent bibliography and no Phase 1. Mitigation: the deep-read budget as a hard number, and Pass 1/2 ordered so Phase 1's blocking questions are answered in the first day.

**3. Importing the source paper's framing wholesale.** The natural move when reading the J-space paper's related work is to inherit its citations and its framing of the field. That framing was constructed to situate *that* claim in *that* domain. Inheriting it silently reintroduces exactly the assumption-import the R-space renaming exists to prevent. Mitigation: cluster B rows get flagged as "from the source paper's framing" so the dependency is visible.

**4. Prior plausibility treated as evidence.** If cluster D turns up work suggesting recommenders do something reasoning-like, the temptation is to treat that as raising the prior on R-space existing. It does not. It bears on interpretive branch (c) in the null diagnosis and on task design — nothing else. No literature finding is evidence for H1, H2 or H3.

**5. Citation drift from me.** The highest-consequence risk in the whole block, per `COMPLIANCE_GUIDE.md` §3.3. If you ask me "what's the paper that showed X" I will produce something that sounds right. Treat any name I emit as a string to search for, never as a reference.

---

## 6. Open for your decision

1. **Reconcile with `LIT_REVIEW_PROTOCOL.md`.** Not attached to this Project; this plan may duplicate or contradict it. The signed protocol wins.
2. **Should I be allowed to run web searches to locate candidate sources?** The protocol as recorded says I propose questions and you populate from primary sources. Using me as a discovery tool — surfacing candidate titles for you to verify — is a different and weaker role than supplying citations, and it might save real time during travel. But it is a **change to a signed protocol**, and if it happens it should be an explicit amendment with a stated boundary, not a drift that starts with one convenient search. My recommendation is to keep the current rule for cluster A specifically, where the incentive problem is sharpest, and consider relaxing it for clusters C and G, which are factual lookups with verifiable answers.
3. **Deep-read budget:** confirm a number. My suggestion is ten.
4. **The Pass 3 checkpoint** — numbered gate, or informal?
5. **Cluster ordering:** I have put Phase-1-unblocking clusters ahead of paper-shaping clusters. If you would rather have the framing settled first, say so — but note that would mean arriving home from travel still unable to start Phase 1.
