"""Stage B — derive the workspace band for this model.

The paper's band (~L38-92 on a reindexed 0-100 scale) is Sonnet 4.5's. Every
ablation experiment reports over the band, and light/medium/heavy differ only
in its width. Nothing in the released code computes one, and no step for
deriving it exists in the proposal or the execution guide. This is that step.

Corpus: WikiText-103, via jlens' own loader. NOT the probe-swap prompts —
deriving the band on the eval you are about to ablate would contaminate it.
WikiText also matches what the published lens was fitted on.

Output is FOUR CURVES, not a verdict. `propose_band` gives a first pass with
explicit, arbitrary thresholds; read the curves against it.

Usage:
    python derive_band.py --model Qwen/Qwen3-8B \
        --lens-file qwen3-8b/jlens/Salesforce-wikitext/Qwen3-8B_jacobian_lens.pt \
        --out results/raw/band_qwen3-8b/
"""
from __future__ import annotations
import argparse, json, time
from dataclasses import asdict

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import jlens
from jlens.examples import load_wikitext_prompts
from jlens.lens import JacobianLens
from ablation.harness import prepare_lens
from band.derive import layer_stats, propose_band

LENS_REPO = "neuronpedia/jacobian-lens"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lens-file", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--n-prompts", type=int, default=20)
    ap.add_argument("--topk", type=int, default=5)
    ap.add_argument("--skip-first", type=int, default=4,
                    help="positions dropped from each statistic. Low, per A.7: "
                         "position masking yielded no meaningful improvement, so "
                         "there is no reason to inherit the code default of 16")
    ap.add_argument("--max-seq-len", type=int, default=128)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = getattr(torch, args.dtype)

    print(f"loading {args.model} ...")
    hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype, device_map=device)
    tok = AutoTokenizer.from_pretrained(args.model)
    lm = jlens.from_hf(hf, tok)
    print(f"  n_layers={lm.n_layers} d_model={lm.d_model}")

    lens = JacobianLens.from_pretrained(LENS_REPO, filename=args.lens_file)
    lens = prepare_lens(lens, device)   # device only; the class holds float32 by design
    print(f"  lens source_layers {min(lens.source_layers)}..{max(lens.source_layers)}")

    prompts = load_wikitext_prompts(args.n_prompts)
    print(f"  {len(prompts)} WikiText passages")

    wu = lm._lm_head.weight.detach()
    t0 = time.perf_counter()
    stats = layer_stats(lens, lm, prompts, wu, k=args.topk,
                        skip_first=args.skip_first, max_seq_len=args.max_seq_len,
                        seed=args.seed)
    print(f"  computed in {time.perf_counter()-t0:.0f}s\n")

    print(f"{'layer':>5} {'depth%':>7} {'kurtosis':>10} {'topk_acc':>9} {'autocorr':>9} {'eff_dim':>8}")
    for s in stats:
        print(f"{s.layer:>5} {100*s.layer/(lm.n_layers-1):>6.0f}% {s.kurtosis:>10.3f} "
              f"{s.topk_acc:>9.3f} {s.autocorr:>9.3f} {s.eff_dim:>8.2f}")

    start, end = propose_band(stats)
    d = lm.n_layers - 1
    print(f"\nPROPOSED BAND: layers {start}..{end}  "
          f"({100*start/d:.0f}%-{100*end/d:.0f}% of depth)")
    print(f"  paper's band for Sonnet 4.5 was ~38%-92% of depth, for reference only")
    print("\n  Thresholds used: kurtosis > 25% of peak (start), "
          "topk_acc > 50% of peak (end).")
    print("  These are ARBITRARY. Read the curves before accepting the proposal.")

    import pathlib
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "band_stats.json").write_text(json.dumps({
        "model": args.model, "n_layers": lm.n_layers, "d_model": lm.d_model,
        "lens_file": args.lens_file, "config": vars(args),
        "stats": [asdict(s) for s in stats],
        "proposed_band": {"start": start, "end": end,
                          "kurt_frac": 0.25, "acc_frac": 0.50},
    }, indent=2))
    print(f"\nwrote {out/'band_stats.json'}")


if __name__ == "__main__":
    main()
