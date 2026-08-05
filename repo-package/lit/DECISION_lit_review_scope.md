# DECISION — Literature review scope and method

**Date:** 2026-08-05 · **Decided by:** Stew · **Drafted by:** Claude
**Signed:** _______________ **Date:** ___________

---

## D1. `LIT_REVIEW_PROTOCOL.md` is superseded

The earlier protocol predates the compliance work, the Phase 0 results, and the
G0 gate. It is **superseded, not withdrawn.**

**Action:** add a header to the existing file reading
`SUPERSEDED 2026-08-05 by LIT_REVIEW_PLAN.md — written before Phase 0 results and
the compliance ledger existed; retained for the record.`
Do not delete it. A superseded document with a dated reason is part of the
record; a vanished one is a gap.

## D2. Claude may run web searches and supply links

**Amends the previous protocol's rule that Claude proposes questions only.**

Permitted:
- Running searches and reporting what came back, with URLs.
- Reporting what a retrieved snippet or page appears to say, marked as retrieved.
- Building candidate/triage lists.

Not permitted, unchanged:
- Any citation, title, author, year, venue, or arXiv ID stated from recall.
- Any characterisation of a paper Claude has not retrieved in this session.
- Any `.bib` entry. Every reference enters the bibliography only after Stew opens
  the primary source (C6).

**Standing rule:** everything Claude surfaces is a **lead**, marked `UNVERIFIED`
until Stew opens the source. Identifiers read out of search snippets are
especially error-prone and must be checked character by character.

## D3. Deep-read budget: 10

Ten sources get the method-and-limitations read. Triage reads are unbudgeted.
If the eleventh looks necessary, that is a decision to log, not a drift.

## D4. Pass 3 checkpoint is informal

"Does the literature change what H1 is worth?" is asked at the end of Pass 3 and
answered in a lab-log entry. Not a numbered gate.

## D5. Cluster ordering — framing before Phase 1 unblocking

Order: **A → B → E → C → D → G.**

Stew's rationale: better to understand the landscape before committing to an
experimental setup.

**Recorded cost:** the Phase-1-blocking questions (which architectures have
released weights; tokens per item; dataset licences) sit behind four clusters. If
the travel block runs short, Phase 1 stays blocked on return, against a 2026-08-18
checkpoint.

**Agreed mitigation:** clusters C(1–2) and G are triage-tier factual lookups, not
deep reads. They get one dedicated early session in parallel with the framing
work and do not consume deep-read budget.
