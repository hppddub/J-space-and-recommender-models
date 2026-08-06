# Responsible-Use Statement — Working Draft

**Repo location:** `paper/RESPONSIBLE_USE_STATEMENT.md`
**Governs:** compliance guide C3.
**Requirement:** the Interp4Discovery CFP requires every submission to include a short statement of potential societal impacts and suggested mitigations. A missing statement is grounds for desk rejection.
**Budget:** 0.25 pp main text (see `paper/PAGE_BUDGET.md` §1, pending the §5 clarification).
**Status:** results-independent content drafted. Results-dependent paragraph marked and blocked.

---

## 0. Drafting rule

This statement is subject to the same discipline as the rest of the paper. It must not assert existence, compactness, or legibility of the R-space, and it must not imply an auditing capability. A responsible-use statement that overclaims in the course of being responsible is worse than no statement, because it launders the overclaim through an ethics section where reviewers are less likely to challenge it.

Terminology discipline (guide §2.1) applies here in full.

---

## 1. Draft — results-independent core

> **Responsible use.** This work is a controlled generalization test of an interpretability technique, conducted entirely on open, published model architectures and public interaction datasets. No production recommendation system was accessed, and no claim is made about any deployed system. We note this substitution explicitly because the motivating question concerns platforms whose internals no external researcher can inspect; the honest scope of this study is an open architecture of the same class.
>
> The technique studied is dual-use in a direct and symmetric way. A method that locates a small set of activation directions with disproportionate causal influence over a recommender's future output is, by the same token, a method for identifying where such a system could be steered. We report it because the auditing and transparency case for understanding these systems is strong and because the method and its limits are better established in the open than assumed; but we do not present the technique as an auditing tool, and Section [X] states the two conditions that would have to hold before any auditing claim were warranted.
>
> A second risk is specific to this paper's framing. Claims that recommender systems can be audited for hidden objectives carry weight in policy discussion beyond what the underlying evidence supports. We have structured the claims so that existence, compactness, and legibility are reported as separate results with separate evidence, and so that any auditing application is explicitly conditional on more than one of them holding. Readers and any downstream citation should respect that staging.
>
> All data used is public and pre-existing. We collected no new data, and no human subjects were involved. [Dataset] is used under [licence]; we cite it as its terms require and redistribute no raw records. The dataset contains user interaction histories and, in some subsets, user-authored text; we do not reproduce any individual record or user-attributable text in this paper or its appendix. Compute used is reported in Appendix [X].
>
> We release code, configurations, seeds, the pre-registration, and the full experimental log, including runs that failed or produced nothing, so that the strength and the limits of this result can be checked independently rather than taken on the paper's own account.

---

## 2. Blocked — results-dependent paragraph

Do not draft this until Phase 3 results exist. The two branches differ materially and pre-drafting either one is a design leak (guide §0, question 3).

**If the result is null or H1 fails:** the dual-use paragraph in §1 largely stands down and should be shortened, with a sentence stating that no exploitable structure was identified by this method and that a negative result does not establish that none exists. Do not use the null as a reassurance — the honest position is that this method did not find it.

**If H1 holds:** the dual-use paragraph becomes live and needs one added sentence naming the concrete misuse path — a located, causally load-bearing subspace is a target for optimisation as readily as for inspection — and what, if anything, mitigates it. Say plainly if nothing does.

**If H1 holds and H2 fails:** note that a diffuse subspace is materially harder to steer than a compact one, and that this weakens both the auditing case and the misuse case symmetrically. Resist stating this as good news.

---

## 3. Fill-ins required before submission

- [ ] `[Dataset]` and `[licence]` — resolve at Phase 1, record in `LICENCES.md` (C8)
- [ ] Section cross-references `[X]`
- [ ] Compute figure — hardware and approximate GPU-hours (C10)
- [ ] Results-dependent paragraph per §2
- [ ] Confirm whether Amazon Reviews subsets are in use; if so, the user-authored-text sentence must be accurate about what appears in figures and appendix
- [ ] Compress to fit 0.25 pp — the draft above is over budget by design, so the cut is an editing pass rather than a scramble

---

## 4. Sign-off

**Decision-maker:** Stew.
**Status:** [ ] reviewed  [ ] signed off  [ ] results-dependent paragraph completed
**Date:** ____________
