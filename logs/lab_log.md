# Lab Log — R-Space Generalization Test

**Repo location:** `logs/lab_log.md`
**Governed by:** `EXECUTION_GUIDE.md` §2.3
**Rule: append-only.** Entries are added at the bottom. Nothing above is edited after the fact. If something was wrong, a later entry corrects it — the wrong version stays.

---

## How to use this file

**Every work session gets an entry.** Including sessions where nothing worked, the run crashed, or the result was null. The diagnosis of a null (proposal 4.4) depends on knowing what was tried and what was ruled out, and a log that only contains successes cannot support that.

**The three questions (guide §0) are mandatory.** They are the drift detector. Answering them honestly is the point; answering them by rote is not.

**Decision gates get their own entries.** Use the gate template at the bottom. Guide §5 requires the decision *and its rationale* to be logged at each of G0–G5.

**Amendments do not go here.** Deviations from a pre-registration go in `preregistration/amendments.md`, timestamped and justified. Reference the amendment from the log entry.

---

## Entry template

Copy this block for each session.

```markdown
## [YYYY-MM-DD] Session NN — <short description>

**Phase:** <0 / 1 / 2 / 3 / 4 / 5 / 6 / writing>
**Read-first sections re-read today:** <list them, or "no — session was X" and say why>
**Hardware:** <local CPU / Colab T4 / Colab A100 / Kaggle P100> · **CU spent:** <n/a or approx>

### What was run
- **Script / notebook:**
- **Config:** `configs/<file>` · **snapshot written to:** `results/raw/<dir>/`
- **Git commit:**
- **Seeds:** model load ___ · random-subspace draws ___ · task sampling ___ · data shuffle ___
- **Runtime:**

### Result
<Raw outcome only. Numbers, error messages, what the run produced. No interpretation in this
subsection — interpretation goes below, clearly separated.>

### Reading of the result
<What this appears to show, and — explicitly — what it does not show. Name which hypothesis it
bears on. If it bears on none, say so.>

### The three questions
1. **Which claim does today's work support?** <H1 / H2 / H3 / none — infrastructure>
2. **Did I import any property of J-space by assumption today?** <Check specifically: did any code,
   comment, plot label, or note treat the R-space as small, verbalizable, or legible without having
   measured it? Proposal 4.1, 4.3, 4.7>
3. **Would this step still be defensible if the final result is null?** <If it only makes sense
   assuming a positive result, that is a design leak — name it>

### Deviations
<Any departure from the prereg or the plan. Cross-reference the `amendments.md` entry. "None" is a
valid answer but should be a considered one.>

### Next step
<One concrete action. Plus any decision left open.>
```

---

## Broken-run template

Shorter form for runs that crashed, were aborted, or produced nothing usable. **These still get logged** — guide §2.3.

```markdown
## [YYYY-MM-DD] Session NN — ABORTED: <short description>

**Phase:** · **Hardware:** · **Git commit:**
**What was attempted:**
**How it failed:** <error, OOM, session preempted, wrong output shape, etc.>
**Diagnosis / suspected cause:**
**Ruled out:** <what this failure lets you eliminate — often the useful part>
**Next step:**
```

---

## Decision gate template

Use at G0–G5 (guide §5). One entry per gate, even when the answer is an easy yes.

```markdown
## [YYYY-MM-DD] GATE <G0–G5>

**Gate question:** <quote it from guide §5>
**Evidence considered:** <point at specific log entries, result files, figures>
**Decision:** <go / no-go / modified scope>
**Rationale:** <why — this is the part that matters in three weeks>
**Consequence for scope:** <what is now in or out of scope as a result>
**Deadline check:** <days to ~Aug 29 AoE; is the minimum viable paper (proposal §6) still reachable>
```

---

## Reference — the gates

| Gate | When | Question | If no |
|---|---|---|---|
| **G0** | After Phase 0 | Did Control A pass well enough to trust the instrument? | Reassess — the paper may become a replication-difficulty report. Decide explicitly |
| **G1** | After Phase 1 | Is there a real easy/hard difficulty gradient in base model performance? | Redesign hard tasks. Phase 4 is uninterpretable without it |
| **G2** | Before Phase 3 | Is `prereg_phase3.md` committed, and were tasks frozen before results were seen? | Do not run. Fix the ordering first |
| **G3** | After Phase 3 | Is there enough for the minimum viable paper (proposal §6)? | Stop and write. A clean Phase 0–3 result beats a rushed Phase 4 |
| **G4** | After Phase 3 | Time for Phase 4 without compromising the Phase 3 write-up? | Skip Phase 4; note as future work |
| **G5** | After Phase 4 | Did both 0a and 0b pass? | Phase 5 stretch / Phase 6 out of scope. State as future work |

---

## Entries

<!-- Append below. Newest at the bottom. Do not edit entries above this line. -->

## [YYYY-MM-DD] Session 01 — Project setup

**Phase:** pre-0 (infrastructure)
**Read-first sections re-read today:** guide §0, §1, §2 — establishing standing rules before any work
**Hardware:** local CPU · **CU spent:** n/a

### What was run
- **Script / notebook:** none — repository scaffolding
- **Config:** n/a
- **Git commit:** <fill in>
- **Seeds:** n/a
- **Runtime:** n/a

### Result
Repository structure created per guide §1.1. Read-only reference copies of the proposal, execution
guide, and AI collaboration guide placed in `proposal/`. Dependency pinning strategy decided:
<fill in>.

### Reading of the result
Infrastructure only. Bears on no hypothesis.

### The three questions
1. **Which claim does today's work support?** None — infrastructure.
2. **Did I import any property of J-space by assumption today?** No — no analysis performed. Terminology
   discipline (guide §2.1) recorded in the repo README so it applies from the first line of code.
3. **Would this step still be defensible if the final result is null?** Yes — setup is claim-neutral.

### Deviations
None.

### Next step
Phase 0, step 1: obtain Anthropic's released J-lens code and read its actual API and assumptions —
specifically where it hardcodes vocabulary structure, tokeniser, or architecture, since those are the
Phase 2 adapter points. Free-tier Colab is sufficient for this step; no GPU purchase yet.

<!-- ^ This first entry is a worked example of the format. Replace or extend it with real content. -->

---

## [2026-08-05] Session 17 — Literature review: scope set, Cluster A/B/E opened, one correction

**Phase:** Writing track / Phase 1 preparation. Not an experimental phase.
**Read-first sections re-read today:** `AI_COLLABORATION_GUIDE.md` §2 (division of
labour), §3 (risky request patterns, rows 10 and 12), §4.1 (standing loop);
`COMPLIANCE_GUIDE.md` §3.3 (LLM policy, citations), C6; proposal §9 item 1.
**Hardware:** Claude sandbox, no GPU · **CU spent:** none

---

### What was run

- **Script / notebook:** none. Literature session.
- **Tools:** four `web_search` calls, two `web_fetch` calls, all run by Claude
  under `lit/DECISION_lit_review_scope.md` D2 (amendment permitting Claude to
  search and supply links; Stew retains all citation decisions).
- **Artifacts created:** `LIT_REVIEW_PLAN.md`, `lit/DECISION_lit_review_scope.md`,
  `lit/searches_log.md`, `lit/candidates.md`, `lit/claim_ledger.md` (empty
  structure).
- **Git commit:** `779c147`
- **Seeds / config / runtime:** n/a.

**Bookkeeping error to fix before commit.** `DECISION_lit_review_scope.md` and
`searches_log.md` were written today but carry the date **2026-08-04**. Correct to
2026-08-05 in both. Recorded here rather than fixed silently.

---

### Result

**Five scope decisions taken** (recorded in `lit/DECISION_lit_review_scope.md`,
awaiting signature): `LIT_REVIEW_PROTOCOL.md` superseded; Claude may search and
supply links but no citation may enter from recall; deep-read budget fixed at 10;
Pass 3 checkpoint informal; cluster order set to A → B → E → C → D → G, i.e.
framing before Phase-1 unblocking, with C(1–2) and G carved out as triage-tier
lookups that do not consume deep-read budget.

**Cluster B — primary source retrieved and read.** The external review of the
J-space paper (Nanda, published 6 July 2026 on LessWrong, written at Anthropic's
request as one of three solicited external commentaries). Contents relevant here:

- Overall assessment positive on the scientific and methodological claims.
- Contains an independent replication on Qwen 3.6 27B, with named collaborators.
  Reported as replicating: verbal report (weak but positive), CKA band structure
  (less clean than the paper's; four to five bands), directed modulation
  (moderate), multilingual (probing and causal), typo, association.
- Reported as **not** replicating: poetry and arithmetic. Attributed by the
  reviewer to plausible experimenter error or weaker model capability.
- Multi-hop factual recall: swapping the answer strictly dominated swapping the
  intermediate. Attributed by the reviewer to the dataset not being hard enough,
  with intermediate and answer terms linearly related.
- Replication recipe stated: Jacobians to the **penultimate layer**, n=25 prompts
  of 128 tokens from the Pile, **first four tokens skipped** due to high norm.
  Notes n=10 nearly as good and n=1 respectable.
- Reviewer's own expectation, stated as a prediction rather than a measurement:
  J-Lens will have many false positives; better as hypothesis generation than
  hypothesis validation; would like reliability data collected.
- Reviewer notes that ablation removes only a fraction of a concept and that
  vector error is magnified under causal intervention relative to observation.
- Reviewer repeatedly names the single-token vocabulary constraint as the method's
  main limitation and multi-token extensions as a priority direction.

**Cluster A — five candidates triaged, none read.** Logged in `candidates.md`.
Two promoted to deep read on the basis of snippets only.

**Cluster E — a named adverse methodological lineage located.** Multiple 2026
papers cite a common set of prior work arguing that ablation-baseline choice
changes which components appear causally important, and recommending resample
over zero ablation. One published proceedings source retrieved directly; four
others are so far only names appearing inside other papers' related-work
sections and have not been retrieved.

**Clusters C, D, F, G: zero queries run.** No absence claim is available for any
of them.

---

### Reading of the result

**Correction — this is the main entry of the session.**

Earlier in this session Claude retrieved a third-party replication repository
(`tao-hpu/jspace-replication`) whose README characterises the external review as
finding that rhyme-planning and mental-arithmetic failed to replicate, that the
multi-hop probe-swap effect was weak, and that the J-lens produces many false
positives. Claude relayed that characterisation to Stew **and drew a conclusion
from it** — that the review would make the project's Control A criterion-4 failure
look corroborative rather than anomalous.

On reading the review itself, that characterisation is misleading. The review's
overall assessment is positive; the core replication succeeded; the two failed
experiments are attributed by the reviewer to his own setup rather than to the
paper; and the false-positive statement is the reviewer's prediction about the
technique's practical use, not a measurement. **The conclusion Claude drew does
not survive. Control A's criterion-4 failure is not corroborated by this
document.**

The failure mode is `AI_COLLABORATION_GUIDE.md` §3 row 10 in a form the table does
not name: not a fabricated number, but a second-hand characterisation of a primary
source, relayed with insufficient marking and then reasoned from. The existing
rule ("only analyse numbers actually pasted from `results/raw/`") has an analogue
that was not written down: **do not reason from a summary of a source that has not
been opened.** Proposed as a new row for §3 — see Next step.

**What the review does support, stated only as far as the document goes.**

1. Proposal §9 item 1's clause "not yet independently replicated even within its
   original domain" is **false** as of this date and must be removed. The rest of
   the item (single-lab, one text-only model) appears to stand.
2. Two Phase 0 deviations logged as open now have external corroboration. Session
   07 recorded that the released code defaults to the final layer while the paper
   specifies penultimate, and the deviation was documented rather than corrected.
   The reviewer's replication used penultimate. Separately,
   `Phase1_HANDOFF.md` §5 flagged `skip_first=16` as the highest-risk inherited
   default; the reviewer's replication used 4. Neither is a result about our data,
   but both reduce the space of live alternative explanations for our lens recipe.
3. G0's statement that the near-ceiling precondition is not reachable with
   affordable open models is consistent with the reviewer encountering a
   dataset-difficulty confound at 27B. This is corroboration of a *bound*, not of
   a result.
4. The single-token constraint that forces our template-lens fallback
   (`Phase1_HANDOFF.md` §4) is named in the review as the method's principal
   limitation. This bears on framing, not on evidence.
5. The reviewer's note that vector error is magnified under causal intervention is
   adverse to H1 as we currently intend to measure it, and converges with the
   Cluster E lineage found independently in query L01-3.

**What today's work does not show.** Nothing about R-space. No literature finding
is evidence for or against H1, H2 or H3, and none of the above changes what the
Phase 3 data will say. Items 2 and 3 narrow alternative explanations; they do not
supply evidence.

---

### The three questions

1. **Which claim does today's work support?** None — infrastructure and framing.
   No row of the claim ledger was populated; the ledger remains empty by design,
   since nothing has been read at primary source except the Cluster B review.
2. **Did I import any property of J-space by assumption today?** Not into the
   design. But the correction above is a related failure: a property of the
   *literature* — that the source result was unreplicated — was carried forward
   unexamined from the design-time proposal, and a second-hand claim about the
   literature was reasoned from without verification. The discipline that applies
   to J-space's properties applies to claims about the field.
3. **Would this step still be defensible if the final result is null?** Yes.
   Cluster E and the null-diagnosis material are more valuable under a null than
   under a positive, and the §9 correction is required either way.

---

### Deviations

**One amendment taken:** `lit/DECISION_lit_review_scope.md` D2 relaxes the prior
rule that Claude proposes questions only. Claude may now run searches and supply
links. The prohibition on citations from recall is unchanged and was restated in
the decision record. The rule proved necessary within the same session — see the
correction above.

---

### Next step

Rewrite proposal §9 item 1 and the matching line in `EXECUTION_GUIDE.md` §6.
Draft in progress.

**Decisions left open:**

- Whether to add a row to `AI_COLLABORATION_GUIDE.md` §3: *"Summarise what this
  paper found" where the paper has not been opened* → Claude states clearly that
  it is relaying a second-hand characterisation, and does not reason from it.
- Whether to add the removed-component **norm** measurement to `prereg_phase3.md`
  (candidate and random draws, every k) before signature. Raised by the Cluster E
  material. Cheap now, an amendment later.
- Whether the null-diagnosis evidence list should be extended beyond its current
  four sources to include self-repair as a fifth alternative explanation for a
  small measured effect (candidate A-04, not yet read).
- Whether the third-party replication repository is citable at all. Its README
  mischaracterised a primary source that is one click away. That is a reason for
  caution about the rest of it.

  ---

## [2026-08-05] Session 18 — Repository audit: provenance gap in Phase 0 results

**Phase:** Writing track / infrastructure. Not an experimental phase.
**Read-first sections re-read today:** `AI_COLLABORATION_GUIDE.md` §1.1
(repository structure), §1.2 (config snapshot and commit hash per run);
`COMPLIANCE_GUIDE.md` §3.6 (reproducibility), C5.
**Hardware:** local · **CU spent:** none

---

### What was run

- **Script / notebook:** none. Repository audit.
- **Method:** the public repository was cloned and inspected; result files were
  checked for the `git_commit` field; the upstream `anthropics/jacobian-lens`
  history was cloned in full to establish which commit Phase 0 used.
- **Git commit:** `83090c2`

---

### Result

**1. Every Phase 0 result carries `git_commit: "UNKNOWN"`.** Checked across the
Control A sweep (per-condition files and `clean.json`), the Qwen3-8B headroom
summary, and the Qwen3.5-4B headroom summary. `band_stats.json` and Control A's
`_summary.json` have no such field at all.

**2. The cause is a silent failure, not a missing feature.** Three separate
implementations — `src/ablation/sweep.py`, `scripts/run_control_a.py`,
`scripts/headroom_check.py` — each call `git rev-parse HEAD` in the current
working directory and fall back to a placeholder string on failure. Under Colab
the working directory is not a git checkout, so the call failed every time and
the placeholder was written. Nothing surfaced the failure.

**3. The upstream clone was unpinned.** Phase 0 notebooks used
`git clone -q --depth 1 https://github.com/anthropics/jacobian-lens.git`, which
records no commit.

**4. The upstream commit is nonetheless known.** As of 2026-08-05 the upstream
repository contains exactly one commit:
`581d398613e5602a5af361e1c34d3a92ea82ba8e`, 2026-07-02, "Initial release".
Every Phase 0 clone necessarily obtained it. Recorded in
`third_party/PINNED_COMMIT.txt` and marked there as a reconstruction.

**5. The code was committed on 2026-08-05, after every run it produced.** The
repository previously contained twelve files and a single commit dated
2026-07-29. The harness, tests, scripts, and all Control A results were added
today.

**6. `COMPLIANCE_GUIDE.md` overstates the project's position on this point.**
Line 134 describes reproducibility as "the project's strongest position," listing
"git commit hashes written into output directories" and "pinned dependencies."
Line 189 repeats both as a reviewer-facing differentiator. Neither held.

---

### Reading of the result

The correspondence between the code now in the repository and the results now in
the repository is **asserted by the author and not verifiable from git history.**
No commit predating the runs contains the code, and the results do not name a
commit. This is a genuine limitation of the Phase 0 record and it is stated here
rather than papered over.

What is *not* affected: the results themselves, the pre-registration, the seeded
random draws, and the append-only log of what was decided when. The Control A
pre-registration exists as a file dated 2026-07-28, and — more importantly — it
contains a criterion the data failed, which is the strongest available evidence
that it was not written to fit the outcome. Provenance of the *code* is weaker
than the record implies; provenance of the *decisions* is intact.

**Finding 6 is the one that needed catching.** A compliance document claiming a
strength the artifacts do not support is precisely the unearned positive claim
the project's governance exists to prevent, and it survived several reviews of
that document because nobody checked the claim against the output files. The
lesson generalises: assertions in the compliance ledger about what the artifacts
contain should be verified against the artifacts, not against intent.

---

### The three questions

1. **Which claim does today's work support?** None — infrastructure. This bears
   on how Phase 0's provenance is described, not on H1, H2 or H3.
2. **Did I import any property of J-space by assumption today?** No.
3. **Would this step still be defensible if the final result is null?** Yes, and
   more so. A null whose code provenance is unverifiable is weaker than one whose
   is; recording the gap now is what makes the Phase 3 record stronger than the
   Phase 0 one.

---

### Deviations

None from a pre-registration. Three corrective actions taken or scheduled:

- `third_party/PINNED_COMMIT.txt` created, recording the upstream commit and
  labelling it a reconstruction.
- `src/provenance.py` added: resolves the commit relative to the source file
  rather than the working directory, and **raises rather than returning a
  placeholder** when the commit cannot be established.
- `COMPLIANCE_GUIDE.md` lines 134 and 189 to be corrected — see next step.

---

### Next step

1. Replace the three `git_commit()` implementations with `src/provenance.py`.
   Verify by running any script and confirming a real hash appears in the output.
2. Correct `COMPLIANCE_GUIDE.md` lines 134 and 189 so the reproducibility claim
   matches the artifacts: seeded draws, pre-registration and the append-only log
   hold; commit hashes and pinned dependencies hold from Phase 1 onward, not for
   Phase 0.
3. Add one sentence to the paper's limitations covering Phase 0 code provenance.

---

## [2026-08-05] Session 19 — Repository made public; C4/C5 consequences

**Phase:** Writing track / infrastructure. Not an experimental phase.
**Read-first sections re-read today:** `COMPLIANCE_GUIDE.md` C4 (anonymisation,
including GitHub and Hugging Face username sweep), C5 (anonymised code release),
§3.6 (reproducibility and code availability); `AI_COLLABORATION_GUIDE.md` §1.1.
**Hardware:** local · **CU spent:** none

---

### What was run

- **Script / notebook:** none. Repository administration.
- **Action:** `github.com/hppddub/J-space-and-recommender-models` changed from
  private to public.
- **Reason:** to allow the AI assistant to clone and audit the repository during
  the Session 17–18 cleanup. It could not be inspected while private.
- **Git commit:** `multiple between August 7 and 8, 2026`

---

### Result

The repository is public at an account and repository name that both identify
the project and its author. It now contains the full Phase 0 record: harness,
tests, Control A results, pre-registrations, decision records, and the lab log.

`COMPLIANCE_GUIDE.md` previously described the delivery gap as "the repo is
private, and an anonymised public mirror has to be prepared, not assumed." That
sentence was written when the repository was private and has been revised.

---

### Reading of the result

**The visibility change did not close the C5 gap. It changed its shape and
raised its urgency.**

C5 requires an *anonymised* code release reachable at review time. A public
repository is not an anonymised one. Three specific consequences:

1. **The repository name describes the project.** A reviewer who searches the
   paper's subject matter can plausibly find it, and the account name is
   identifying. This is a soft de-anonymisation route that did not exist while
   the repository was private.

2. **The content is now identifying in more ways than the name.** The lab log
   names the author in places, the commit history carries an authored account,
   and decision records are signed. An anonymised mirror is therefore a genuine
   scrub, not a rename — commit history included.

3. **C4's username sweep now has a live target.** Any occurrence of the account
   name inside committed files, notebook outputs, or paths has to be found and
   removed before the mirror is published.

**What did not change.** Double-blind review does not prohibit public code, and
having a public repository is common and generally tolerated. The obligation is
to avoid *linking* it from the submission and to provide an anonymised route
instead. Nothing about the visibility change is a violation; it is a task that
became more urgent and slightly larger.

**Why this is logged separately from Session 18.** Session 18 concerns the
provenance of Phase 0 results — an evidentiary matter. This concerns submission
compliance. Bundling them would make the compliance consequence easy to miss
inside a longer entry about commit hashes.

---

### The three questions

1. **Which claim does today's work support?** None — infrastructure. Bears on
   submission compliance, not on H1, H2 or H3.
2. **Did I import any property of J-space by assumption today?** No.
3. **Would this step still be defensible if the final result is null?** Yes.
   A null with a published, inspectable record is more useful to the field than
   one without, provided the anonymisation obligation is met separately.

---

### Deviations

`COMPLIANCE_GUIDE.md` assessment paragraph revised: the reproducibility claim now
distinguishes what holds for Phase 0 (seeded draws, per-run configuration in
every result file, pre-registration, append-only log) from what does not (commit
hashes, pinned dependencies — corrected going into Phase 1), and the delivery gap
restated for a public repository.

---

### Next step

**Decision required — repository visibility during review.**

- **Option A: stay public.** Maximum transparency, matches the reproducibility
  framing, and lets the work be inspected. Accepts a soft de-anonymisation route.
- **Option B: revert to private after the audit, republish on acceptance.**
  Removes the route entirely. Costs nothing scientific; the anonymised mirror is
  required either way.

Not decided today. Recorded so it is a decision rather than a default.

**Scheduled work, both required before submission:**

1. Build the anonymised mirror (C5). Fresh account or Anonymous GitHub, history
   squashed or scrubbed, author name removed from log entries and decision
   records. This is more than a copy and should not be left to the final week.
2. Run the C4 username sweep across all committed files and notebook outputs,
   not just the repository name.


**Decisions left open:**

- Whether Phase 0's provenance gap warrants any change to what Control A is
  claimed to establish. Current view: no — the gap concerns which revision of the
  code ran, not whether the reported numbers came from the reported procedure.
  Recorded so the question is visible rather than assumed away.

---

## [2026-08-05] Session 20 — Perturbation-magnitude instrumentation; a test that had never run

**Phase:** Writing track / Phase 3 preparation.
**Read-first sections re-read today:** `EXECUTION_GUIDE.md` §2.4 (pre-registration
before the run it governs); `AI_COLLABORATION_GUIDE.md` §1.2; literature Cluster E
notes in `lit/candidates.md` (threat T1).
**Hardware:** Colab, CPU runtime for tests · **CU spent:** negligible

---

### What was run

- **Script / notebook:** `python -m pytest tests/ -v` on Colab, against the
  repository at the commit below.
- **Code changes:** perturbation-magnitude recording added to
  `src/ablation/harness.py`; two tests added to `tests/test_ablation.py`;
  hardcoded sandbox path removed from all four `tests/test_*.py`;
  `TinyDecoder.unembed` dtype handling corrected in `tests/tests_tiny.py`.
- **Document changes:** `preregistration/prereg_phase3_draft.md` §1 and new §3.1.
- **Git commit:** `026b869` and preceding.

---

### Result

**1. Perturbation-magnitude recording is in place.** The harness now records
`‖h − h′‖` and `‖h‖` per layer at ablated positions, for every condition, and
returns per-layer summary statistics on `AblationResult.perturbation`. Cost is
nil: the removed component was already computed in order to be zeroed.

Pre-registered in §3.1 as **report-only** — it gates no claim. Interpretation
language for each possible outcome is fixed there in advance, so a disparity
cannot be quietly omitted and a convenient result cannot be recruited.

**2. The test suite had a hardcoded path to an environment that does not exist.**
All four test files carried `sys.path.insert(0, "/home/claude/jacobian-lens")` on
line 4 — a path inside the AI assistant's sandbox. As committed, the suite could
only run there. Replaced with an optional `JLENS_PATH` environment variable,
falling back to the installed package.

**3. A GPU-only test had been silently skipped since it was written, and fails
when actually run.** `test_harness_works_with_a_bfloat16_model_on_gpu` is marked
`skipif(not torch.cuda.is_available())`. No prior test execution had a GPU, so it
had never executed. Run on Colab, it failed:
`RuntimeError: expected scalar type Float but found BFloat16`.

**4. The cause was test-double drift, not a harness fault.** The real
`HFLensModel.unembed` (`jlens/hf.py:166`) casts the residual to the lm_head's
dtype. `TinyDecoder.unembed` cast unconditionally to float32. Under a bfloat16
model, the double fed float32 into a LayerNorm holding bfloat16 parameters.
Corrected to mirror production. **56 passed** after the fix.

**5. The Phase 0 diagnostic did not run.** Two attempts to produce a working
Colab notebook failed — the first collapsed every cell to one line (missing
newline terminators in the `.ipynb` source arrays), the second still did not open
correctly for reasons not diagnosed. Deferred rather than debugged further.

---

### Reading of the result

**Finding 3 is the substantive one and it does not invalidate Control A.**
Control A ran on the real `HFLensModel`, whose dtype handling is correct, and ran
to completion. The failure is confined to the synthetic double.

What it does invalidate is an *assurance*. This test exists specifically to verify
the harness in bfloat16 on GPU — the exact configuration Control A ran in — and it
was written after the Phase 0 session in which a `prepare_lens` dtype cast broke
Stage B. It was written to guard the thing that had already broken once, and it
provided no coverage at all for its entire life. Any statement in the Phase 0
record to the effect that the bf16 path is tested was false until today.

**The pattern across Sessions 18 and 20 is the same failure mode twice.** A
mechanism that reports success when it has silently done nothing: `git_commit`
returning the string `"UNKNOWN"` on failure, and a test reporting a pass by being
skipped. Neither was caught by reading the code; both were caught by running it in
a different environment. **The general lesson: verification that can no-op quietly
is not verification.** Where feasible, such mechanisms should fail loudly —
`src/provenance.py` now raises rather than returning a placeholder, and the
suite should be run somewhere with a GPU before any claim about GPU coverage.

**Nothing today bears on H1, H2 or H3.** The instrumentation makes a future
measurement possible; it does not constitute one.

---

### The three questions

1. **Which claim does today's work support?** None — instrumentation and test
   maintenance.
2. **Did I import any property of J-space by assumption today?** No. §3.1 was
   deliberately written as report-only with no threshold, because any numeric
   cut-off chosen before recommender magnitudes exist would be arbitrary and one
   chosen afterwards would be post-hoc.
3. **Would this step still be defensible if the final result is null?** Yes.
   Perturbation magnitude is more informative under a null than under a positive:
   it distinguishes "the directions did not matter" from "the intervention barely
   fired."

---

### Deviations

`prereg_phase3_draft.md` §1 and §3.1 were edited while the document remains
**unsigned**. This is drafting, not amendment; no entry in `amendments.md` is
required. The same change after signature would require one.

---

### Next step — PARKED, to resume

**The Phase 0 perturbation diagnostic has not been run.** Everything it needs is
committed and the test suite passes. Only the notebook is missing.

To resume:

- Prefer a **plain Python script pasted into one Colab cell** over an uploaded
  `.ipynb`. Two attempts at notebook generation failed; the format is not worth
  further debugging when a script is equivalent.
- The run reproduces Control A's grid exactly: `STRENGTHS` and the seed derivation
  `BASE_SEED + 1000*d + len(layers)` from `scripts/run_control_a.py:37-79`,
  `BASE_SEED = 20260728`, bfloat16, `max_seq_len=128`. These must not be altered —
  the point is measuring what Control A did.
- Clone `jacobian-lens` with an explicit
  `git checkout 581d398613e5602a5af361e1c34d3a92ea82ba8e`, not `--depth 1`.
- **Check `clean` returns zero removed norm before reading anything else.**
- Estimated 15–30 minutes on A100.

**Prediction, recorded now and before the run:** `random_iso` removes materially
less norm than `random_lens`, which removes less than the candidate. If so, the
original paper's own control is the weaker of the two nulls and Phase 3 should
report primarily against `random_lens`. If the prediction fails and the nulls
remove comparable norm, the matched-size control was already sufficient and
threat T1 is answered outright — the better outcome, and one to state plainly
rather than bury.

**Also still open, unchanged:**

- Literature clusters C, D, F and G: zero queries run. No absence claim is
  available for any of them.
- Repository visibility decision (Session 19).
- Anonymised mirror for C5.
