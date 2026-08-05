"""Stage B2 — readout verification.

Control A ablates the top-k J-lens directions and expects two-hop reasoning to
collapse. That expectation rests on an assumption nothing has yet checked:

    that the top-k directions actually CONTAIN the unspoken intermediate.

For "the language spoken in the country where the Amazon River ends", the paper's
claim is that `Brazil` sits in the readout before the model says `Portuguese`.
If it does not — if the readout surfaces something else — then ablation removes
*something*, but not the thing the theory says matters, and a null becomes
uninterpretable in exactly the way proposal §4.5 warns about ("readout too weak"
vs "phenomenon absent").

`probe-swap.json` carries an `intermediate` field for all 90 prompts, and **none
of the 90 intermediates appears anywhere in its own prompt**, so this is a clean
test of unspoken content rather than an echo of the input.

Two measures, both from the paper:

  rank      position of the intermediate in the lens readout. Low = surfaced.
  loading   cosine similarity between the residual stream and the intermediate's
            lens vector. The paper defines a concept's *workspace loading* this
            way and finds it predicts whether interventions on that concept
            work — number words load poorly and intervene poorly. If your
            intermediates load poorly, that diagnoses a null in advance rather
            than after the fact.

**Foil control.** For each prompt the same measures are computed for a randomly
chosen *other* prompt's intermediate. Without it, a good rank could simply mean
the lens favours common words. The true-vs-foil gap is the actual evidence.

NOTE ON NAMING: this is Phase 0 instrument verification on a language model. It
is not Phase 2's R-space identification, which will live in `src/readout/` and
is a different thing entirely.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Sequence

import torch

from jlens.hooks import ActivationRecorder

from ablation.directions import lens_vectors


@dataclass
class ReadoutRecord:
    """Readout measurements for one prompt at one layer."""

    name: str
    layer: int
    target_token: str
    n_target_tokens: int
    best_rank: int            # best (lowest) rank across positions; 0 = top-1
    best_position: int
    max_loading: float        # cosine sim, best across positions
    mean_loading: float
    is_foil: bool


@torch.no_grad()
def measure_readout(
    model: Any, lens: Any, unembed_weight: torch.Tensor,
    prompt: str, target: str, layers: Sequence[int],
    *, name: str = "", is_foil: bool = False,
    skip_first: int = 4, max_seq_len: int = 128,
) -> list[ReadoutRecord]:
    """Rank and workspace loading of ``target`` in the readout at each layer.

    Args:
        target: the concept word. A leading space is added before tokenising,
            matching how it would appear mid-text.
    """
    tok = model.tokenizer
    tgt = " " + target.strip()
    # Real HF tokenizers take add_special_tokens; the LensModel protocol does not
    # require it (tests/tiny.py's toy tokenizer has no such kwarg), so fall back.
    # A leading BOS from the fallback path is dropped below.
    try:
        ids_t = tok(tgt, add_special_tokens=False).input_ids
    except TypeError:
        ids_t = tok(tgt).input_ids
        if torch.is_tensor(ids_t):
            ids_t = ids_t[0].tolist()
        bos = getattr(tok, "bos_token_id", None)
        if bos is not None and ids_t and ids_t[0] == bos:
            ids_t = ids_t[1:]
    if torch.is_tensor(ids_t):
        ids_t = ids_t[0].tolist() if ids_t.dim() > 1 else ids_t.tolist()
    if not ids_t:
        raise ValueError(f"target {target!r} tokenised to nothing")
    # The J-lens is vocabulary-indexed and only represents single tokens
    # (paper §A.9). For a multi-token target only the first token is
    # representable; n_target_tokens is recorded so those can be split out.
    tid = torch.tensor([ids_t[0]])

    ids = model.encode(prompt, max_length=max_seq_len)
    final = model.n_layers - 1
    with ActivationRecorder(model.layers, sorted({*layers, final})) as rec:
        model.forward(ids)
        acts = {i: rec.activations[i][0].detach() for i in sorted({*layers, final})}

    out = []
    for layer in layers:
        h = acts[layer][skip_first:].float()
        if h.shape[0] == 0:
            continue
        logits = model.unembed(lens.transport(h, layer)).float()

        # rank = how many tokens score strictly higher than the target
        tgt_score = logits[:, tid[0]]
        ranks = (logits > tgt_score[:, None]).sum(-1)
        best_pos = int(ranks.argmin())
        best_rank = int(ranks[best_pos])

        # workspace loading: cosine(residual, the target's lens vector)
        v = lens_vectors(unembed_weight, lens.jacobians[layer].to(h.device),
                         tid.to(h.device))[0].float()
        v = v / v.norm().clamp_min(1e-12)
        cos = (h / h.norm(dim=-1, keepdim=True).clamp_min(1e-12)) @ v

        out.append(ReadoutRecord(
            name=name, layer=layer, target_token=target,
            n_target_tokens=len(ids_t), best_rank=best_rank,
            best_position=best_pos + skip_first,
            max_loading=float(cos.max()), mean_loading=float(cos.mean()),
            is_foil=is_foil,
        ))
    return out


def summarise(records: Sequence[ReadoutRecord], layers: Sequence[int],
              ks: Sequence[int] = (1, 5, 10, 25, 100)) -> dict[str, Any]:
    """Per-layer readout accuracy and loading, true vs foil."""
    out: dict[str, Any] = {"layers": list(layers), "k_values": list(ks), "per_layer": {}}
    for layer in layers:
        row: dict[str, Any] = {}
        for tag, foil in (("true", False), ("foil", True)):
            rs = [r for r in records if r.layer == layer and r.is_foil == foil]
            if not rs:
                continue
            row[tag] = {
                "n": len(rs),
                "median_rank": sorted(r.best_rank for r in rs)[len(rs) // 2],
                "mean_max_loading": sum(r.max_loading for r in rs) / len(rs),
                **{f"top{k}": sum(r.best_rank < k for r in rs) / len(rs) for k in ks},
            }
        if "true" in row and "foil" in row:
            row["top10_gap"] = row["true"]["top10"] - row["foil"]["top10"]
            row["loading_gap"] = row["true"]["mean_max_loading"] - row["foil"]["mean_max_loading"]
        out["per_layer"][layer] = row
    return out


def verdict(summary: dict[str, Any], band: Sequence[int],
            *, min_top10: float = 0.30, min_gap: float = 0.15) -> dict[str, Any]:
    """Does the readout surface intermediates inside the band?

    Thresholds are judgment calls, exposed so the values used are recorded. The
    paper gives no numeric criterion for "the readout works".

    Args:
        min_top10: fraction of prompts whose intermediate must reach the top 10.
        min_gap: how far true must exceed foil on that fraction. This is the
            one that matters — a high top-10 rate with no gap over foils means
            the lens favours common words, not that it surfaced the concept.
    """
    inband = [summary["per_layer"][l] for l in band if l in summary["per_layer"]]
    inband = [r for r in inband if "true" in r and "foil" in r]
    if not inband:
        return {"verdict": "NO DATA"}

    best = max(inband, key=lambda r: r["top10_gap"])
    peak_top10 = max(r["true"]["top10"] for r in inband)
    peak_gap = best["top10_gap"]

    d = {"peak_true_top10": peak_top10, "peak_gap_over_foil": peak_gap,
         "min_top10": min_top10, "min_gap": min_gap}
    if peak_top10 >= min_top10 and peak_gap >= min_gap:
        d["verdict"] = "READOUT SURFACES INTERMEDIATES"
        d["reading"] = (
            f"At its best band layer the intermediate reaches the top 10 for "
            f"{peak_top10:.0%} of prompts, {peak_gap:+.0%} above matched foils. "
            "The premise Control A rests on is supported: the top-k directions "
            "do contain the unspoken intermediate. This is itself a replication "
            "of one of the paper's core claims on an open model."
        )
    elif peak_gap < min_gap:
        d["verdict"] = "NO SIGNAL OVER FOILS"
        d["reading"] = (
            f"True intermediates rank no better than foils (gap {peak_gap:+.0%}). "
            "Whatever the readout is surfacing, it is not prompt-specific "
            "content. Ablating the top-k would remove *something*, but not the "
            "intermediate, and a Control A null could not distinguish 'no "
            "workspace' from 'readout too weak' (proposal §4.5). Report this "
            "and treat any Control A result as bounded by it."
        )
    else:
        d["verdict"] = "WEAK — signal present but below threshold"
        d["reading"] = (
            f"Intermediates beat foils by {peak_gap:+.0%} but reach the top 10 "
            f"for only {peak_top10:.0%} of prompts. The readout carries real "
            "content and is weaker than the paper's. Control A remains "
            "interpretable, with its power bounded by this."
        )
    return d
