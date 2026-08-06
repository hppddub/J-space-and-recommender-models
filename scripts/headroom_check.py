"""Phase 0 headroom pre-check — DECISION_control_A.md §4.6.

Measures unablated accuracy on the 90 two-hop prompts of probe-swap.json.
No lens. No harness. No ablation. One forward pass per prompt.

This decides the model. Per DECISION_control_A.md §4.6, the paper's ablation
result depends on the unablated model being near ceiling; if accuracy is low
there is nothing for ablation to remove, and a failed Control A would be caused
by model selection rather than by a broken instrument — which is precisely the
attribution Control A exists to make possible.

**Write and commit your threshold before running this.** See the docstring of
`main()`. A threshold chosen after seeing the number is not a threshold.

Usage:
    python headroom_check.py --model Qwen/Qwen3.5-4B \
        --data data/experiments/probe-swap.json --out results/raw/headroom/
"""

from __future__ import annotations
from provenance import git_commit

import argparse
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


# --- scoring ---------------------------------------------------------------

def normalise(prompt: str, answer: str) -> tuple[str, str]:
    """Fix the trailing-whitespace inconsistency in probe-swap.json.

    29 of 90 prompts end with a space and 61 do not, so the true continuation is
    " Portuguese" for some items and "Portuguese" for others. Tokenising the raw
    `answer` scores one group wrong regardless of which convention you pick, and
    depresses measured accuracy for a reason that has nothing to do with the
    model. Normalising both sides removes the artifact.
    """
    return prompt.rstrip(), " " + answer.strip()


@torch.no_grad()
def score_item(model, tok, prompt: str, answer: str, device) -> dict:
    """Three metrics, because they disagree and the disagreement is informative.

    - ``exact``: greedy continuation of len(answer_tokens) equals the answer.
      Strict and unambiguous. Recommended primary.
    - ``first_token``: greedy next token equals the answer's first token. This
      is what "greedy next-token accuracy" most plausibly means, and it is
      lenient — it credits a correct first token followed by a wrong completion.
    - ``n_answer_tokens``: 1 means the two metrics coincide for this item.
    """
    prompt, answer = normalise(prompt, answer)
    ans_ids = tok(answer, add_special_tokens=False).input_ids
    ids = tok(prompt, return_tensors="pt").input_ids.to(device)

    out = model.generate(
        ids,
        max_new_tokens=len(ans_ids),
        do_sample=False,
        num_beams=1,
        pad_token_id=tok.eos_token_id,
    )
    gen_ids = out[0, ids.shape[1]:].tolist()

    return {
        "exact": tok.decode(gen_ids).strip().lower() == answer.strip().lower(),
        "first_token": bool(gen_ids) and gen_ids[0] == ans_ids[0],
        "n_answer_tokens": len(ans_ids),
        "generated": tok.decode(gen_ids),
    }


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson 95% interval. At n=90 the interval is roughly +/-8-10pp — wide
    enough that a threshold should not be set to two decimal places."""
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5) / d
    return (max(0.0, c - h), min(1.0, c + h))


# --- main ------------------------------------------------------------------

def main() -> None:
    """Run the check and write results.

    Before running, commit a file recording:
      - the threshold on the primary metric that counts as sufficient headroom
      - which metric is primary (recommended: ``exact``)
      - what you will do if it fails (DECISION_phase0_model.md §4: step *up*,
        not down — below some size Control A stops being informative at all)
    """
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--data", required=True, help="path to probe-swap.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--limit", type=int, default=None, help="smoke-test on N items")
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=getattr(torch, args.dtype), device_map=device
    ).eval()

    items = json.load(open(args.data))["items"]
    if args.limit:
        items = items[: args.limit]

    rows = []
    for i, it in enumerate(items):
        r = score_item(model, tok, it["prompt"], it["answer"], device)
        r.update(name=it["name"], category=it["category"], answer=it["answer"])
        rows.append(r)
        print(f"[{i+1}/{len(items)}] {it['name']:<28} "
              f"exact={r['exact']:d} first={r['first_token']:d} "
              f"({r['n_answer_tokens']}tok) -> {r['generated']!r}")

    n = len(rows)
    n_exact = sum(r["exact"] for r in rows)
    n_first = sum(r["first_token"] for r in rows)
    single = [r for r in rows if r["n_answer_tokens"] == 1]

    by_cat = defaultdict(list)
    for r in rows:
        by_cat[r["category"]].append(r["exact"])

    summary = {
        "model": args.model,
        "n": n,
        "exact": {"k": n_exact, "acc": n_exact / n, "wilson95": wilson(n_exact, n)},
        "first_token": {"k": n_first, "acc": n_first / n, "wilson95": wilson(n_first, n)},
        "single_token_subset": {
            "n": len(single),
            "acc": (sum(r["exact"] for r in single) / len(single)) if single else None,
        },
        "answer_token_lengths": dict(Counter(r["n_answer_tokens"] for r in rows)),
        # Only categories with n>=4 are worth reading; probe-swap.json has a long
        # tail of singleton categories where a "0%" is one item.
        "by_category_n_ge_4": {
            c: {"n": len(v), "acc": sum(v) / len(v)}
            for c, v in sorted(by_cat.items()) if len(v) >= 4
        },
        "git_commit": git_commit(),
        "config": vars(args),
    }

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "rows.json").write_text(json.dumps(rows, indent=2))
    (out / "summary.json").write_text(json.dumps(summary, indent=2))

    lo, hi = summary["exact"]["wilson95"]
    print("\n" + "=" * 60)
    print(f"exact       : {n_exact}/{n} = {n_exact/n:.1%}  (95% CI {lo:.1%}-{hi:.1%})")
    print(f"first_token : {n_first}/{n} = {n_first/n:.1%}")
    print(f"single-token answers: {len(single)}/{n}")
    print("=" * 60)
    print("Compare against the threshold you committed BEFORE this run.")


if __name__ == "__main__":
    main()
