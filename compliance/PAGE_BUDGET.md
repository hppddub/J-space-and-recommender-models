# Page Budget — Interp4Discovery Submission

**Repo location:** `paper/PAGE_BUDGET.md`
**Governs:** compliance guide C2. Fixed **before** drafting begins, per compliance guide §3.1.
**Constraint:** ≤5 pages main text, NeurIPS 2026 workshop template. References and appendices excluded. Main text must be self-contained; reviewers are not obliged to read appendices. Camera-ready adds one page (six total).
**Status:** draft — requires Stew's sign-off before drafting starts.

---

## 0. Why this document exists

The failure mode it prevents is specific and predictable: at day 28, the paper is 6.5 pages, and the cheapest-looking cut is a table of matched random baselines or a paragraph about Control B. That cut is a formatting decision in appearance and a claims decision in fact (proposal 4.8, 4.4). Fixing the budget now means the cut has already been made, deliberately, against a plan.

**The rule:** content moves to the appendix. Content does not leave the record. If something moves, the main text says it exists and where it is.

---

## 1. Allocation

Assumes the minimum viable paper (proposal §6): Phases 0–3.

| § | Section | Budget | Must contain |
|---|---|---|---|
| 1 | Introduction, scope, and what is not tested | **1.00 pp** | The construct under test (proposal 4.1). The substitution stated openly — no outsider can inspect a production system, so this was tested on an open architecture of the same class (guide §6). J-space as single-lab and its current replication status. Verbalizability explicitly excluded. Related work folded in here — 3–5 sentences, not a section |
| 2 | Method | **1.00 pp** | R-space readout and its adaptation from J-lens. Ablation harness. Dimensionality sweep design. Matched random-subspace baseline design. Pre-registration referenced with a pointer to the appendix |
| 3 | Controls | **0.50 pp** | Control A result with **effect magnitude**, pass/partial/fail per finding. Control B result. Both stated in main text even though detail lives in the appendix — a reviewer reading only the main text must be able to judge whether a null is diagnosable |
| 4 | H1 — causal importance | **0.75 pp** | Figure 1: candidate impact against the matched random distribution. Effect size. No mention of compactness anywhere in this section |
| 5 | H2 — compactness | **0.75 pp** | Figure 2: ablation impact as a function of *k*, full curve regardless of shape. Knee analysis reported either way. No mention of causal importance as a conclusion here |
| 6 | Diagnosis and discussion | **0.75 pp** | Explicit null diagnosis if applicable, written against Control A, Control B, the nonlinear probe, and the Phase 1 difficulty gradient. Limits of the linear readout. What the result does not license |
| 7 | Responsible use | **0.25 pp** | Per `paper/RESPONSIBLE_USE_STATEMENT.md`. Mandatory — absence is grounds for desk rejection |
| | **Total** | **5.00 pp** | |

**Slack: none.** The budget is exactly full by construction. Any section that overruns takes from another section, and that trade is a decision to be logged, not absorbed.

---

## 2. Figures

**Two in main text.** One for H1, one for H2. This is not a stylistic preference — it is guide §2.2 enforced by layout. Two figures, two claims, no composite figure asserting both.

A third figure enters main text only by displacing 0.25 pp of prose, named explicitly in the trade.

---

## 3. Appendix (unlimited, but assume unread)

Everything below goes to the appendix, and each has a one-clause pointer from the main text:

- Full Control A replication record: per-finding pass/partial/fail, effect magnitudes, model and tokenization decisions
- Per-*k* tables: candidate impact and full random-draw distributions at every *k*
- `prereg_phase3.md` reproduced verbatim
- `amendments.md` reproduced verbatim, or "no amendments" stated
- Task-family construction and the Phase 1 base-model difficulty gradient
- Seeds, config hashes, compute resources and approximate GPU-hours
- Nonlinear probe detail, if Phase 4 was reached

---

## 4. Discharging the honesty checklist inside 5 pages

Guide §6 requires all nine items to appear explicitly and prominently. Nine items is not nine paragraphs. Mapping:

| Checklist item (proposal §9) | Discharged in |
|---|---|
| 1 — J-space single-lab, one model, replication status | §1, one sentence |
| 2 — verbalizability not tested | §1, one sentence |
| 3 — legibility depends on external metadata | §1 or §6, one clause (moot if Phase 5 not reached — say so) |
| 4 — three separate results | Discharged **structurally** by §§4–5 existing separately, not by prose asserting they are separate |
| 5 — nulls carry both controls | §3 and §6 |
| 6 — linear readout as false-negative source | §6 |
| 7 — no auditing claim without both gates | §6, one sentence, framed as future work |
| 8 — size measured by sweep | Discharged **structurally** by Figure 2 being a curve |
| 9 — ablations carry matched random baselines | Discharged **structurally** by Figure 1 and the appendix tables |

Items 4, 8, and 9 cost almost no prose because the paper's structure is the evidence. That is the point of fixing the structure first.

---

## 5. Open question for the organizers

The CFP does not state whether the responsible-use statement counts toward the five-page main text. This budget assumes it does (the conservative case, 0.25 pp).

**Action:** email `interp4discovery@gmail.com` and ask. It is free to ask now and expensive to discover at day 30. If it may sit in the appendix, §7 releases 0.25 pp back to §6.

---

## 6. Sign-off

**Decision-maker:** Stew.
**Status:** [ ] reviewed  [ ] signed off
**Date:** ____________

Once signed off, an overrun is an explicit trade logged in the lab log, not a quiet edit.
