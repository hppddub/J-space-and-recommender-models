# Licence Register — R-Space Generalization Test

**Repo location:** `LICENCES.md` (repo root)
**Governs:** compliance guide C8 (datasets), C9 (model and J-lens code).
**Why:** the NeurIPS Code of Ethics applies program-wide and requires authors to respect the terms of licensed datasets, to confirm datasets have not been deprecated or withdrawn, and to state licences and access restrictions in the paper. This register is where those facts live so that the responsible-use statement and the paper's data section can be filled from a record rather than from recall.

**Rule:** one row per artifact. A row is not complete until the *licence text itself* has been opened — not the README's description of it, not a memory of what that project usually uses. Unverified rows stay marked unverified.

---

## 1. Code and models

| Artifact | Source | Licence | Verified from | Permits research use | Permits publishing results | Attribution required | Status |
|---|---|---|---|---|---|---|---|
| Anthropic `jacobian-lens` | GitHub (cloned) | | `LICENSE` file in repo root | | | | **open — close at Phase 0** |
| Phase 0 model (Qwen3.5-4B, pending headroom pre-check) | Hugging Face | | model card + licence file on the HF repo | | | | **open — close at Phase 0** |
| Phase 1 recommender (HSTU-BLaIR / GPTRec / TIGER reimpl., TBD) | | | | | | | open — Phase 1 |
| Any pretrained recommender weights used | | | | | | | open — Phase 1 |

**Notes to fill at Phase 0:**
- Qwen releases have historically varied by size tier in whether they are Apache-2.0 or under a bespoke community licence. Do not assume; open the licence on the specific checkpoint used.
- If the J-lens code carries a licence restricting derivative distribution, that constrains the anonymised code release (C5). Check this **before** planning the release, not during it.

---

## 2. Datasets

| Dataset | Source | Licence / terms | Deprecation checked | PII present | Redistribution permitted | Citation required | Status |
|---|---|---|---|---|---|---|---|
| MovieLens-1M | GroupLens | GroupLens usage terms — verify current text | | anonymised user IDs | typically **no** | **yes** — specific citation required by terms | open — Phase 1 |
| Amazon Reviews 2023 (category subsets) | | | | reviewer IDs; user-authored review text | | | open — Phase 1 |
| Steam dataset | | | | | | | open — Phase 1 |

**Checks required per dataset before committing to it (Phase 1, guide 1b):**

- [ ] Licence text opened and recorded above
- [ ] Checked against the NeurIPS deprecated-datasets list
- [ ] Confirmed still available from the original distributor
- [ ] Citation requirement recorded, and the required citation form captured verbatim
- [ ] PII assessment: what user-attributable content exists, and whether any of it could surface in a figure, table, or appendix
- [ ] Metadata richness confirmed sufficient for Phase 5 (guide Phase 1, 1b) — this is a scientific check, recorded here because it shares the same moment

**Amazon Reviews 2023 specifically.** It carries user-authored review text and reviewer identifiers. This is the dataset in the candidate set most likely to create a data-ethics obligation. If it is selected, the responsible-use statement's data paragraph must accurately describe what does and does not appear in the paper, and no individual review text should appear anywhere in the submission.

---

## 3. Feeds into

- `paper/RESPONSIBLE_USE_STATEMENT.md` §1, fourth paragraph — `[Dataset]` and `[licence]` fill-ins
- Paper data/setup section
- Compliance guide C8, C9
- The anonymised code release (C5) — licence compatibility must be checked before release, not after

---

## 4. Sign-off

**Decision-maker:** Stew.
**Phase 0 rows closed:** [ ]  **Date:** ____________
**Phase 1 rows closed:** [ ]  **Date:** ____________
