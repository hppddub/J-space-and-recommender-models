"""Stage C2 — the intact side of Control A.

`DECISION_control_A.md` §4.5. This half is not optional and is not secondary.

The paper's claim is **selective** degradation: ablating the J-space collapses
multi-step reasoning while leaving fluent generation and unrelated tasks
comparatively intact. A degrading-side measurement alone cannot distinguish

    "we removed the workspace"      from      "we broke the model"

because both produce a large drop on the reasoning eval. Only the contrast
between the two sides separates them.

Primary measure, following the paper: **top-1 match on a pretraining-like
corpus** — the fraction of positions where the ablated model's most likely next
token agrees with the unablated model's. WikiText is used because it needs no
extra download (jlens ships a loader), it is the corpus the published lens was
fitted on, and next-token prediction has no floor effect, so "intact" cannot be
trivially satisfied the way a chance-level classification task could be.

Two further measures come from the same forward passes at no extra cost, and are
reported because top-1 match is coarse — it registers nothing until the argmax
actually flips:

  top5_overlap   graded agreement; catches reordering below the argmax
  mean_kl        KL(clean || ablated), the full distributional shift

Cross-entropy against the *true* next token is also reported when ids are
available, since "the ablated model still predicts real text well" is a stronger
claim than "it agrees with itself".
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Sequence

import torch

from .harness import AblationResult, AblationSpec, PromptCache, build_cache, run_ablation


@dataclass
class IntactResult:
    """Intact-side metrics for one prompt under one ablation condition."""

    top1_match: float          # 1.0 = ablation never changed the argmax
    top5_overlap: float        # mean |top5_clean ∩ top5_ablated| / 5
    mean_kl: float             # mean KL(clean || ablated), nats
    clean_ce: float | None     # cross-entropy vs true next token, unablated
    ablated_ce: float | None   # same, ablated
    n_positions: int

    @property
    def ce_delta(self) -> float | None:
        """Increase in cross-entropy caused by ablation. The headline number if
        ids were available: how much worse the model predicts real text."""
        if self.clean_ce is None or self.ablated_ce is None:
            return None
        return self.ablated_ce - self.clean_ce


@torch.no_grad()
def score_intact(result: AblationResult, *, skip_first: int = 4) -> IntactResult:
    """Score one ablation result on the intact side.

    Args:
        result: from :func:`run_ablation`, on a corpus prompt.
        skip_first: positions dropped from the front. Early positions are
            attention sinks with atypical residual statistics; kept low because
            §A.7 found position masking gave no meaningful improvement, so
            there is no reason to inherit the code default of 16.
    """
    clean = result.clean_logits[skip_first:].float()
    ablated = result.logits[skip_first:].float()
    n = clean.shape[0]
    if n == 0:
        return IntactResult(float("nan"), float("nan"), float("nan"), None, None, 0)

    top1_match = float((clean.argmax(-1) == ablated.argmax(-1)).float().mean())

    tc = clean.topk(5, dim=-1).indices
    ta = ablated.topk(5, dim=-1).indices
    overlap = (tc.unsqueeze(-1) == ta.unsqueeze(-2)).any(-1).float().sum(-1) / 5.0
    top5_overlap = float(overlap.mean())

    logp_c = torch.log_softmax(clean, dim=-1)
    logp_a = torch.log_softmax(ablated, dim=-1)
    mean_kl = float((logp_c.exp() * (logp_c - logp_a)).sum(-1).mean())

    clean_ce = ablated_ce = None
    if result.ids is not None:
        # position i predicts token i+1; drop the final position, which has no target
        targets = result.ids[0][skip_first + 1:]
        m = min(targets.shape[0], n - 1)
        if m > 0:
            t = targets[:m]
            clean_ce = float(torch.nn.functional.cross_entropy(clean[:m], t))
            ablated_ce = float(torch.nn.functional.cross_entropy(ablated[:m], t))

    return IntactResult(top1_match, top5_overlap, mean_kl, clean_ce, ablated_ce, n)


def aggregate(results: Sequence[IntactResult]) -> dict[str, Any]:
    """Mean each metric across prompts, ignoring empty results."""
    rs = [r for r in results if r.n_positions > 0]
    if not rs:
        return {"n_prompts": 0}
    out: dict[str, Any] = {"n_prompts": len(rs),
                           "n_positions": sum(r.n_positions for r in rs)}
    for f in ("top1_match", "top5_overlap", "mean_kl"):
        out[f] = sum(getattr(r, f) for r in rs) / len(rs)
    for f in ("clean_ce", "ablated_ce"):
        vals = [getattr(r, f) for r in rs if getattr(r, f) is not None]
        out[f] = sum(vals) / len(vals) if vals else None
    if out.get("clean_ce") is not None and out.get("ablated_ce") is not None:
        out["ce_delta"] = out["ablated_ce"] - out["clean_ce"]
    return out


@torch.no_grad()
def run_intact_side(
    model: Any, lens: Any, unembed_weight: torch.Tensor,
    corpus_prompts: Sequence[str], spec: AblationSpec,
    *, skip_first: int = 4, max_seq_len: int = 128, k_max: int | None = None,
    verbose: bool = True,
) -> dict[str, Any]:
    """Run one ablation condition across a corpus and aggregate the intact metrics."""
    k_max = k_max or max(2 * spec.k, 1)
    results = []
    for i, prompt in enumerate(corpus_prompts):
        cache = (build_cache(model, lens, prompt, spec.layers, k_max=k_max,
                             exclude_clean_top=spec.exclude_clean_top,
                             max_seq_len=max_seq_len)
                 if spec.selector != "none" else None)
        r = run_ablation(model, lens, unembed_weight, prompt, spec,
                         cache=cache, max_seq_len=max_seq_len)
        results.append(score_intact(r, skip_first=skip_first))
        if verbose and (i + 1) % 5 == 0:
            print(f"  [{i+1}/{len(corpus_prompts)}] "
                  f"top1_match={results[-1].top1_match:.3f}")
    return aggregate(results)


# --- the diagnostic that stops a vacuous "intact" -------------------------

NO_EFFECT_TOP1 = 0.99
NO_EFFECT_KL = 1e-3

#: Above this, the corpus counts as preserved. Exposed as a parameter of
#: :func:`diagnose` so the value used is recorded rather than buried — it is a
#: judgment call, not a fact, and the paper gives no numeric criterion.
PRESERVED_TOP1 = 0.90


def diagnose(intact: dict[str, Any], degrading_drop: float | None = None,
             *, preserved_top1: float = PRESERVED_TOP1) -> dict[str, Any]:
    """Distinguish selective degradation from the two ways it can be faked.

    **The failure this exists to catch:** a top-1 match near 1.0 reads as "the
    intact side held up", but it is equally consistent with the ablation having
    done nothing at all — a mis-specified band, a silently no-op confound guard,
    a hook that never fired. In that case the degrading side must also show
    nothing, and reporting "intact preserved" would be describing a broken
    experiment as a result.

    So the intact side is only evidence *given* that the ablation demonstrably
    perturbed the model somewhere. That is why ``degrading_drop`` belongs here.

    Args:
        intact: output of :func:`aggregate`.
        degrading_drop: accuracy lost on the reasoning eval under the same
            condition, as a fraction. Pass it whenever it is known.
    """
    t1, kl = intact.get("top1_match"), intact.get("mean_kl")
    d: dict[str, Any] = {"top1_match": t1, "mean_kl": kl,
                         "degrading_drop": degrading_drop}

    no_effect = (t1 is not None and t1 >= NO_EFFECT_TOP1
                 and kl is not None and kl <= NO_EFFECT_KL)

    if no_effect and (degrading_drop is None or degrading_drop < 0.05):
        d["verdict"] = "NO EFFECT — not evidence of selectivity"
        d["reading"] = (
            "The ablation barely perturbed the corpus distribution and did not "
            "meaningfully harm the reasoning eval either. This is consistent "
            "with the ablation not being applied: check that hooks fired, that "
            "the band indexes real layers, and that the clean-top-k guard is "
            "not excluding every candidate direction. Do not report this as an "
            "intact side."
        )
    elif no_effect:
        d["verdict"] = "SUSPICIOUS — large reasoning drop with no corpus shift"
        d["reading"] = (
            "The reasoning eval dropped substantially while the corpus "
            "distribution is essentially unchanged. That is a stronger "
            "selectivity claim than the paper makes, and warrants checking that "
            "the reasoning drop is not an artifact of the eval or the guard "
            "before it is believed."
        )
    elif degrading_drop is not None and degrading_drop >= 0.05:
        # BOTH conditions are required. An earlier version tested only for
        # degradation and labelled heavy corpus disruption "SELECTIVE" — the
        # exact conflation this module exists to prevent.
        corpus_disruption = 1.0 - (t1 if t1 is not None else 0.0)
        d["corpus_disruption"] = corpus_disruption
        d["selectivity_ratio"] = degrading_drop / max(corpus_disruption, 1e-6)
        if t1 is not None and t1 >= preserved_top1:
            d["verdict"] = "SELECTIVE — degradation with corpus largely preserved"
            d["reading"] = (
                f"Reasoning fell by {degrading_drop:.1%} while top-1 agreement on "
                f"the corpus held at {t1:.1%} (threshold {preserved_top1:.0%}). "
                f"Selectivity ratio {d['selectivity_ratio']:.1f}x. This is the "
                "paper's claim shape. Compare against the matched random-subspace "
                "condition before attributing it to the candidate subspace "
                "(proposal 4.8)."
            )
        else:
            d["verdict"] = "DAMAGE — both sides degraded"
            d["reading"] = (
                f"Reasoning fell by {degrading_drop:.1%}, but corpus top-1 "
                f"agreement also fell to {t1:.1%}, below the {preserved_top1:.0%} "
                "preservation threshold. Ablation degraded the model generally "
                "rather than selectively, and the workspace interpretation is "
                "not supported by this condition regardless of how large the "
                "reasoning drop was."
            )
    else:
        d["verdict"] = "INCONCLUSIVE"
        d["reading"] = (
            "The corpus distribution moved but no reasoning drop was supplied, "
            "or it was below 5%. Selectivity cannot be assessed from one side."
        )
    return d
