> **SUPERSEDED 2026-08-05 by lit/LIT_REVIEW_PLAN.md** — written before Phase 0
> results and the compliance ledger existed. Retained for the record.

# Literature Review Protocol — R-Space Generalization Test

**Repo location:** `proposal/LIT_REVIEW_PROTOCOL.md`
**When:** between Phase 0 sign-off (G0) and Phase 1 start.
**Companion to:** `AI_COLLABORATION_GUIDE.md` §3 (risky request patterns) — this document extends it to the literature.
**Status:** draft — requires Stew's sign-off.

---

## 0. The failure mode this is designed against

A language model asked about literature will produce fluent, plausible, correctly-formatted citations that do not exist, or that exist but do not say what it claims. It will also attach specific numbers to papers it has only partially encountered. It does this most confidently in exactly the places where verification is hardest: adjacent-field work, recent work, and work it has seen only in summary.

The NeurIPS 2026 Main Track Handbook names hallucinated citations specifically as a Code of Conduct violation and places responsibility for every reference on the author. This is not only a project-discipline concern.

**The structural fix is role separation, not carefulness.** Careful use of an unreliable source is still use of an unreliable source. The protocol below removes Claude from the citation-supply chain entirely.

---

## 1. Claude's declared limits — read this first

**Knowledge cutoff: end of May 2026.**

The Anthropic J-space paper was published in July 2026. **It is after Claude's cutoff.** Everything Claude appears to "know" about J-lens, J-space, the workspace band, the ablation protocol, or the appendices comes from documents supplied in this Project — that is, from the proposal's own summary and from any PDF pasted into a session. It is a summary of a summary.

Consequences, which hold regardless of how confident Claude sounds:

- **Claude is not a source on the primary paper of this project.** Any statement Claude makes about what the J-space paper says must be checked against the PDF, including statements it made in earlier sessions.
- Claude cannot report the current replication status of the J-space finding. That is the single most framing-critical fact in the paper (proposal §9 item 1) and it must come from a retrieved source.
- Anything published after May 2026 in generative recommenders, mechanistic interpretability, or causal subspace methods is invisible to Claude unless retrieved.
- Anything published *before* May 2026 is known imperfectly and unevenly.

**Operating rule:** treat every Claude utterance about a paper as a *hypothesis to check*, never as a citation.

---

## 2. Role separation

| Task | Who |
|---|---|
| Deciding what the review must establish | Stew |
| Proposing questions the literature must answer | Claude |
| Finding papers | Stew, or Claude via retrieval with sources in context |
| Reading the paper | **Stew** |
| Supplying a citation for the bibliography | **Stew only** |
| Recording what a paper says | Stew, into the claim ledger |
| Arguing that a characterisation is wrong | **Claude — highest-value use** |
| Deciding whether a claim is supported | Stew |

**Claude never writes a bibliography entry from recall.** If Claude produces a title, author, or year that was not retrieved in-session or supplied by Stew, that entry is discarded, not verified — because verifying a fabricated-then-confirmed citation still means the search was anchored on a fabrication and the real relevant work was never looked for.

**Retrieval is different from recall.** Claude searching and reading a retrieved page is grounded. That output is provenance tier T2 (below), not T1, and still requires Stew to open the primary source before it supports a specific claim.

---

## 3. Provenance tiers

Every entry carries a tier. The tier determines what it is allowed to support.

| Tier | Meaning | May support |
|---|---|---|
| **T1** | Stew opened the paper and read the relevant section | A specific claim about method, result, or number — with a section/figure locator |
| **T2** | Abstract or landing page read from the publisher/arXiv; or retrieved in-session by Claude | "This work exists and concerns X." Nothing about what it found |
| **T3** | Mentioned by another paper, or surfaced by Claude, not yet retrieved | **Nothing.** Resolve to T1/T2 or delete |

**No T3 entry appears in the paper.** Not in related work, not in a footnote, not as "see also."

**A number never comes from a T2.** If the paper reports "prior work found a 40% drop," that is a T1 claim with a figure or table locator, or it does not go in.

---

## 4. The claim ledger

One row per sentence you intend to write about someone else's work. Store as `proposal/lit_claim_ledger.md`.

| # | Claim as it will appear | Source | Tier | Locator (§/fig/p) | Checked by Stew | Adversarial pass |
|---|---|---|---|---|---|---|
| 1 | | | | | [ ] | [ ] |

**The locator field is the control.** If you cannot say *where* in the paper the support is, you do not have the support. An empty locator field means the claim does not enter the draft. This catches the most common real failure, which is not a fabricated paper but a real paper misremembered.

---

## 5. What this review is actually for

**Calibration first, because it changes the size of the job.** The submission is five pages of main text. Related work is 3–5 sentences folded into the introduction (see `paper/PAGE_BUDGET.md` §1). This review is **not** for filling a related-work section.

Its real jobs are four:

**A. Has this already been done?** If someone has applied mechanistic-interpretability subspace methods to generative recommenders, the paper's contribution changes and you need to know before Phase 1, not at review. This is the highest-value question and should be answered first.

**B. What is the current status of the J-space finding?** Proposal §9 item 1 and the introduction both depend on it. The design-time framing ("~3 weeks old, single-lab, replication in progress") is now stale and will read as inattention. Whether the open-model replication succeeded, partially succeeded, or failed materially affects how Control A's result should be presented — and if a public replication now exists, it is a comparison point for your own Control A magnitudes.

**C. Is the Phase 1 model choice still right?** Proposal §7 names HSTU-BLaIR, GPTRec, TIGER reimplementations. That list has a date on it. Confirm the chosen architecture is still available, still the lightest viable option, and still genuinely autoregressive over a discrete token vocabulary.

**D. Are the controls standard practice?** Matched random-subspace baselines (4.8) and dimensionality sweeps (4.7) should be grounded in how causal-tracing and activation-patching work actually reports them. This costs one or two citations and pre-empts a reviewer asking why your baseline is constructed the way it is.

**Anything not serving A–D is out of scope for this review.** Interesting adjacent literature goes in a notes file for a future, longer paper.

---

## 6. Question list, not a reading list

Claude proposes questions. Stew finds the papers. This ordering matters: a list of paper titles from Claude invites fabrication and anchors the search on whatever Claude happened to recall; a list of questions does neither.

Questions to carry into the search:

1. Has any published work applied activation patching, causal tracing, or subspace ablation to a *generative* recommender (semantic-ID / item-token autoregressive)? *(Job A — answer first)*
2. Has any published work applied mechanistic interpretability to recommender systems of any architecture? *(Job A, wider net)*
3. What is the current replication status of the J-space / global-workspace finding, on any open-weight model? *(Job B)*
4. Are HSTU-BLaIR, GPTRec, and TIGER reimplementations still the lightest viable open generative recommenders, and are checkpoints or training recipes available? *(Job C)*
5. How do causal-tracing and activation-patching papers construct and report matched random-subspace baselines? *(Job D)*
6. How is subspace dimensionality typically established in interpretability work — sweep, elbow criterion, variance threshold? *(Job D, supports H2's knee analysis)*
7. Is there prior work claiming workspace-like or bottleneck-like structure in non-language sequence models? *(context for the generalization framing)*
8. What is known about linear probes producing false negatives where structure is nonlinear? *(supports proposal 4.5's sensitivity check)*

Questions 1 and 3 are load-bearing. If either returns something unexpected, stop and reassess scope before Phase 1 rather than absorbing it.

---

## 7. Procedure

1. **Time-box it.** Two to three working sessions. This is travel-week work: it needs reading and judgement, not GPU sessions. If it runs past three sessions, that is a scope problem to log, not a sign of thoroughness.
2. Work question by question from §6, in order. Record every search actually run — query terms and date — in the lab log, so a reviewer question about coverage has an answer.
3. For each candidate paper: record at T2 first (exists, is about X). Promote to T1 only after opening it.
4. Fill the claim ledger as you go, never afterward from memory.
5. **Record what you searched for and did not find.** For question 1 especially, "no prior work located applying subspace ablation to generative recommenders, searched via [terms] on [date]" is a claim the paper may well need to make, and it needs evidence of the search, not just the absence.
6. Hand the ledger to Claude for the adversarial pass (§8).
7. Only then draft the 3–5 introduction sentences.

---

## 8. Adversarial pass — Claude's actual job here

Once the ledger is populated with T1 entries, Claude's task is to attack it, not to extend it. Specifically:

- For each claim, argue the case that the characterisation is wrong, overstated, or would be contested by someone who knows that literature.
- Flag any claim whose locator field is empty or vague.
- Flag any claim that a T2 entry is being asked to support.
- Flag any sentence that bundles two hypotheses, imports a J-space property, or uses a banned phrasing (guide §2.1) — chat and drafts inherit each other's language.
- Ask, for each: would this still be worth citing if the final result is null?

Claude must **not**, during this pass, suggest additional papers from recall. If a gap is apparent, Claude names the *gap* — "nothing here supports the claim that X is standard practice" — and Stew searches.

---

## 9. Standing additions to the collab guide

Proposed rows 14–15 for `AI_COLLABORATION_GUIDE.md` §3:

| # | The request | Why it's risky | What Claude should do instead |
|---|---|---|---|
| 14 | "What papers should I cite for X?" / "Who showed Y?" | Claude produces plausible, well-formatted citations from recall. Some will not exist; others will not say what is claimed. Handbook names hallucinated citations as a Code of Conduct violation | Do not supply citations from recall. Offer the *question* the literature must answer and search terms. If retrieval is available, retrieve and mark the result T2. State the cutoff limitation explicitly |
| 15 | "Summarise what the J-space paper says about Z" | The paper postdates Claude's training cutoff. Any answer is reconstructed from this Project's own summary documents and will sound authoritative regardless | Say plainly that the source is the Project's summary, not the paper. Direct to the PDF. Answer only from text pasted in-session |

---

## 10. Sign-off

**Decision-maker:** Stew.
**Status:** [ ] reviewed  [ ] signed off  [ ] collab guide rows 14–15 adopted
**Date:** ____________
