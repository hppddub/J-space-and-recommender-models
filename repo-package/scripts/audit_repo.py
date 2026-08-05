#!/usr/bin/env python3
"""
audit_repo.py — compare this repo against the layout the governance documents specify.

Run from the repo root:

    python3 scripts/audit_repo.py

Prints a report. Changes nothing. Safe to run any time.

Every path below was extracted from the project's own documents
(proposal, EXECUTION_GUIDE, AI_COLLABORATION_GUIDE, COMPLIANCE_GUIDE,
Phase0 logs, GATE_G0, Phase1_HANDOFF). If a path here is wrong, the
document that names it is the authority, not this script.
"""

import os
import sys

# ---------------------------------------------------------------- expected files

EXPECTED = {
    "Governance — proposal and guides": [
        "proposal/jspace_generative_recommenders_proposal.md",
        "proposal/EXECUTION_GUIDE.md",
        "proposal/AI_COLLABORATION_GUIDE.md",
        "proposal/COMPLIANCE_GUIDE.md",
        "README.md",
    ],
    "Governance — Phase 0 record": [
        "proposal/PHASE0_adapter_points.md",
        "proposal/PHASE0_paper_findings.md",
        "docs/Phase0_LAB_LOG_consolidated.md",
        "docs/Phase0_OVERVIEW.md",
        "docs/Phase1_HANDOFF.md",
    ],
    "Decision records": [
        "decisions/DECISION_phase0_model.md",
        "decisions/DECISION_model_change.md",
        "decisions/DECISION_control_A.md",
        "decisions/THRESHOLD_headroom.md",
        "decisions/GATE_G0.md",
    ],
    "Pre-registration": [
        "preregistration/prereg_controlA.md",
        "preregistration/prereg_phase3.md",
        "preregistration/amendments.md",
    ],
    "Logs": [
        "logs/lab_log.md",
    ],
    "Source — ablation harness": [
        "src/ablation/directions.py",
        "src/ablation/harness.py",
        "src/ablation/sweep.py",
    ],
    "Source — band derivation and readout": [
        "src/band/derive.py",
        "src/band/readout.py",
    ],
    "Source — evaluation": [
        "src/evals.py",
        "src/tasks.py",
        "src/intact.py",
        "src/rescore.py",
    ],
    "Tests": [
        "tests/test_ablation.py",
        "tests/test_tasks.py",
        "tests/test_intact.py",
        "tests/test_readout.py",
        "tests/test_hf_layout.py",
    ],
    "Scripts": [
        "scripts/step0_verify_model.py",
        "scripts/headroom_check.py",
        "scripts/derive_band.py",
        "scripts/verify_readout.py",
        "scripts/run_control_a.py",
        "scripts/run_intact_tasks.py",
    ],
    "Notebooks": [
        "notebooks/stageA_inspect_lens.ipynb",
        "notebooks/stageB_derive_band.ipynb",
        "notebooks/stageB2_verify_readout.ipynb",
        "notebooks/controlA_run.ipynb",
        "notebooks/controlA_intact_tasks.ipynb",
        "notebooks/headroom_qwen3-4b.ipynb",
        "notebooks/pro_session_qwen3-8b.ipynb",
    ],
    "Compliance and writing": [
        "compliance/PAGE_BUDGET.md",
        "compliance/RESPONSIBLE_USE_STATEMENT.md",
        "compliance/LICENCES.md",
    ],
    "Literature review (new, session 17)": [
        "lit/DECISION_lit_review_scope.md",
        "lit/claim_ledger.md",
        "lit/searches_log.md",
        "lit/candidates.md",
        "lit/AMENDMENT_jspace_status_framing.md",
    ],
    "Third party (vendored, never modified)": [
        "third_party/jacobian-lens/",
        "third_party/PINNED_COMMIT.txt",
    ],
}

EXPECTED_DIRS = [
    "results/raw/",
    "configs/",
]

# Results directories named in the Phase 0 record. Presence is not required
# (they may be gitignored), but absence is worth knowing about.
RESULTS_EXPECTED = [
    "results/raw/headroom_qwen3.5-4b/",
    "results/raw/band_qwen3-8b/",
    "results/raw/controlA_qwen3-8b/",
]

SUPERSEDED = [
    "LIT_REVIEW_PROTOCOL.md",
    "proposal/LIT_REVIEW_PROTOCOL.md",
    "lit/LIT_REVIEW_PROTOCOL.md",
]


def exists(p):
    return os.path.exists(p.rstrip("/"))


def main():
    if not os.path.isdir(".git"):
        print("WARNING: no .git directory here. Are you in the repo root?\n")

    missing_total = 0
    present_total = 0

    for section, paths in EXPECTED.items():
        print(f"\n=== {section} ===")
        for p in paths:
            if exists(p):
                print(f"  ok       {p}")
                present_total += 1
            else:
                print(f"  MISSING  {p}")
                missing_total += 1

    print("\n=== Directories ===")
    for d in EXPECTED_DIRS + RESULTS_EXPECTED:
        print(f"  {'ok      ' if exists(d) else 'MISSING '} {d}")

    print("\n=== Superseded (should carry a SUPERSEDED header, not be deleted) ===")
    for p in SUPERSEDED:
        if exists(p):
            with open(p, "r", errors="replace") as f:
                head = f.read(400)
            flag = "has header" if "SUPERSEDED" in head else "NO HEADER — add one"
            print(f"  found    {p}  ({flag})")

    # --- files present but not expected, at top level only
    print("\n=== Top-level files not in the expected list ===")
    known = {p.split("/")[0] for group in EXPECTED.values() for p in group}
    known |= {"scripts", "src", "tests", "logs", "docs", "results", "configs",
              "third_party", "proposal", "preregistration", "decisions", "lit",
              "notebooks", "compliance", ".git", ".gitignore", "LICENSE"}
    for entry in sorted(os.listdir(".")):
        if entry not in known:
            print(f"  unlisted {entry}")

    print(f"\n---\nPresent: {present_total}   Missing: {missing_total}")
    print("Missing is not automatically bad — a file may live elsewhere, or")
    print("not exist yet. Use this to decide, not as a checklist to satisfy.")


if __name__ == "__main__":
    main()
