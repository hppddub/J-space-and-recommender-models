# Candidate Sources — Triage

**Every row is `UNVERIFIED` until Stew opens the primary source.** Titles, IDs and
characterisations below were read out of search snippets and one page fetch by
Claude on 2026-08-04. Identifiers in particular must be checked character by
character before any of them enters a `.bib` file (C6, `DECISION_lit_review_scope.md` D2).

**Status codes:** `TRIAGE` seen in snippet only · `DEEP` promoted to the
ten-source deep-read budget · `DROP` with reason · `BACKGROUND` not citable, lead only.

---

## Cluster B — J-space current status

| ID | What it is | Link | Status | Why |
|---|---|---|---|---|
| B-01 | **External review of the source paper**, by Neel Nanda, on LessWrong. Per B-02's description: rhyme-planning and mental-arithmetic experiments **failed to replicate**; multi-hop probe-swap effect **weak**; **J-lens produces many false positives**; multi-fact editing **replicated cleanly** | `lesswrong.com/posts/zFJ3ZdQwrTWE9jT5S/a-review-of-anthropic-s-global-workspace-paper` | **DEEP — read first** | Highest-value item found. The characterisation above is **second-hand via B-02 and must not be cited from it** — read the review itself |
| B-02 | **Independent third-party replication**, `tao-hpu/jspace-replication`. Small open-weight models (GPT-2 124M, Qwen3 1.7B–14B). Contains `docs/claims-inventory.md` mapping paper claim → prompt set → review verdict → priority, and `docs/replication-log.md`. MIT. Paper "arXiv link forthcoming" | `github.com/tao-hpu/jspace-replication` | **DEEP** | Someone has already built a claim ledger for the source paper. See caveat below |
| B-03 | **arXiv version of the source paper** | `arxiv.org/html/2607.15495v1` | TRIAGE | Project has been working from `transformer-circuits.pub`. Check whether section numbering matches — §A.7/§A.9 are cited throughout our Phase 0 record and must resolve correctly in whichever version we cite |
| B-04 | Zvi Mowshowitz commentary | `thezvi.substack.com/p/no-space-like-j-space` | BACKGROUND | Not citable. Useful only for locating what the discourse focused on |
| B-05 | "The AI Dude" blog review | `theaidude.net/blog/jacobian-lens-deep-dive-anthropics-j-space-paper-review` | BACKGROUND | Not citable. Raises a **circularity objection** worth knowing: the lens finds directions whose perturbation changes verbalized output, then declares those directions the verbalizable workspace |
| B-06 | `jspace.com` explainer | — | **DROP** | Reads as SEO/AI-generated content farm. Contains confident numeric claims with no traceable source. Do not cite, do not use as a lead |

**Caveat on B-02.** Zero stars, zero forks, 26 commits, paper not yet posted, and
its README says the project "grew past replication into an audit and reframing" —
i.e. it has a thesis. Treat it as a **lead and a methods comparison**, not an
authority. Its value to us is largely that it points at B-01 and shows what an
independent replication chose to measure. Whether it is citable is Stew's call
and probably depends on whether the arXiv version appears before 29 August.

---

## Cluster A — Is R-space a rediscovery?

| ID | What it is | Link | Status | Why |
|---|---|---|---|---|
| A-01 | *Beyond Language: Format-Agnostic Reasoning Subspaces in Large Language Models* (FARS). Snippet reports subspace ablation of **10 directions out of 1600–4096** with three controls, and states that random directions are close to a no-op | `arxiv.org/html/2605.09496` | **DEEP** | Closest thing found so far to a prior "small reasoning subspace with random controls" result. Directly relevant to what H1 is worth |
| A-02 | *DecodeShare: Tracing the Shared Subspace of LLM Decode-Time Decisions*. Snippet uses the word **"workspace"** for a 32-dimensional Llama-2-7B layer-10 subspace; reports energy/dimension-matched random controls; distinguishes decode-time from prefill-time estimation | `arxiv.org/html/2607.20469v1` | **DEEP** | Potentially the nearest parallel work. If it claims a low-dimensional causally load-bearing workspace with matched controls, our novelty framing must engage it |
| A-03 | *H-Probes: Extracting Hierarchical Structures From Latent Representations of Language Models*. Appendix A.5 describes an ablation protocol using **random rank-matched subspaces** alongside PCA-matched bases | `arxiv.org/pdf/2605.00847` | TRIAGE | Methods comparison for our §4.8 control. Note it also ablates a *rank-matched PCA basis* — a control we do not currently run |
| A-04 | *Conditional Co-Ablation: Recovering Self-Repair Backups in Transformer Circuits*. Snippet describes **self-repair**: ablating primary components produces small effects because backup components absorb the damage | `arxiv.org/html/2607.01940` | **DEEP** | This is a threat, not support — see §Threats below |
| A-05 | *Attention Layers Add Into Low-Dimensional Residual Subspaces* / *Dimensional Collapse in Transformer Attention Outputs* | `arxiv.org/html/2508.16929` | TRIAGE | Bears on whether low-dimensional structure is generic. Appears to be about SAE training, not causal ablation — may be tangential |

---

## Cluster E — Ablation methodology (the adverse lineage)

A named literature exists arguing that **ablation-baseline choice changes which
components appear causally important.** Our harness zero-ablates. This is the
most concrete reviewer objection surfaced so far.

| ID | What it is | Link | Status | Why |
|---|---|---|---|---|
| E-01 | Li & Janson, *Optimal Ablation for Interpretability*, NeurIPS 2024. Snippet reports that for the median component the optimal-ablation loss gap is **11.1% of the zero-ablation gap**, 33.0% of mean, 17.7% of resample | `proceedings.neurips.cc/paper_files/paper/2024/file/c55e6792923cc16fd6ed5c3f672420a5-Paper-Conference.pdf` | **DEEP** | Published proceedings, verifiable. Directly quantifies how much zero-ablation may overstate importance |
| E-02 | Heimersheim & Nanda 2024 — repeatedly cited as the source for "ablation-baseline choice changes which components look important," recommending resample ablation | *not yet located directly* | **DEEP once located** | Cited by at least three separate 2026 papers in the L01-3 results. Find the primary |
| E-03 | Zhang & Nanda 2024 — cited alongside E-02 in the same lineage | *not yet located directly* | TRIAGE | Same |
| E-04 | Hase & Bansal 2021 — cited as showing zero ablation creates out-of-distribution activations | *not yet located directly* | TRIAGE | The origin of the OOD objection |
| E-05 | Goldowsky-Dill et al. 2023 — cited as arguing marginal-distribution resampling may be preferable, and that mean ablation can itself resample off-distribution | *not yet located directly* | TRIAGE | Note this cuts **against** the naive fix of switching to mean ablation |

**E-02 through E-05 were named inside other papers' related-work sections and
have not been retrieved.** They are leads only.

---

## Threats — the column that must not be empty

Per `LIT_REVIEW_PLAN.md` §3.8. Four found in one session, which is a good sign
about the search and a bad sign about the framing.

**T1 — Zero-ablation may overstate importance (E-01, E-04).** Our Control A
headline is a 90% relative degradation under zero-ablation. If the optimal-ablation
gap is a fraction of the zero-ablation gap, a reviewer can argue our effect size
is inflated by distribution shift rather than by the directions mattering.

*Partial defence we already have:* the random draws are zero-ablated too, so
distributional shift is matched across candidate and control, and the candidate
beat 38/38 draws. That argument should be made explicitly in the paper.

*Where the defence is incomplete, and a concrete Phase 3 action:* the shift is
matched on **dimension count**, not on **perturbation magnitude**. If the
candidate directions carry larger activation norm than random draws, they push
the residual stream further off-distribution, and "matched-size" is not matched
on the thing doing the damage. **Measure and report the norm of the removed
component for candidate and random draws at every k.** This is cheap, it is not
currently in `prereg_phase3.md`, and adding it before Phase 3 runs costs nothing
while adding it after would be an amendment.

**T2 — Self-repair (A-04).** If backup components absorb ablation damage, a
*small* measured effect does not license "these directions do not matter." This
cuts toward false negatives, so it belongs in the null diagnosis: a Phase 3 null
has a fifth candidate explanation we have not been tracking.

**T3 — Prior low-dimensional workspace results may already exist (A-01, A-02).**
A-02's use of "workspace" for a 32-dimensional subspace with matched random
controls is close enough to our construct that it needs a direct read before any
novelty sentence is written.

**T4 — The circularity objection (B-05, and implicitly B-01's false-positive
finding).** If the lens defines the space it then validates, the R-space port
inherits the problem. Our version: the R-space is defined by the J-lens readout
and then tested by ablation of J-lens-ranked directions. Worth an explicit
sentence.

---

## Immediate consequence for existing documents

1. **`prereg_phase3.md`** — consider adding the perturbation-norm measurement (T1)
   before it is signed. Cheap now, an amendment later.
2. **Null-diagnosis evidence list** — currently four sources (Control A, Control B,
   nonlinear probe, Phase 1 difficulty gradient). T2 suggests self-repair is a
   fifth alternative explanation for a small effect.
3. **`COMPLIANCE_GUIDE.md` §5** flagged that the proposal's "single-lab, ~1 month
   old, not independently replicated" framing is stale. B-01 and B-02 mean it is
   now **wrong**, not merely stale: an external review and at least one independent
   replication exist. Rewrite once B-01 is read.
