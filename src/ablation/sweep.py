"""Resumable sweep over ablation conditions.

Colab sessions die (AI guide §1.2). The Phase 3 sweep is naturally many short
independent runs, so it survives that *provided* it is resumable from the
start — checkpoint per condition, skip completed on restart.

Every run writes a config snapshot and git commit hash into its output
directory (guide §1.2). "It was in the session I lost" does not survive review.
"""

from __future__ import annotations
from provenance import git_commit

import json
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from .harness import AblationSpec



def build_conditions(
    bands: dict[str, Sequence[int]],
    ks: Sequence[int],
    *,
    n_random_draws: int = 5,
    base_seed: int = 0,
    include_next_k: bool = True,
) -> list[AblationSpec]:
    """The full condition grid: candidate + matched controls at every point.

    Controls are generated *alongside* every candidate condition rather than as
    a separate pass. Proposal 4.8 requires a matched random distribution beside
    every ablation number in the paper; generating them together makes it
    structurally hard to end up with a candidate result that has no baseline.
    """
    out: list[AblationSpec] = [AblationSpec(layers=(), k=0, selector="none")]
    for band in bands.values():
        layers = tuple(band)
        for k in ks:
            out.append(AblationSpec(layers=layers, k=k, selector="topk"))
            if include_next_k:
                out.append(AblationSpec(layers=layers, k=k, selector="next_k"))
            for d in range(n_random_draws):
                seed = base_seed + 1000 * d + k
                out.append(AblationSpec(layers=layers, k=k, selector="random_lens", seed=seed))
                out.append(AblationSpec(layers=layers, k=k, selector="random_iso", seed=seed))
    return out


def run_sweep(
    conditions: Iterable[AblationSpec],
    evaluate: Callable[[AblationSpec], dict[str, Any]],
    out_dir: str | Path,
    *,
    extra_config: dict[str, Any] | None = None,
    verbose: bool = True,
) -> list[dict[str, Any]]:
    """Evaluate each condition, skipping any already on disk.

    Args:
        evaluate: Takes a spec, returns a JSON-serialisable dict of metrics.
            Kept as a callback so the same sweep drives Control A (an open LLM
            on a two-hop set) and Phase 3 (a recommender on easy/hard tasks)
            without modification.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    commit, results = git_commit(), []

    for spec in conditions:
        key = spec.key()
        path = out_dir / key
        result_file = path / "result.json"
        if result_file.exists():
            results.append(json.loads(result_file.read_text()))
            if verbose:
                print(f"[skip] {key} {spec.selector} k={spec.k}")
            continue

        metrics = evaluate(spec)
        path.mkdir(parents=True, exist_ok=True)
        (path / "config.json").write_text(
            json.dumps(
                {"spec": asdict(spec), "git_commit": commit, **(extra_config or {})},
                indent=2, default=str,
            )
        )
        record = {"key": key, "spec": asdict(spec), "metrics": metrics}
        result_file.write_text(json.dumps(record, indent=2, default=str))
        results.append(record)
        if verbose:
            print(f"[run ] {key} {spec.selector} k={spec.k} -> {metrics}")

    return results


def summarise(results: Sequence[dict[str, Any]], metric: str) -> dict[str, Any]:
    """Group by (band, k, selector) — deliberately *not* a composite score.

    Guide 2.2: no composite metric may blend causal importance with compactness
    or legibility. This returns the candidate value and the raw distribution of
    each control separately, so H1 and H2 are read off different objects.
    """
    from collections import defaultdict

    groups: dict[tuple, list[float]] = defaultdict(list)
    for r in results:
        s = r["spec"]
        groups[(tuple(s["layers"]), s["k"], s["selector"])].append(r["metrics"][metric])

    out: dict[str, Any] = {}
    for (layers, k, selector), vals in groups.items():
        out[f"{selector}|k={k}|layers={layers[0] if layers else '-'}..{layers[-1] if layers else '-'}"] = {
            "n": len(vals),
            "values": vals,
            "mean": sum(vals) / len(vals),
        }
    return out
