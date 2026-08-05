"""Coarse-output intact tasks for Control A — completing DECISION_control_A §4.5.

The first Control A run measured the intact side only on WikiText next-token
match, which failed (top-1 0.577 at heavy). That is the most sensitive of the
measures §4.5 specified. This runs the coarse ones the paper actually reported
as unaffected.

Reported as SUPPLEMENTARY. The pre-registered criterion (prereg §4: WikiText
top-1 >= 0.90) failed and that stands; nothing here changes it. These tasks were
named in the signed spec from the start, so running them is completing an
under-delivered spec, not shopping for a measure that passes.

Usage:
    python run_intact_tasks.py --model Qwen/Qwen3-8B \
        --lens-file qwen3-8b/jlens/Salesforce-wikitext/Qwen3-8B_jacobian_lens.pt \
        --out results/raw/controlA_qwen3-8b/intact_tasks/
"""
from __future__ import annotations
import argparse, json, time
from dataclasses import asdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import jlens
from jlens.lens import JacobianLens
from ablation.harness import AblationSpec, prepare_lens
from ablation.tasks import check_headroom, load_mmlu, load_sst2, score_task, summarise

LENS_REPO = "neuronpedia/jacobian-lens"

# Same bands as the signed prereg + Amendment 003.
STRENGTHS = {
    "light":       tuple(range(20, 24)),
    "medium":      tuple(range(20, 28)),
    "heavy":       tuple(range(20, 32)),
    "heavy-early": tuple(range(15, 32)),
    "heavy-late":  tuple(range(24, 32)),
    "heavy-paper": tuple(range(13, 32)),
}


def build_specs(n_random: int, base_seed: int) -> dict[str, AblationSpec]:
    """Candidates at every strength, plus matched randoms at the primary band.

    Randoms only at `heavy`: they exist here to show what a same-size,
    same-layer ablation does to a coarse task, and repeating that at all six
    strengths would multiply runtime without adding evidence.
    """
    specs = {"clean": AblationSpec(layers=(), k=0, selector="none")}
    for name, layers in STRENGTHS.items():
        specs[f"{name}|topk"] = AblationSpec(layers=layers, k=10, selector="topk")
    specs["heavy|next_k"] = AblationSpec(layers=STRENGTHS["heavy"], k=10, selector="next_k")
    for d in range(n_random):
        seed = base_seed + 1000 * d
        specs[f"heavy|random_lens|{d}"] = AblationSpec(
            layers=STRENGTHS["heavy"], k=10, selector="random_lens", seed=seed)
        specs[f"heavy|random_iso|{d}"] = AblationSpec(
            layers=STRENGTHS["heavy"], k=10, selector="random_iso", seed=seed)
    return specs


@torch.no_grad()
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lens-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--n-items", type=int, default=150)
    ap.add_argument("--n-random", type=int, default=5)
    ap.add_argument("--base-seed", type=int, default=20260729)
    ap.add_argument("--max-seq-len", type=int, default=512)
    ap.add_argument("--tasks", default="mmlu,sst2")
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=getattr(torch, args.dtype),
                                              device_map=device)
    lm = jlens.from_hf(hf, AutoTokenizer.from_pretrained(args.model))
    lens = prepare_lens(JacobianLens.from_pretrained(LENS_REPO, filename=args.lens_file), device)
    wu = lm._lm_head.weight.detach()

    specs = build_specs(args.n_random, args.base_seed)
    all_layers = tuple(sorted({l for ls in STRENGTHS.values() for l in ls}))
    print(f"{len(specs)} conditions; layers {all_layers[0]}..{all_layers[-1]}\n")

    loaders = {"mmlu": load_mmlu, "sst2": load_sst2}
    everything = {}

    for tname in args.tasks.split(","):
        tname = tname.strip()
        print(f"=== {tname} ===")
        task = loaders[tname](args.n_items, seed=args.base_seed)
        task.tokenise(lm.tokenizer)
        print(f"  {len(task.prompts)} items, chance {task.chance:.0%}")

        t0 = time.perf_counter()
        res = score_task(lm, lens, wu, task, specs, all_layers=all_layers,
                         max_seq_len=args.max_seq_len)
        summ = summarise(res, task)
        print(f"  {time.perf_counter()-t0:.0f}s\n")

        h = summ["headroom"]
        print(f"  HEADROOM: {h['reading']}")
        if not h["usable"]:
            print("  >>> This task is EXCLUDED from the intact verdict.\n")
        else:
            print()
            print(f"  {'condition':<26}{'acc':>8}{'ret(raw)':>10}{'ret(>chance)':>14}{'flips':>8}")
            print(f"  {'clean':<26}{summ['clean']:>8.3f}{'-':>10}{'-':>14}{'-':>8}")
            for n, c in summ["conditions"].items():
                if n.startswith("heavy|random") and not n.endswith("|0"):
                    continue                      # print one of each for brevity
                print(f"  {n:<26}{c['acc']:>8.3f}{c['retention_raw']:>10.3f}"
                      f"{c['retention_above_chance']:>14.3f}{c['answer_flip_rate']:>8.3f}")
            rl = [summ["conditions"][f"heavy|random_lens|{i}"]["retention_above_chance"]
                  for i in range(args.n_random)]
            ri = [summ["conditions"][f"heavy|random_iso|{i}"]["retention_above_chance"]
                  for i in range(args.n_random)]
            print(f"\n  mean retention(>chance): random_lens {sum(rl)/len(rl):.3f}  "
                  f"random_iso {sum(ri)/len(ri):.3f}  "
                  f"candidate {summ['conditions']['heavy|topk']['retention_above_chance']:.3f}")
        everything[tname] = {"summary": summ, "raw": res}
        (out / f"{tname}.json").write_text(json.dumps(everything[tname], indent=2))

    (out / "_intact_tasks.json").write_text(json.dumps(
        {"results": everything, "config": vars(args),
         "note": "SUPPLEMENTARY. The pre-registered intact criterion "
                 "(WikiText top-1 >= 0.90) failed at 0.577 and that stands."},
        indent=2))
    print(f"\nwrote {out}/_intact_tasks.json")
    print("\nRead alongside the WikiText result, not instead of it. Corpus next-token")
    print("prediction and constrained multiple choice answer different questions;")
    print("a gap between them is a finding about the ablation's shape, not a tie-break.")


if __name__ == "__main__":
    main()
