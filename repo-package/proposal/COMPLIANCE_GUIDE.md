# Compliance Guide — R-Space Generalization Test

**Companion to:** `jspace_generative_recommenders_proposal.md` (**the proposal**), `EXECUTION_GUIDE.md` (**the guide**), `AI_COLLABORATION_GUIDE.md` (**the collab guide**)
**Purpose:** map the actual venue requirements onto the project's existing phase and gate structure, and name the gaps.
**Repo location:** `proposal/COMPLIANCE_GUIDE.md`
**Sources retrieved:** 2026-07-28. All venue material below is marked *tentative* by its publisher and must be re-checked before submission.

---

## 0. Precedence

The proposal governs *what is claimed*. The guide governs *how it is run*. The collab guide governs *how an AI assistant is used*. This document governs *what the venue requires*, and it has no authority over any scientific claim.

Where this document conflicts with the other three on a scientific question, they win. Where it conflicts with them on a **venue requirement**, this document wins and they get corrected — because venue requirements are external facts, not project choices.

---

## 1. Which documents actually govern this submission

This matters, because two of the three documents most often assumed to govern a NeurIPS workshop submission do not.

| Document | Governs | Binds this project? |
|---|---|---|
| **Interp4Discovery CFP** (`interpretability4discovery.github.io/cfp.html`) | Papers submitted to this workshop | **Yes — this is the binding document** |
| NeurIPS 2026 Workshops Guidance (`neurips.cc/.../WorkshopsGuidance`) | *Proposals to organize a workshop* | **No, not directly.** Binds the organizers. Sets the outer envelope the CFP sits inside |
| NeurIPS 2026 Main Track Handbook (`neurips.cc/.../MainTrackHandbook`) | Main-track (9-page, archival) submissions | **No, not directly.** Relevant via two inheritance paths (§3.3, §3.5) and as a Plan B venue (§7) |
| NeurIPS Code of Ethics / Code of Conduct | Everyone in the program | **Yes** |

**Consequence.** A compliance checklist built against the Handbook would over-constrain the paper (9 pages, main-track checklist, funding statement) and simultaneously miss the two requirements that can actually cause desk rejection here: the responsible-use statement and the five-page limit.

**Standing rule.** Before submission, re-fetch the CFP page. It is explicitly labelled provisional in two places, and the organizers reserve the right to expand formats. A compliance guide written 32 days out is a snapshot, not a contract.

---

## 2. Confirmed dates and the schedule reality

From the CFP and the NeurIPS Workshops Guidance, both retrieved 2026-07-28:

| Item | Date | Source |
|---|---|---|
| Submission deadline | **August 29, 2026, 11:59 PM AoE** | CFP (exact); NeurIPS lists this as a *suggested* date that workshops may vary — Interp4Discovery adopted it |
| Author notification | On or before September 29, 2026 | CFP; NeurIPS-mandated, stated as non-extendable |
| Workshop | December 12 **or** 13, 2026, Atlanta | CFP; final day TBC |

**Days remaining as of 2026-07-28: 32.** In local time (Markham, EDT) the AoE deadline falls the morning of August 30.

**The honest read.** Phase 0 is not complete. The minimum viable paper (proposal §6) is Phases 0–3. That is four phases in 32 days, on rented GPU time, with the collab guide's own §1.4 warning that Phase 0 is the most compute-expensive phase and may need A100 sessions that have not yet been purchased.

This is not a reason to cut controls — cutting Control B or writing the prereg after the run destroys the thing that makes the paper worth submitting (collab guide §3, rows 4 and 11). It is a reason to make an **explicit, logged scope decision now** rather than discovering the constraint at day 25. Options, to be decided by Stew, not by drift:

1. **Full MVP.** Phases 0–3 compressed. Requires Phase 0 to close within roughly the next 7–10 days.
2. **Phase 0 as the paper.** A rigorous Control A replication attempt on an open model — with pass/partial/fail per finding and effect magnitudes — is itself a contribution the CFP explicitly invites (§3.2). The R-space test becomes the stated future work. This is a *smaller* claim, not a weaker one.
3. **Defer the venue.** Target a later workshop or the main-track Negative Results type (§7). The work is non-archival-safe either way.

**Recommendation: treat this as a decision gate.** It is not one of G0–G5. Propose adding **G-V (venue/scope gate)**, resolved before any further compute spend. See §8.

---

## 3. Binding requirements

### 3.1 Format and length — the constraint that reshapes the paper

- **Up to 5 pages of main text.** References and appendices are excluded, but the main text must stand alone; reviewers are not obliged to read appendices.
- NeurIPS 2026 workshop LaTeX template, single PDF, English.
- Camera-ready gets one extra main-text page (six total).

**Why this is a genuine problem for this project, not a formatting detail.** The guide (§6) requires that all nine honesty-checklist items appear "explicitly and prominently in the text," and the proposal requires H1 and H2 reported as separate results with separate figures, the full sweep curve regardless of shape, matched random baselines at every *k*, Control A, Control B, and an explicit null diagnosis written against four evidence sources. Plus a mandatory responsible-use statement (§3.4). In five self-contained pages.

**Resolution — proposed, for Stew's decision:**
- The nine honesty items are not nine paragraphs. Items 1, 2, 3, 6 compress into a single "Scope and what is not tested" paragraph in the introduction. Items 4, 8, 9 are discharged by the *structure* of the results section rather than by prose about the structure. Items 5 and 7 belong to the discussion.
- Figures do the separation work: one figure for H1 (candidate vs. matched random distribution), one for H2 (impact vs. *k*, full curve). Two figures, two claims, no composite.
- Control A detail, the full per-*k* baseline tables, prereg text, and amendments go to the appendix — but the main text must state that Control A passed/partially passed/failed and at what magnitude, because a reviewer who reads only the main text must still be able to judge whether the null is diagnosable.
- **Do not** solve the page limit by dropping a control from the reported record. Moving a control to the appendix is a formatting decision; omitting it is a scientific one.

### 3.2 Negative results are explicitly welcome

The CFP states that failure cases and negative results are welcome, and specifically invites careful studies of unsuccessful methods, misleading interpretations, failed validation, and practical limits on when interpretability can support reliable discovery.

This is the strongest external validation the project's design has received. Proposal §6's position — that a properly diagnosed null is more useful than an under-controlled positive — is not a fallback rationalisation at this venue; it is a stated call. It should be reflected in the paper's framing, and it removes any remaining pressure toward collab guide §3 row 9 ("make this null sound stronger").

It also raises the bar. A venue that invites negative results will review them as results, and the reviewers are being asked to weigh reproducibility and code availability specifically (§3.6). An undiagnosed null will not clear that bar.

### 3.3 LLM and agent use — the item with the most exposure here

**Inheritance path.** The Workshops Guidance adopts the Main Track Handbook's LLM policy for proposals and states plainly that hallucinated content is not permitted. The Interp4Discovery CFP does not restate an LLM policy. Treat the Handbook policy as the applicable standard; it is the conservative read and it is what a reviewer will have in mind.

**What the Handbook requires of authors:**
- Disclose agent/LLM use in the experimental setup **if it is an important, original, or non-standard component of the method**. Spell-checking, editing help, and basic code assistance need not be disclosed.
- Authors are responsible for all content — text, figures, and references. Hallucinated citations are named specifically as a Code of Conduct violation.
- LLMs and agents cannot be authors.
- Prompt injection and other attempts to manipulate review are prohibited.

**Assessment for this project.** Claude is a development tool here, not part of the method — the method is J-lens plus an ablation harness. Under a strict reading, no disclosure is required. But given the volume of Claude-drafted material (harness across three modules, decision records, prereg drafts, this document), the defensible move is a one-line acknowledgment in the paper: an AI assistant was used for code drafting and document preparation, all outputs were verified by the author, and the assistant is not an author. Cost: one line. Benefit: it forecloses the question entirely.

**The real risk is not disclosure — it is citations.** Every reference in the paper must be verified against the primary source before submission. The project already has the right instinct here: the NeurIPS workshop guide in this repo flags ten acronyms as unverified rather than inventing expansions. Extend that discipline to the bibliography as a hard pre-submission step (§9).

**This reinforces collab guide §3 row 10.** Claude producing a plausible-looking number it does not have is, in this context, not merely a project-discipline violation — it is a route to a Code of Conduct finding.

### 3.4 Responsible-use statement — mandatory, and currently missing from the plan

The CFP requires every submission to include a short statement of potential societal impacts and suggested mitigations, and states that a missing statement is grounds for desk rejection.

**This is not in the proposal's §9 honesty checklist and not in the guide's §6 pre-submission list.** It is the single clearest compliance gap in the current documents.

It is also not a formality for this project specifically. Draft content to develop:

- **Dual use.** A method that reliably locates a small, causally load-bearing subspace controlling a recommender's future output is, symmetrically, a method for *targeting* that subspace. The auditing framing (proposal Stage 1) and an engagement-optimisation framing use the same finding. Name this directly rather than letting a reviewer find it.
- **Overclaim risk as societal impact.** The proposal's own core concern — that "we can audit recommenders for hidden objectives" would be an unearned claim — is itself a societal-impact issue, because such a claim could be cited in policy contexts it cannot support. The guide §6 framing point (nobody outside these companies can inspect production systems; this was tested on an open architecture of the same class) belongs in this statement as well as the introduction.
- **Data.** See §3.5.
- **Mitigation.** The staged claims structure, the gating of Stage 1 on both 0a and 0b, and the explicit exclusion of verbalizability *are* the mitigations. Say so.

**Budget.** Assume it consumes main-text space. Confirm with the organizers whether it may sit in an appendix; the CFP does not say. Contact: `interp4discovery@gmail.com`.

### 3.5 Data and ethics

Inherited from the NeurIPS Code of Ethics, which applies program-wide. Relevant items for the datasets in proposal §7:

| Requirement | Action | Phase |
|---|---|---|
| Confirm datasets are not deprecated | Check the NeurIPS deprecated-datasets list before committing to MovieLens-1M / Amazon Reviews 2023 / Steam | Phase 1 |
| Respect dataset licences | MovieLens carries GroupLens usage terms (citation required, redistribution restricted). Verify Amazon Reviews 2023 and Steam terms. Record each licence in the repo | Phase 1 |
| Minimise PII exposure | Amazon Reviews contains real review text and reviewer identifiers. If any raw text appears in a figure or appendix, it needs a considered justification | Phases 1, 5 |
| Substantiate representativeness claims | Do not describe a category subset as representative of user preference generally | Writing |
| Model licence | Confirm the Phase 0 model's licence permits research use and publication of results. Same for Anthropic's released J-lens code — record its licence in the repo | Phase 0 |

None of these are expected to block anything. All are cheap now and expensive at day 30.

### 3.6 Anonymity and reproducibility

**Double-blind.** The CFP is specific: strip names, affiliations, acknowledgments; cite own prior work in the third person; and search the manuscript for the GitHub and Hugging Face usernames of all contributors before submitting.

**Code and data.** Authors are strongly encouraged to open-source code, models, prompts, and data, and **reviewers are explicitly asked to weigh reproducibility and code availability**. Recommended anonymisation routes: `anonymous.4open.science` for repositories, an anonymous Hugging Face account for large artifacts.

**Assessment.** This is the project's strongest position. Seeded random-subspace draws, per-run config snapshots, git commit hashes written into output directories, pinned dependencies, pre-registration, and an append-only lab log exceed what the venue asks for. The only gap is *delivery*: the repo is private, and an anonymised public mirror has to be prepared, not assumed.

**Action.** Plan the anonymised release as a task with real hours attached, not as a submission-day step. The lab log and `amendments.md` are strong evidence for a null result — decide deliberately whether they go in the anonymised release. Recommendation: yes, and say so in the paper.

### 3.7 Eligibility, archival status, and what this does not cost you

- Non-archival. Workshop acceptance does not block later archival publication — stated on the CFP, and consistent with the Handbook, which permits main-track submission of work presented at non-archival workshops and treats non-archival dual submission as allowed.
- Prior non-archival work is welcome; work under review elsewhere is welcome.
- Work already accepted at an **archival** venue is not accepted (except NeurIPS 2026 fast-track).
- **Attendance is encouraged but not required.** This removes Atlanta travel as a gating cost — a materially different rule from the main track, where in-person presentation is required.

**Implication.** Submitting here is close to free in option-value terms. It does not consume the work.

### 3.8 Conflicts of interest

Workshop organizers and those with personal conflicts with them cannot submit. Listed organizers: Xiaoyan Bai (UChicago), Yonatan Belinkov (Technion), Ekdeep Singh Lubana (Goodfire AI), Yaniv Nikankin (Technion), Chenhao Tan (UChicago), Amirtha Varshini A S (Montai Therapeutics). Sponsor: Goodfire.

Confirm no advisor/advisee, co-authorship within three years, or shared-institution relationship. Expected to be clear; log the confirmation.

### 3.9 OpenReview account — highest-urgency item

Submission is through OpenReview. The CFP flags **twice** that account approval without an institutional email can take up to two weeks, and asks authors to register early. The Handbook adds that profiles must be current, since they drive conflict detection.

**If this account does not exist yet, create it today.** Two weeks of a 32-day runway is not a margin that can be recovered.

---

## 4. Compliance ledger

Same format as the guide's §3 nuance ledger. Check at every gate.

| # | Requirement | Source | Enforced in | Verification check | Status |
|---|---|---|---|---|---|
| C1 | OpenReview account active, profile current | CFP; Handbook | Now | Account exists and is approved | **Open — urgent** |
| C2 | ≤5 pages main text, NeurIPS 2026 workshop template, self-contained | CFP | Writing | Compiled PDF measured, not estimated | Open |
| C3 | Responsible-use statement present | CFP | Writing | Statement drafted; desk-reject risk if absent | **Open — gap in current docs** |
| C4 | Full anonymisation incl. GitHub/HF username sweep | CFP | Writing | Text search run on the final PDF | Open |
| C5 | Anonymised code release prepared | CFP | Writing | Anonymous mirror live and reachable before submission | Open |
| C6 | Every citation verified against primary source | Handbook LLM policy | Writing | One-by-one check; no reference enters from recall | Open |
| C7 | AI-assistance acknowledgment line | Handbook LLM policy | Writing | One line present | Open |
| C8 | Dataset licences and deprecation status recorded | Code of Ethics | Phase 1 | Licence file per dataset in repo | Open |
| C9 | Model and J-lens code licences recorded | Code of Ethics | Phase 0 | Licences noted in the model-selection decision record | Open |
| C10 | Compute resources reported | Code of Ethics (reproducibility) | Writing | Hardware and approximate GPU-hours stated | Open |
| C11 | No archival prior publication of this work | CFP | Now | Trivially satisfied; confirm and log | Open |
| C12 | COI with organizers checked | Workshops Guidance | Now | Confirmation logged | Open |
| C13 | CFP re-fetched before submission | CFP (self-declared provisional) | ~Aug 20 | Diff against this document | Open |

---

## 5. Assessment of work to date

Measured against venue requirements, not against the plan.

**Where the project is ahead of what the venue asks.**

- Reproducibility discipline exceeds the standard. Seeded draws, config snapshots, commit hashes, pinned dependencies, append-only log. The venue asks reviewers to weigh reproducibility; this is a differentiator, provided it is actually shipped (C5).
- Pre-registration is not required by the venue and is uncommon at workshops. For a null result at a venue that invites nulls, it is close to decisive.
- The verification instinct is already correct. The repo's NeurIPS workshop guide flags ten acronyms as unverified rather than filling gaps — exactly the behaviour that keeps §3.3 from becoming a problem.
- Self-corrections are logged rather than silently edited (the Control A protocol reversal; the single-token constraint revision). This is the habit that makes an appendix credible.
- Phase 0 substance is real: 21/21 tests on the cloned repo, three open questions resolved from primary text rather than inference, appendices read directly, a full harness with 15/15 synthetic tests, two tokenization landmines caught before they cost a GPU session.

**Where the gaps are.**

1. **C1, OpenReview.** No record of an account. Up-to-two-week approval risk on a 32-day runway. Fix today.
2. **C3, responsible-use statement.** Mandatory, desk-reject-carrying, absent from the proposal's §9 checklist and the guide's §6 list. Proposed remedy in §6 below.
3. **The five-page limit is unbudgeted.** The current writing plan implicitly assumes more room than exists. This needs an explicit page-budget decision before drafting, not during.
4. **The 32-day schedule against an incomplete Phase 0.** Named in §2. Needs a logged decision, not optimism.
5. **The lab log in the reference copy contains only the Session 01 template, with placeholders unfilled.** Sessions have clearly been worked since. Either the working copy has diverged from the reference copy, or entries were not written. The first is a sync problem; the second is a real evidentiary gap, because the diagnosis of a null (proposal 4.4) rests on the record of what was tried. **Verify which it is.** If entries are missing, reconstruct them now, dated as reconstructions — a reconstruction acknowledged as such is admissible; a backfilled entry presented as contemporaneous is not.
6. **Dataset and model licences unrecorded** (C8, C9). Cheap now.
7. **No compute reporting plan** (C10).

**One thing that is not a gap but reads like one.** The proposal describes the J-space result as roughly a month old and single-lab. That framing was written earlier; it is now some months old and there is an in-progress open-model replication. Update the wording to the state of the literature at submission rather than repeating the design-time phrasing — reviewers will know the current status, and stale framing reads as inattention rather than as caution.

---

## 6. Proposed amendments to the existing documents

These are proposals. Per the collab guide's division of labour, the decision is Stew's.

**To the proposal, §9 (honesty checklist) — add three items:**

> 10. A responsible-use statement covering dual-use implications, overclaim risk, and data provenance is included, per the venue requirement.
> 11. AI assistance used in code drafting and document preparation is acknowledged; all content, including every reference, was verified by the author.
> 12. Compute resources used are reported, and the anonymised code and log release is linked.

**To the guide, §6 (writing) — add:** a page budget, fixed before drafting, allocating the five main-text pages across introduction and scope, method, H1, H2, null diagnosis, and responsible use. Anything that does not fit goes to the appendix, and the main text says explicitly that it did.

**To the guide, §5 (decision gates) — add G-V:** *Given the confirmed deadline and current phase state, which scope are we submitting?* Resolved before further compute spend. Options in §2.

**To the collab guide, §3 (risky request patterns) — add row 13:**

> | 13 | "We're at the page limit — can we drop the random-baseline table / Control B mention?" | Trims a control out of the reported record under formatting pressure. This is proposal 4.8 and 4.4 lost to layout | Move it to the appendix and state in the main text that it exists and where. Never remove it from the record. Flag that the request arrived as a formatting question and is a claims question |

---

## 7. Plan B, if the deadline is not met

Non-archival status means nothing is consumed by missing this venue or by submitting to it.

- **NeurIPS 2026 main track, Negative Results contribution type.** The Handbook formally recognises a contribution type whose main contribution is understanding a negative result, and states the bar is high. A pre-registered, doubly-controlled null with a diagnosis written against Control A, Control B, the nonlinear probe, and the Phase 1 difficulty gradient is built for exactly that bar. Note the main track is archival, double-blind, nine pages, and requires in-person presentation.
- **Later workshop cycles.** ICLR and ICML workshop rounds follow.
- **Preprint.** Permitted alongside submission; the Handbook allows non-anonymous preprints and warns only against aggressive promotion of work under review. Check the workshop's own stance before posting.

The point of naming these now is that they should not be reached for at day 28 as a rationalisation for cutting a control.

---

## 8. Immediate actions, in order

1. **Create or verify the OpenReview account today.** (C1)
2. **Log gate G-V.** Decide the submission scope against the 32-day runway and record the rationale. Do not let this resolve implicitly.
3. **Reconcile the lab log** reference copy against the working copy. If entries are missing, reconstruct and label them as reconstructions. (§5, gap 5)
4. **Draft the responsible-use statement** now, while Phase 0 compute runs. It does not depend on results. (C3)
5. **Fix the page budget** before any drafting begins. (C2)
6. **Record licences** for the Phase 0 model and the J-lens code in the model-selection decision record. (C9)
7. **Re-fetch the CFP around August 20** and diff it against §3 of this document. (C13)

---

## 9. Pre-submission compliance checklist

Run alongside the guide's §6 nine-item honesty checklist. Both must pass.

- [ ] OpenReview account approved and profile current
- [ ] PDF compiles in the NeurIPS 2026 workshop template; main text measured at ≤5 pages
- [ ] Main text is self-contained — a reviewer who reads no appendix can still judge whether the null is diagnosable
- [ ] Responsible-use statement present, covering dual use, overclaim risk, and data provenance
- [ ] Every author name, affiliation, acknowledgment removed; own prior work cited in the third person
- [ ] Manuscript and supplement searched for GitHub and Hugging Face usernames of all contributors
- [ ] Anonymised code mirror live, reachable, and free of identifying metadata
- [ ] Every reference opened and verified against its primary source
- [ ] AI-assistance acknowledgment line present
- [ ] Dataset licences and deprecation status confirmed and cited
- [ ] Compute resources and approximate GPU-hours reported
- [ ] COI with the listed organizers confirmed absent
- [ ] CFP re-fetched within the last 10 days and diffed against this document
- [ ] Every ablation figure carries its matched random-draw distribution (proposal 4.8 — survived the page cut)
- [ ] H1 and H2 appear as separate results with separate figures (proposal 4.3 — survived the page cut)

---

## 10. Sign-off

**Prepared by:** Claude, from primary sources retrieved 2026-07-28.
**Decision-maker:** Stew. Every proposed amendment in §6 and every scope option in §2 requires explicit sign-off before it takes effect.
**Status:** [ ] reviewed  [ ] signed off  [ ] amendments adopted
**Date signed off:** ____________

**Standing caveat.** The Interp4Discovery CFP labels its own submission requirements provisional and reserves the right to change them. This document is accurate to 2026-07-28 and must be re-verified before submission (C13).
