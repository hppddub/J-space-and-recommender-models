# AMENDMENT — J-space status framing

**Date:** 2026-08-05 · **Drafted by:** Claude · **Owner:** Stew
**Trigger:** Session 17. Primary source read (external review of the J-space
paper, 6 July 2026), establishing that the clause "not yet independently
replicated even within its original domain" is false as of this date.
**Applies to:** `jspace_generative_recommenders_proposal.md`,
`EXECUTION_GUIDE.md`
**Signed:** _______________ **Date:** ___________

---

## Verify before applying

Two items in the new text are mine, not yours, and both are assertions about
someone else's published work:

1. **"July 2026."** Taken from the review's publication date and secondary
   coverage, not from the paper's own masthead. Confirm the exact publication
   date against the paper before submission.
2. **The multi-hop characterisation** in Change 1 — that the confound was a
   dataset whose intermediate and answer terms were linearly related. Confirm
   this is the reviewer's own framing of his result and not sharper than what he
   claimed.

Do not apply Change 1 until both are checked.

---

## Change 1 — proposal §1, line 17

**Old:**

> This is a **single-lab, ~3-week-old finding at time of writing**, established on
> one text-only language model (Claude), and still undergoing independent review
> and replication (including an in-progress replication on an open-weight model).
> It should be treated as a claim to test, not a fact to build on.

**New:**

> The J-space result was published in July 2026 by a single lab, established
> primarily on one text-only language model. It shipped with solicited external
> commentary, one of which included an independent replication on an open-weight
> model: the core claims reproduced, two experiments did not, and the multi-hop
> replication was confounded by a dataset whose intermediate and answer terms were
> linearly related. Every model on which the construct has been established shares
> a natural-language token vocabulary — the property this project removes. It
> should be treated as a claim to test, not a fact to build on.

---

## Change 2 — proposal §9, item 1, line 187

**Old:**

> - J-space is a single-lab finding, roughly a month old at the time of this
>   project's design, established on one text-only LLM, and not yet independently
>   replicated even within its original domain.

**New:**

> - J-space is a recent single-lab result, established on one text-only language
>   model. It has since been replicated in part on a second, open-weight text
>   model; both models share the property this project removes, a natural-language
>   token vocabulary.

---

## Change 3 — `EXECUTION_GUIDE.md` §6, checklist item 1, line 303

The checklist restates §9 tersely. Mirror Change 2 in the same register.

**Old:**

> 1. J-space is single-lab, ~1 month old at design time, one text-only LLM, not
>    independently replicated even in its original domain

**New:**

> 1. J-space is a recent single-lab result on one text-only LLM, replicated in
>    part on a second open-weight text model; both have natural-language token
>    vocabularies

---

## Change 4 — `EXECUTION_GUIDE.md` Phase 0 guardrail, line 130

The guardrail's instruction is still right. Its stated *reason* is stale, and the
correct reason is stronger.

**Old:**

> - If the replication only partially succeeds, **document exactly which parts did
>   and didn't reproduce.** This bounds every downstream claim, and it is itself a
>   reportable finding given the original result is single-lab and ~1 month old.

**New:**

> - If the replication only partially succeeds, **document exactly which parts did
>   and didn't reproduce.** This bounds every downstream claim. Per-finding
>   reporting is also the established practice for this result: the published
>   external replication reported its own outcomes finding by finding rather than
>   as a single verdict.

---

## Consequence to carry forward — not a text change

The deleted clause was doing work beyond accuracy. It licensed a reading in which
a Phase 3 null could be attributed to the method being untested outside its
original lab. **That reading is no longer available.** The technique ports to an
open-weight model of a different family on a modest prompt budget.

A null in the recommender domain must therefore be diagnosed as either (a) the
phenomenon is absent in this domain, or (b) the readout is too weak *in this
domain specifically* — not (c) the method does not travel. The Phase 4 null
diagnosis in `EXECUTION_GUIDE.md` currently lists four evidence sources against
three branches. Branch (b) at the *pipeline* level, which Control A was built to
address, is now partly addressed by external evidence as well; branch (c) as
originally framed is closed.

This narrows the diagnosis, which is an improvement, and removes a fallback,
which is a cost. **Decide explicitly whether the Phase 4 diagnosis wording should
be revised now or after Phase 3 results exist.** Revising it now, before results,
is the more defensible ordering.
