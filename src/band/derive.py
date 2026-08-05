"""Workspace-band derivation.

The paper's band (~L38-92 on a reindexed 0-100 scale) is Sonnet 4.5's. Every
ablation experiment reports over the band, so it must be derived per model
before ablation can run. Nothing in the released code computes it.

Four J-lens-derived statistics, per the paper:

  kurtosis    excess kurtosis of the readout logit distribution. ~0 through the
              early block, rises from ~1/3 depth. MARKS THE START.
  topk_acc    top-k accuracy of the lens at predicting the model's actual next
              token. ~0 early, ticks up at band start, jumps steeply in the
              final layers. MARKS THE END (motor onset).
  autocorr    autocorrelation of the top-1 lens token across nearby positions,
              against a position-shuffled null. Persistence of abstract content.
  eff_dim     effective linear dimensionality of ``W_U J_l``. Small early, rises
              sharply at band onset, again at the motor transition.

CAVEAT, stated by the paper itself: all four derive from the J-lens, so layer
effects could be artifacts of the method rather than facts about the model. The
paper answers this with the ignition experiment, which uses no lens at all. That
is not implemented here. For Phase 0 (a language model, replicating a published
band) these four are adequate; for Phase 2 in the recommender domain they are
NOT, and a readout-independent check is required there.

Only kurtosis and eff_dim port to a recommender without reinterpretation.
topk_acc and autocorr both presuppose a token stream with language-like local
redundancy.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch


@dataclass
class LayerStats:
    layer: int
    kurtosis: float
    topk_acc: float
    autocorr: float
    eff_dim: float


def excess_kurtosis(logits: torch.Tensor) -> float:
    """Excess kurtosis of the readout distribution, averaged over positions.

    Computed per position then averaged, not pooled: pooling would mix
    across-position variance into the shape statistic.
    """
    x = logits.float()
    c = x - x.mean(-1, keepdim=True)
    var = c.pow(2).mean(-1)
    k = c.pow(4).mean(-1) / var.pow(2).clamp_min(1e-12) - 3.0
    return float(k.mean())


def topk_accuracy(
    lens_logits: torch.Tensor, model_logits: torch.Tensor, k: int = 5
) -> float:
    """Fraction of positions where the model's argmax is in the lens's top k.

    Scored against the model's OWN next-token prediction, not ground truth —
    this measures how far the lens has converged onto the output, which is what
    marks the motor transition.
    """
    target = model_logits.argmax(-1)
    topk = lens_logits.topk(k, dim=-1).indices
    return float((topk == target[:, None]).any(-1).float().mean())


def top1_autocorrelation(
    lens_logits: torch.Tensor, *, lag: int = 1, n_shuffles: int = 20,
    generator: torch.Generator | None = None,
) -> float:
    """Excess agreement of the top-1 lens token at distance ``lag``, over a
    position-shuffled null.

    Returned as observed minus null, so 0 means "no more persistent than
    chance". Reporting the raw rate instead would confound persistence with a
    single token dominating every position.
    """
    top1 = lens_logits.argmax(-1)
    if top1.numel() <= lag:
        return 0.0
    observed = float((top1[:-lag] == top1[lag:]).float().mean())
    null = 0.0
    for _ in range(n_shuffles):
        perm = torch.randperm(top1.numel(), generator=generator)
        s = top1[perm]
        null += float((s[:-lag] == s[lag:]).float().mean())
    return observed - null / n_shuffles


def effective_dimensionality(
    unembed_weight: torch.Tensor, jacobian: torch.Tensor, *, n_rows: int = 4096,
    generator: torch.Generator | None = None,
) -> float:
    """Participation ratio of the singular values of ``W_U J_l``.

    ``(sum s^2)^2 / sum s^4`` — 1.0 if one direction dominates, rank if all are
    equal. Estimated on a random row subsample because the full product is
    ``[vocab, d_model]`` and materialising it is not affordable; the subsample
    size is recorded since the estimate depends on it.
    """
    v = unembed_weight.shape[0]
    idx = (torch.randperm(v, generator=generator)[:n_rows]
           if v > n_rows else torch.arange(v))
    m = unembed_weight[idx].to(jacobian.dtype) @ jacobian
    s = torch.linalg.svdvals(m.float())
    s2 = s.pow(2)
    # Participation ratio: (sum s^2)^2 / sum s^4. Normalised by the largest
    # singular value first — the raw fourth power overflows float32 on real
    # weight matrices, which silently returns 0 rather than raising.
    s2 = s2 / s2.max().clamp_min(1e-30)
    return float(s2.sum().pow(2) / s2.pow(2).sum().clamp_min(1e-30))


def layer_stats(
    lens, model, prompts, unembed_weight, *, layers=None, k: int = 5,
    skip_first: int = 4, max_seq_len: int = 128, seed: int = 0,
) -> list[LayerStats]:
    """Compute all four statistics per layer, averaged over prompts."""
    layers = list(lens.source_layers if layers is None else layers)
    gen = torch.Generator().manual_seed(seed)
    acc = {l: [[], [], []] for l in layers}

    for prompt in prompts:
        lens_logits, model_logits, _ = lens.apply(
            model, prompt, layers=layers, max_seq_len=max_seq_len
        )
        for l in layers:
            ll = lens_logits[l][skip_first:]
            ml = model_logits[skip_first:]
            if ll.shape[0] < 2:
                continue
            acc[l][0].append(excess_kurtosis(ll))
            acc[l][1].append(topk_accuracy(ll, ml, k=k))
            acc[l][2].append(top1_autocorrelation(ll, generator=gen))

    out = []
    for l in layers:
        ed = effective_dimensionality(
            unembed_weight, lens.jacobians[l].to(unembed_weight.device), generator=gen
        )
        m = lambda xs: sum(xs) / len(xs) if xs else float("nan")
        out.append(LayerStats(l, m(acc[l][0]), m(acc[l][1]), m(acc[l][2]), ed))
    return out


def propose_band(stats: list[LayerStats], *, kurt_frac: float = 0.25,
                 acc_frac: float = 0.50) -> tuple[int, int]:
    """A FIRST PASS at the band. Not a substitute for reading the curves.

    Start: first layer whose kurtosis exceeds ``kurt_frac`` of the maximum.
    End:   last layer before top-k accuracy exceeds ``acc_frac`` of the maximum
           (the motor transition, where the lens collapses onto the output).

    The thresholds are arbitrary and are exposed so they can be recorded rather
    than buried. Plot the curves and check the proposal against them; if the
    statistics disagree about where the band is, that disagreement is a finding
    and the band should not be forced.
    """
    ks = [s.kurtosis for s in stats]
    accs = [s.topk_acc for s in stats]
    kt, at = kurt_frac * max(ks), acc_frac * max(accs)
    start = next((s.layer for s, v in zip(stats, ks) if v > kt), stats[0].layer)
    end = stats[-1].layer
    for s, v in zip(stats, accs):
        if s.layer > start and v > at:
            end = s.layer
            break
    return start, end
