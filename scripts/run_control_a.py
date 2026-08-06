"""Control A — the full run. Degrading side + intact side + criteria.

Governed by `preregistration/prereg_controlA.md`, signed 2026-07-28.
Implements `DECISION_control_A.md`.

Nothing here decides whether Control A passed. It computes the pre-registered
quantities and prints them against the pre-registered thresholds. The call is
the user's (AI collaboration guide §2, row 12).

Usage:
    python run_control_a.py \
        --model Qwen/Qwen3-8B \
        --lens-file qwen3-8b/jlens/Salesforce-wikitext/Qwen3-8B_jacobian_lens.pt \
        --data jacobian-lens/data/experiments/probe-swap.json \
        --out results/raw/controlA_qwen3-8b/
"""
from __future__ import annotations

import argparse, json, subprocess, time
from collections import defaultdict
from dataclasses import asdict
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

import jlens
from jlens.examples import load_wikitext_prompts
from jlens.lens import JacobianLens
from ablation.harness import AblationSpec, build_cache, prepare_lens, run_ablation
from ablation.intact import aggregate, diagnose, score_intact

LENS_REPO = "neuronpedia/jacobian-lens"

# --- prereg §2 and §3. Shared start; heavy additionally at two other starts. ---
STRENGTHS: dict[str, tuple[int, ...]] = {
    "light":       tuple(range(20, 24)),   # 4 layers
    "medium":      tuple(range(20, 28)),   # 8
    "heavy":       tuple(range(20, 32)),   # 12  <- primary
    "heavy-early": tuple(range(15, 32)),   # 17  sensitivity: under-ablation
    "heavy-late":  tuple(range(24, 32)),   # 8   sensitivity: over-ablation
    "heavy-paper": tuple(range(13, 32)),   # 19  Amendment 003
}

#: Band-start dose-response, ordered from the highest start to the lowest
#: (69% -> 37% of depth). Amendment 003 pre-registers the prediction that IF
#: under-ablation is real, the effect grows monotonically down this list; a flat
#: curve means the band start is not load-bearing.
START_ORDER = ("heavy-late", "heavy", "heavy-early", "heavy-paper")
PRIMARY = "heavy"

# prereg §4: relative reduction, dose-response gap, intact-side floor
REL_REDUCTION_REQUIRED = 0.50   # prereg §4; Amendment 002 moves the absolute
                                # target from <=32.2% to <=34.3% (clean 68.5%)
DOSE_GAP_PP = 10.0
PRESERVED_TOP1 = 0.90


def norm(prompt: str, answer: str) -> tuple[str, str]:
    """The trailing-whitespace fix: 29 of 90 prompts end with a space."""
    return prompt.rstrip(), " " + answer.strip()


def build_grid(n_draws: int, base_seed: int) -> list[tuple[str, AblationSpec]]:
    """Candidate + matched controls at every strength (prereg §4.1: 19 draws)."""
    grid: list[tuple[str, AblationSpec]] = [
        ("clean", AblationSpec(layers=(), k=0, selector="none"))
    ]
    for name, layers in STRENGTHS.items():
        grid.append((f"{name}|topk", AblationSpec(layers=layers, k=10, selector="topk")))
        grid.append((f"{name}|next_k", AblationSpec(layers=layers, k=10, selector="next_k")))
        for d in range(n_draws):
            seed = base_seed + 1000 * d + len(layers)
            grid.append((f"{name}|random_lens|{d}",
                         AblationSpec(layers=layers, k=10, selector="random_lens", seed=seed)))
            grid.append((f"{name}|random_iso|{d}",
                         AblationSpec(layers=layers, k=10, selector="random_iso", seed=seed)))
    return grid


@torch.no_grad()
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--lens-file", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--n-draws", type=int, default=19)      # prereg §4.1
    ap.add_argument("--base-seed", type=int, default=20260728)
    ap.add_argument("--intact-passages", type=int, default=20)
    ap.add_argument("--intact-random-sample", type=int, default=5,
                    help="random draws given the intact side, at the primary band only. "
                         "The intact side exists to establish SELECTIVITY of the "
                         "candidate; running it on all 19x5 random draws would "
                         "roughly double runtime for little added evidence.")
    ap.add_argument("--max-seq-len", type=int, default=128)
    ap.add_argument("--skip-first", type=int, default=4)
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = getattr(torch, args.dtype)

    print(f"loading {args.model} ...")
    hf = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype, device_map=device)
    tok = AutoTokenizer.from_pretrained(args.model)
    lm = jlens.from_hf(hf, tok)
    lens = prepare_lens(JacobianLens.from_pretrained(LENS_REPO, filename=args.lens_file), device)
    wu = lm._lm_head.weight.detach()
    print(f"  n_layers={lm.n_layers} d_model={lm.d_model}")

    # ---- data ------------------------------------------------------------
    items = json.load(open(args.data))["items"]
    for it in items:
        p, a = norm(it["prompt"], it["answer"])
        it["_prompt"], it["_answer"] = p, a
        it["_ans_ids"] = tok(a, add_special_tokens=False).input_ids
        it["_single"] = len(it["_ans_ids"]) == 1
    single = [it for it in items if it["_single"]]
    print(f"  {len(items)} prompts; {len(single)} with single-token answers "
          f"(primary eval, prereg amendment 002)")

    passages = load_wikitext_prompts(args.intact_passages)
    print(f"  {len(passages)} WikiText passages for the intact side")

    # ---- caches: build once, reuse across all conditions ------------------
    all_layers = tuple(sorted({l for ls in STRENGTHS.values() for l in ls}))
    print(f"\nbuilding caches over layers {all_layers[0]}..{all_layers[-1]} ...")
    t0 = time.perf_counter()
    deg_cache = {it["name"]: build_cache(lm, lens, it["_prompt"], all_layers,
                                         k_max=20, max_seq_len=args.max_seq_len)
                 for it in items}
    int_cache = [build_cache(lm, lens, p, all_layers, k_max=20,
                             max_seq_len=args.max_seq_len) for p in passages]
    print(f"  {time.perf_counter()-t0:.0f}s")

    grid = build_grid(args.n_draws, args.base_seed)
    intact_for = {f"{s}|topk" for s in STRENGTHS} | {f"{s}|next_k" for s in STRENGTHS} | {"clean"}
    intact_for |= {f"{PRIMARY}|random_lens|{d}" for d in range(args.intact_random_sample)}
    intact_for |= {f"{PRIMARY}|random_iso|{d}" for d in range(args.intact_random_sample)}
    print(f"\n{len(grid)} conditions; intact side on {len(intact_for)} of them\n")

    commit = git_commit()
    results: dict[str, dict] = {}

    for i, (name, spec) in enumerate(grid, 1):
        f = out / f"{name.replace('|','__')}.json"
        if f.exists():
            results[name] = json.loads(f.read_text()); print(f"[skip] {name}"); continue

        t = time.perf_counter()
        by_cat, strict_hits, first_hits, strict_n = defaultdict(list), 0, 0, 0
        for it in items:
            r = run_ablation(lm, lens, wu, it["_prompt"], spec,
                             cache=deg_cache[it["name"]], max_seq_len=args.max_seq_len)
            pred = int(r.logits[-1].argmax())
            first = pred == it["_ans_ids"][0]
            first_hits += first
            if it["_single"]:
                strict = tok.decode([pred]).strip().lower() == it["_answer"].strip().lower()
                strict_hits += strict; strict_n += 1
                by_cat[it["category"]].append(strict)

        rec = {
            "condition": name, "spec": asdict(spec), "git_commit": commit,
            "strict_single": {"k": strict_hits, "n": strict_n, "acc": strict_hits / strict_n},
            "first_token_all": {"k": first_hits, "n": len(items), "acc": first_hits / len(items)},
            "by_category": {c: {"n": len(v), "acc": sum(v) / len(v)}
                            for c, v in sorted(by_cat.items()) if len(v) >= 4},
            "seconds": round(time.perf_counter() - t, 1),
        }

        if name in intact_for:
            rec["intact"] = aggregate([
                score_intact(run_ablation(lm, lens, wu, p, spec, cache=c,
                                          max_seq_len=args.max_seq_len),
                             skip_first=args.skip_first)
                for p, c in zip(passages, int_cache)])

        f.write_text(json.dumps(rec, indent=2))
        results[name] = rec
        it1 = rec.get("intact", {}).get("top1_match")
        print(f"[{i:>3}/{len(grid)}] {name:<28} strict={rec['strict_single']['acc']:.3f}"
              + (f"  intact_top1={it1:.3f}" if it1 is not None else "")
              + f"  ({rec['seconds']}s)")

    (out / "_all_results.json").write_text(json.dumps(results, indent=2))
    report(results, args, out)


def report(results: dict, args, out: Path) -> None:
    """Print the pre-registered quantities against the pre-registered thresholds."""
    clean = results["clean"]["strict_single"]["acc"]
    print("\n" + "=" * 74)
    print(f"CONTROL A — clean strict (single-token subset): {clean:.1%}")
    print("=" * 74)
    print(f"{'strength':<14}{'candidate':>10}{'drop':>8}{'rel':>8}"
          f"{'next_k':>9}{'rnd_lens max':>14}{'rnd_iso max':>13}{'beats all':>11}")

    summary = {}
    for s in STRENGTHS:
        cand = results[f"{s}|topk"]["strict_single"]["acc"]
        nxt = results[f"{s}|next_k"]["strict_single"]["acc"]
        rl = [results[k]["strict_single"]["acc"] for k in results if k.startswith(f"{s}|random_lens")]
        ri = [results[k]["strict_single"]["acc"] for k in results if k.startswith(f"{s}|random_iso")]
        drop, rel = clean - cand, (clean - cand) / clean if clean else 0.0
        beats_lens = cand < min(rl) if rl else None
        beats_iso = cand < min(ri) if ri else None
        beats = bool(beats_lens) and bool(beats_iso)
        # p is reported PER NULL, not pooled. random_lens draws from the lens
        # dictionary and random_iso draws isotropic directions; they are
        # different null distributions and are not exchangeable with each other,
        # so 1/(19+19+1) would not be a valid combined p-value.
        summary[s] = {"candidate": cand, "drop": drop, "rel_reduction": rel,
                      "next_k": nxt, "random_lens": rl, "random_iso": ri,
                      "beats_all_random_lens": beats_lens,
                      "beats_all_random_iso": beats_iso,
                      "beats_all_random": beats,
                      "p_vs_random_lens": 1 / (len(rl) + 1) if beats_lens else None,
                      "p_vs_random_iso": 1 / (len(ri) + 1) if beats_iso else None}
        print(f"{s:<14}{cand:>9.1%}{drop:>8.1%}{rel:>8.1%}{nxt:>9.1%}"
              f"{(max(rl) if rl else float('nan')):>14.1%}"
              f"{(max(ri) if ri else float('nan')):>13.1%}{str(beats):>11}")

    h = summary[PRIMARY]
    lo = summary["light"]
    print("\n--- prereg §4 criteria ---")
    c1 = h["rel_reduction"] >= REL_REDUCTION_REQUIRED
    c2 = (h["drop"] - lo["drop"]) * 100 >= DOSE_GAP_PP
    c3 = all(summary[s]["beats_all_random"] for s in STRENGTHS)
    intact = results.get(f"{PRIMARY}|topk", {}).get("intact", {})
    t1 = intact.get("top1_match")
    c4 = t1 is not None and t1 >= PRESERVED_TOP1
    print(f"  substantial degradation (>={REL_REDUCTION_REQUIRED:.0%} rel) : "
          f"{h['rel_reduction']:.1%}  {'PASS' if c1 else 'FAIL'}")
    print(f"  dose-response (heavy-light >= {DOSE_GAP_PP}pp)        : "
          f"{(h['drop']-lo['drop'])*100:+.1f}pp  {'PASS' if c2 else 'FAIL'}")
    print(f"  candidate beats every random draw               : {'PASS' if c3 else 'FAIL'}")
    print(f"  intact top-1 >= {PRESERVED_TOP1:.0%}                          : "
          + (f"{t1:.1%}  {'PASS' if c4 else 'FAIL'}" if t1 is not None else "n/a"))

    if t1 is not None:
        d = diagnose(intact, degrading_drop=h["drop"], preserved_top1=PRESERVED_TOP1)
        print(f"\n  selectivity verdict: {d['verdict']}")
        print(f"  {d['reading']}")

    print("\n--- band-start dose-response (prereg §3 + Amendment 003) ---")
    depth = STRENGTHS[PRIMARY][-1] + 4          # n_layers - 1 = 35 for Qwen3-8B
    rels = []
    for nm in START_ORDER:
        st = STRENGTHS[nm][0]
        rels.append(summary[nm]["rel_reduction"])
        print(f"  {nm:<13} L{st:>2}..{STRENGTHS[nm][-1]}  start {100*st/depth:>3.0f}% depth  "
              f"width {len(STRENGTHS[nm]):>2}  rel reduction {summary[nm]['rel_reduction']:>7.1%}")

    mono = all(rels[i] <= rels[i + 1] + 1e-9 for i in range(len(rels) - 1))
    spread = max(rels) - min(rels)
    print(f"\n  Amendment 003 predicted: heavy-late < heavy < heavy-early < heavy-paper")
    print(f"  monotonic increasing as start moves down : {mono}")
    print(f"  spread across the four starts            : {spread:.1%}")
    if mono and spread >= 0.10:
        print("  -> consistent with UNDER-ABLATION: the primary band leaves")
        print("     recoverable content below L20, as Stage B2's readout suggested.")
    elif spread < 0.10:
        print("  -> band start is NOT load-bearing. This is the stronger outcome:")
        print("     it can be stated across four starts spanning 69%->37% of depth.")
    else:
        print("  -> non-monotonic. Report the pattern; do not pick a start by result.")

    print("\n  width control: medium (L20-27) and heavy-late (L24-31) are both 8 layers")
    print(f"    medium {summary['medium']['rel_reduction']:.1%} vs "
          f"heavy-late {summary['heavy-late']['rel_reduction']:.1%}"
          "   <- isolates start position from width")

    print("\n--- light, against its pre-registered prediction (§2.1) ---")
    print(f"  light rel reduction {lo['rel_reduction']:.1%}. Prereg predicted light may "
          "show little effect\n  because 8 downstream layers can re-establish content. "
          "A flat curve is therefore\n  WEAK evidence against the workspace under this nesting.")

    (out / "_summary.json").write_text(json.dumps(
        {"clean": clean, "strengths": summary,
         "criteria": {"substantial": c1, "dose_response": c2,
                      "beats_random": c3, "intact": c4},
         "band_start_dose_response": {
             "order": list(START_ORDER),
             "rel_reductions": rels,
             "monotonic": mono,
             "spread": spread},
         "amendments": ["002 strict on 73 single-token items",
                        "003 heavy-paper L13-31 added"],
         "config": vars(args)}, indent=2))
    print(f"\nwrote {out/'_summary.json'}")
    print("\nThe pass/partial/fail call is the user's (prereg §4). "
          "Log it as a gate decision (G0).")


if __name__ == "__main__":
    main()
