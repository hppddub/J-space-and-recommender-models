#!/usr/bin/env bash
#
# reorganize.sh — restructure the repo to the layout the governance documents specify.
#
# SAFE BY DEFAULT. Run it once to see what it would do:
#
#     bash reorganize.sh
#
# Then run it for real:
#
#     bash reorganize.sh --apply
#
# It only moves files that exist. It never deletes. It never overwrites.
# If your local copy has more files than the GitHub remote (likely), those
# get moved too, provided their names match.
#
# Run from the repo root.

set -u

APPLY=0
[ "${1:-}" = "--apply" ] && APPLY=1

if [ ! -d .git ]; then
  echo "ERROR: no .git here. Run from the repo root."
  exit 1
fi

if [ $APPLY -eq 1 ]; then
  # Only tracked-file modifications block. Untracked files (including this
  # script, and any files you are about to add) are fine.
  DIRTY=$(git status --porcelain --untracked-files=no | wc -l)
  if [ "$DIRTY" -ne 0 ]; then
    echo "You have uncommitted changes to tracked files. Commit or stash them"
    echo "first, so this reorganization is a clean, reviewable diff on its own."
    echo
    git status --short --untracked-files=no
    exit 1
  fi
fi

say() { if [ $APPLY -eq 1 ]; then echo "  $*"; else echo "  [dry run] $*"; fi; }

mkd() {
  if [ ! -d "$1" ]; then
    say "mkdir $1"
    [ $APPLY -eq 1 ] && mkdir -p "$1"
  fi
}

mv_if() {                       # mv_if <source> <destination-dir>
  local src="$1" dst="$2"
  if [ -e "$src" ]; then
    if [ -e "$dst/$(basename "$src")" ]; then
      say "SKIP $src -> $dst/ (destination already exists)"
      return
    fi
    say "git mv $src -> $dst/"
    if [ $APPLY -eq 1 ]; then
      mkdir -p "$dst"
      git mv "$src" "$dst/" 2>/dev/null || mv "$src" "$dst/"
    fi
  fi
}

echo "=== 1. Directories ==="
for d in proposal docs decisions preregistration logs lit compliance \
         src src/ablation src/band tests scripts notebooks configs \
         results results/raw third_party; do
  mkd "$d"
done

echo
echo "=== 2. Results — headroom run for Qwen3.5-4B ==="
echo "    (summary.json's own config says out=results/raw/headroom_qwen3.5-4b/)"
mkd "results/raw/headroom_qwen3.5-4b"
for f in summary.json rows.json diagnostic_rows.json rescored_rows.json; do
  mv_if "$f" "results/raw/headroom_qwen3.5-4b"
done

echo
echo "=== 3. Scripts ==="
for f in headroom_check.py rescore.py derive_band.py verify_readout.py \
         run_control_a.py run_intact_tasks.py step0_verify_model.py audit_repo.py; do
  mv_if "$f" "scripts"
done

echo
echo "=== 4. Notebooks ==="
for f in *.ipynb; do
  [ -e "$f" ] && mv_if "$f" "notebooks"
done

echo
echo "=== 5. Decision records ==="
for f in DECISION_model_change.md DECISION_phase0_model.md DECISION_control_A.md \
         THRESHOLD_headroom.md GATE_G0.md; do
  mv_if "$f" "decisions"
done

echo
echo "=== 6. Pre-registration and amendments ==="
for f in amendment_001_headroom_scoring.md amendments_002_003.md amendments.md \
         prereg_controlA.md prereg_phase3.md prereg_phase4.md; do
  mv_if "$f" "preregistration"
done

echo
echo "=== 7. Governance documents ==="
for f in jspace_generative_recommenders_proposal.md EXECUTION_GUIDE.md \
         AI_COLLABORATION_GUIDE.md COMPLIANCE_GUIDE.md \
         PHASE0_adapter_points.md PHASE0_paper_findings.md; do
  mv_if "$f" "proposal"
done

for f in Phase0_OVERVIEW.md Phase0_LAB_LOG_consolidated.md Phase1_HANDOFF.md; do
  mv_if "$f" "docs"
done

echo
echo "=== 8. Logs, compliance, literature ==="
mv_if "lab_log.md" "logs"
for f in PAGE_BUDGET.md RESPONSIBLE_USE_STATEMENT.md LICENCES.md; do
  mv_if "$f" "compliance"
done
for f in claim_ledger.md searches_log.md candidates.md \
         DECISION_lit_review_scope.md AMENDMENT_jspace_status_framing.md; do
  mv_if "$f" "lit"
done

echo
echo "=== 9. Source ==="
for f in directions.py harness.py sweep.py; do mv_if "$f" "src/ablation"; done
for f in derive.py readout.py;               do mv_if "$f" "src/band";     done
for f in evals.py tasks.py intact.py;        do mv_if "$f" "src";          done
for f in test_*.py;  do [ -e "$f" ] && mv_if "$f" "tests"; done

echo
echo "=== 10. Placeholder READMEs for empty directories ==="
write_stub() {
  local path="$1" body="$2"
  if [ ! -e "$path" ]; then
    say "write $path"
    if [ $APPLY -eq 1 ]; then
      mkdir -p "$(dirname "$path")"
      printf '%s\n' "$body" > "$path"
    fi
  fi
}

write_stub "configs/README.md" \
"# configs

One config file per run. Every run writes a snapshot of its config into its
\`results/raw/<run>/\` directory alongside the git commit hash, per
AI_COLLABORATION_GUIDE.md §1.2."

write_stub "results/raw/README.md" \
"# results/raw

One directory per run. Each contains the raw outputs, a config snapshot, and the
git commit hash of the code that produced them.

Large binary artifacts (.npy, .npz, weights) are gitignored. JSON result files
are the evidence and are committed."

write_stub "third_party/README.md" \
"# third_party

Vendored dependencies. Never modified — adaptations live in \`src/\`.

- \`jacobian-lens/\` — Anthropic's released J-lens code, Apache-2.0.
  Pinned commit recorded in \`PINNED_COMMIT.txt\`."

echo
echo "=== 11. .gitignore ==="
if [ ! -e .gitignore ]; then
  say "write .gitignore"
  if [ $APPLY -eq 1 ]; then
    cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.venv/
venv/
.ipynb_checkpoints/
.DS_Store

# Model weights and large binaries — never committed
*.safetensors
*.bin
*.pt
*.pth

# Large numeric artifacts. JSON results ARE committed: they are the evidence.
results/raw/**/*.npy
results/raw/**/*.npz

# Vendored upstream is cloned, not committed. Remove this line if you
# decide to vendor it for real.
third_party/jacobian-lens/
EOF
  fi
fi

echo
echo "======================================================================"
if [ $APPLY -eq 1 ]; then
  echo "Done. Review with:  git status  and  git diff --stat"
  echo "Then commit. See REPO_CLEANUP_PLAN.md step 5 for staged commits."
else
  echo "Dry run only. Nothing changed."
  echo "Run 'bash reorganize.sh --apply' to do it."
fi
