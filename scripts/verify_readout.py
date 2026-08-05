"""Stage B2 — does the lens surface the unspoken intermediate?

Run BEFORE Control A. Control A ablates the top-k directions and expects two-hop
reasoning to collapse; that only follows if those directions contain the
intermediate. This checks the premise.

Cheap: one forward pass per prompt, a few minutes, ~1 unit.

Usage:
    python verify_readout.py --model Qwen/Qwen3-8B \
        --lens-file qwen3-8b/jlens/Salesforce-wikitext/Qwen3-8B_jacobian_lens.pt \
        --data jacobian-lens/data/experiments/probe-swap.json \
        --out results/raw/readout_qwen3-8b/
"""
from __future__ import annotations
import argparse, json, random, time
from dataclasses import asdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import jlens
from jlens.lens import JacobianLens
from ablation.harness import prepare_lens
from band.readout import measure_readout, summarise, verdict

LENS_REPO = "neuronpedia/jacobian-lens"


@torch.no_grad()
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lens-file", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--band-start", type=int, default=20)   # prereg §2
    ap.add_argument("--band-end", type=int, default=31)
    ap.add_argument("--scan-from", type=int, default=0,
                    help="also measure outside the band, to see where content peaks")
    ap.add_argument("--scan-step", type=int, default=2)
    ap.add_argument("--skip-first", type=int, default=4)
    ap.add_argument("--max-seq-len", type=int, default=128)
    ap.add_argument("--seed", type=int, default=20260728)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=getattr(torch, args.dtype),
                                              device_map=device)
    lm = jlens.from_hf(hf, AutoTokenizer.from_pretrained(args.model))
    lens = prepare_lens(JacobianLens.from_pretrained(LENS_REPO, filename=args.lens_file), device)
    wu = lm._lm_head.weight.detach()

    items = json.load(open(args.data))["items"]
    band = list(range(args.band_start, args.band_end + 1))
    scan = sorted(set(range(args.scan_from, max(lens.source_layers) + 1, args.scan_step)) | set(band))
    print(f"{len(items)} prompts; measuring {len(scan)} layers "
          f"(band {band[0]}..{band[-1]} plus a scan)\n")

    rng = random.Random(args.seed)
    records = []
    t0 = time.perf_counter()
    for i, it in enumerate(items, 1):
        # foil: another prompt's intermediate. Controls for the lens simply
        # favouring common words.
        foil = rng.choice([x for x in items if x["intermediate"] != it["intermediate"]])
        p = it["prompt"].rstrip()
        records += measure_readout(lm, lens, wu, p, it["intermediate"], scan,
                                   name=it["name"], skip_first=args.skip_first,
                                   max_seq_len=args.max_seq_len)
        records += measure_readout(lm, lens, wu, p, foil["intermediate"], scan,
                                   name=it["name"], is_foil=True,
                                   skip_first=args.skip_first, max_seq_len=args.max_seq_len)
        if i % 15 == 0:
            print(f"  [{i}/{len(items)}] {time.perf_counter()-t0:.0f}s")

    summ = summarise(records, scan)
    v = verdict(summ, band)

    print(f"\n{'layer':>6} {'true top10':>11} {'foil top10':>11} {'gap':>8} "
          f"{'med rank':>9} {'loading':>9} {'foil load':>10}")
    for l in scan:
        r = summ["per_layer"].get(l, {})
        if "true" not in r or "foil" not in r:
            continue
        mark = " *" if args.band_start <= l <= args.band_end else "  "
        print(f"{l:>4}{mark} {r['true']['top10']:>11.1%} {r['foil']['top10']:>11.1%} "
              f"{r['top10_gap']:>+8.1%} {r['true']['median_rank']:>9} "
              f"{r['true']['mean_max_loading']:>9.3f} {r['foil']['mean_max_loading']:>10.3f}")
    print("  (* = inside the pre-registered band)")

    print(f"\nVERDICT: {v['verdict']}")
    print(f"  {v.get('reading','')}")

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    (out / "readout_records.json").write_text(
        json.dumps([asdict(r) for r in records], indent=2))
    (out / "readout_summary.json").write_text(
        json.dumps({"summary": summ, "verdict": v, "band": band,
                    "config": vars(args)}, indent=2, default=str))
    print(f"\nwrote {out}/readout_summary.json")


if __name__ == "__main__":
    main()
