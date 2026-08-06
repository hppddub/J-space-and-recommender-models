"""
provenance.py — record which code produced a result.

Replaces the three separate `git_commit()` implementations in
`src/ablation/sweep.py`, `scripts/run_control_a.py`, and
`scripts/headroom_check.py`.

## The bug this fixes

All three called `git rev-parse HEAD` in the *current working directory*. Under
Colab the working directory is not a git checkout, so the call failed and each
returned the string "UNKNOWN". Every Phase 0 result carries that value. The
failure was silent, so nothing surfaced it until the repository was audited.

## The two changes

1. Look for the git checkout **next to the source file**, not in the working
   directory. The source file is inside the repository by definition.
2. When the commit genuinely cannot be determined, **raise** rather than return a
   placeholder. A run that cannot identify its own code should not silently
   produce results that look complete.

Set `allow_unknown=True` only for throwaway exploration, never for a run whose
output will be reported.
"""

from __future__ import annotations

import os
import subprocess


class ProvenanceError(RuntimeError):
    """Raised when the code version behind a run cannot be established."""


def _run(args, cwd):
    return subprocess.check_output(
        args, cwd=cwd, text=True, stderr=subprocess.DEVNULL
    ).strip()


def git_commit(explicit: str | None = None, allow_unknown: bool = False) -> str:
    """Return the full commit hash of the code being executed.

    explicit       -- pass a hash directly. Use this when the code was copied
                      into an environment without a git checkout. It is recorded
                      verbatim, so it must be correct.
    allow_unknown  -- return "UNKNOWN-NOT-A-GIT-CHECKOUT" instead of raising.
                      Exploration only.
    """
    if explicit:
        return explicit.strip()

    here = os.path.dirname(os.path.abspath(__file__))
    try:
        commit = _run(["git", "rev-parse", "HEAD"], cwd=here)
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        if allow_unknown:
            return "UNKNOWN-NOT-A-GIT-CHECKOUT"
        raise ProvenanceError(
            "Could not determine the git commit for this run.\n"
            f"  Looked in: {here}\n"
            "This usually means the code was copied into the environment rather\n"
            "than cloned. Fix by either:\n"
            "  (a) cloning the repository in the runtime environment, or\n"
            "  (b) passing the hash explicitly: git_commit(explicit='<hash>')\n"
            "Do not proceed without one of these — Phase 0 results were written\n"
            "with git_commit='UNKNOWN' and their provenance is now unverifiable."
        )

    # A clean tree matters as much as the hash: a dirty tree means the committed
    # code is not the code that ran.
    try:
        if _run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=here):
            commit += "-dirty"
    except Exception:
        pass

    return commit


def provenance_block(explicit: str | None = None, allow_unknown: bool = False) -> dict:
    """Metadata block to embed in every result file."""
    import platform
    from datetime import datetime, timezone

    return {
        "git_commit": git_commit(explicit=explicit, allow_unknown=allow_unknown),
        "run_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "python": platform.python_version(),
        "upstream_jacobian_lens": "581d398613e5602a5af361e1c34d3a92ea82ba8e",
    }


if __name__ == "__main__":
    print(git_commit(allow_unknown=True))
