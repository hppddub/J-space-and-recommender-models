"""Two-pass ablation harness.

Pass 1 is a clean forward pass: it records the residual stream at every band
layer, computes lens logits, and captures the clean next-token distribution.
Pass 2 re-runs with the selected directions projected out.

Two passes are not an optimisation choice — the confound guard of proposal 4.4
(paper: exclude the clean pass's top-10) *requires* knowing the clean output
before choosing what to ablate.

This harness is built to Phase 3 requirements from the first line, per guide
§3a: Control A, Control B, and the Phase 3 sweep all run through it unchanged.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Literal, Sequence

import torch

from jlens.hooks import ActivationRecorder
from jlens.lens import JacobianLens

from .directions import (
    Basis,
    clean_top_mask,
    lens_vectors,
    orthonormalise,
    project_out,
    random_isotropic,
    random_lens_tokens,
    select_by_rank,
)

Selector = Literal["topk", "next_k", "random_lens", "random_iso", "none"]


def record_at_or(spec, final):
    return sorted({*spec.layers, final})


def _mask_from_ids(ids: torch.Tensor, shape) -> torch.Tensor:
    """Rebuild the clean-top-k boolean mask from cached ids."""
    m = torch.zeros(shape, dtype=torch.bool, device=ids.device)
    return m.scatter(-1, ids, True)


@dataclass(frozen=True)
class AblationSpec:
    """One fully-specified ablation condition. Serialise this into every result.

    Attributes:
        layers: Band of block indices to ablate at. Light/medium/heavy differ
            only here — the paper varies the layer range, not k.
        k: Directions removed per position (proposal 4.7 sweeps this; the paper
            fixed it at 10). Sweeping k *and* layers multiplies runs — state
            which axis in prereg_phase3.md.
        selector: Which directions. ``"none"`` is the clean baseline.
        seed: Required for every random selector (guide §1.2).
        exclude_clean_top: Confound guard size. **Do not set to 0** except as a
            deliberate, logged demonstration of the artifact it prevents.
        mode: Projection mode; see :func:`project_out`.
        positions: Token positions to ablate at; ``None`` means all.
    """

    layers: tuple[int, ...]
    k: int
    selector: Selector = "topk"
    seed: int | None = None
    exclude_clean_top: int = 10
    mode: str = "subspace"
    positions: tuple[int, ...] | None = None

    def __post_init__(self) -> None:
        if self.selector in ("random_lens", "random_iso") and self.seed is None:
            raise ValueError(
                "random selectors require an explicit seed — an unseeded "
                "matched-random baseline is not reproducible and proposal 4.8 "
                "results computed against it are not reportable"
            )

    def key(self) -> str:
        import hashlib, json
        blob = json.dumps(asdict(self), sort_keys=True, default=str)
        return hashlib.sha256(blob.encode()).hexdigest()[:16]


@dataclass
class AblationResult:
    logits: torch.Tensor              # [n_positions, vocab] ablated next-token logits
    clean_logits: torch.Tensor        # [n_positions, vocab] unablated
    effective_rank: dict[int, torch.Tensor] = field(default_factory=dict)
    spec: AblationSpec | None = None
    ids: torch.Tensor | None = None       # [1, seq_len]; needed to score against
                                          # true next tokens on a corpus (intact side)


def prepare_lens(lens: JacobianLens, device) -> JacobianLens:
    """Move the Jacobians onto the compute device. **Does not touch dtype.**

    ``JacobianLens.__init__`` does ``J.float()`` on every Jacobian, so the class
    holds float32 regardless of what was on disk (``save`` writes fp16 purely
    for compactness). ``apply()`` correspondingly casts residuals with
    ``.float()`` before ``transport``. The library's internal contract is
    float32 throughout, and ``HFLensModel.unembed`` casts to the head's dtype
    itself, so nothing downstream needs the model's dtype here.

    An earlier version of this function cast the Jacobians to the model's dtype.
    That broke the contract and produced
    ``RuntimeError: expected mat1 and mat2 to have the same dtype`` inside
    ``transport``. Callers passing activations straight from
    ``ActivationRecorder`` (which are in the *model's* dtype, not float32) must
    cast those to float — see :func:`build_cache`.

    Only the device move is needed: without it ``transport`` copies a
    ``[d_model, d_model]`` matrix host-to-device on every call.
    """
    lens.jacobians = {k: v.to(device=device) for k, v in lens.jacobians.items()}
    return lens


@dataclass
class PromptCache:
    """Per-prompt work that every condition would otherwise repeat.

    The clean forward pass and the lens readout are identical across all
    conditions for a given prompt — only the direction *selection* differs. A
    37-condition sweep without this recomputes both 37 times.

    What is cached is deliberately small: the ranked token ids per layer, not
    the lens logits themselves. Lens logits are ``[n_positions, vocab]``, which
    at a 150k vocabulary is megabytes per layer per prompt; the ranked ids are
    ``[n_positions, k_max]``. Any ``k <= k_max`` is then a slice.

    ``k_max`` must be at least ``2 * max(k)`` in the sweep, because the
    ``next_k`` selector reads ranks ``k..2k``.
    """

    ids: torch.Tensor
    n_pos: int
    clean_logits: torch.Tensor
    excluded_ids: torch.Tensor | None          # [n_pos, n_exclude]
    ranked_ids: dict[int, torch.Tensor]        # layer -> [n_pos, k_max]
    k_max: int


@torch.no_grad()
def build_cache(
    model: Any, lens: JacobianLens, prompt: str, layers: Sequence[int],
    *, k_max: int, exclude_clean_top: int = 10, max_seq_len: int = 512,
) -> PromptCache:
    """Run the clean pass once and rank directions once, for reuse."""
    ids = model.encode(prompt, max_length=max_seq_len)
    final = model.n_layers - 1
    record_at = sorted({*layers, final})

    with ActivationRecorder(model.layers, record_at) as rec:
        model.forward(ids)
        acts = {i: rec.activations[i][0].detach() for i in record_at}
    clean_logits = model.unembed(acts[final])

    excluded = (clean_top_mask(clean_logits, exclude_clean_top)
                if exclude_clean_top > 0 else None)
    excluded_ids = (clean_logits.topk(exclude_clean_top, dim=-1).indices
                    if exclude_clean_top > 0 else None)

    ranked = {}
    for layer in layers:
        # .float() to match the lens's float32 Jacobians, as apply() does.
        lens_logits = model.unembed(lens.transport(acts[layer].float(), layer))
        ranked[layer] = select_by_rank(lens_logits, k_max, excluded=excluded)

    return PromptCache(ids, ids.shape[1], clean_logits, excluded_ids, ranked, k_max)


class _Ablator:
    """Forward hooks that project out precomputed per-position direction sets."""

    def __init__(
        self,
        blocks: Sequence[torch.nn.Module],
        bases: dict[int, Basis],
        position_mask: torch.Tensor | None,
        mode: str,
    ) -> None:
        self._blocks, self._bases = blocks, bases
        self._position_mask, self._mode = position_mask, mode
        self._handles: list[Any] = []

    def _hook(self, index: int):
        basis = self._bases[index]

        def fn(module, inputs, output):
            is_tuple = not torch.is_tensor(output)
            tensor = output[0] if is_tuple else output
            # tensor: [batch, seq, d_model]; harness runs batch=1.
            h = tensor[0]
            new = project_out(h, basis, mode=self._mode)
            if self._position_mask is not None:
                new = torch.where(self._position_mask[:, None], new, h)
            tensor = torch.cat([new[None], tensor[1:]], dim=0)
            return (tensor, *output[1:]) if is_tuple else tensor

        return fn

    def __enter__(self):
        try:
            for i in self._bases:
                self._handles.append(self._blocks[i].register_forward_hook(self._hook(i)))
        except Exception:
            self.__exit__()
            raise
        return self

    def __exit__(self, *exc) -> None:
        for h in self._handles:
            h.remove()
        self._handles = []


@torch.no_grad()
def run_ablation(
    model: Any,
    lens: JacobianLens,
    unembed_weight: torch.Tensor,
    prompt: str,
    spec: AblationSpec,
    *,
    max_seq_len: int = 512,
    cache: PromptCache | None = None,
) -> AblationResult:
    """Run one ablation condition end to end.

    Args:
        model: Anything satisfying ``jlens.protocol.LensModel``.
        lens: Fitted lens. ``spec.layers`` must be a subset of its source layers
            for lens-based selectors.
        unembed_weight: ``W_U``, ``[vocab, d_model]`` — usually
            ``model.lm_head.weight``. Passed explicitly because the LensModel
            protocol exposes ``unembed()`` (norm + head) but not ``W_U`` itself.
    """
    final = model.n_layers - 1

    # --- Pass 1: clean (skipped entirely when a cache is supplied) ---
    if cache is not None:
        if spec.k * (2 if spec.selector == "next_k" else 1) > cache.k_max:
            raise ValueError(
                f"cache holds k_max={cache.k_max} ranked directions but this "
                f"condition needs {spec.k * (2 if spec.selector == 'next_k' else 1)}. "
                "Rebuild the cache with a larger k_max."
            )
        ids, n_pos = cache.ids, cache.n_pos
        clean_logits, acts = cache.clean_logits, None
    else:
        ids = model.encode(prompt, max_length=max_seq_len)
        n_pos = ids.shape[1]
        with ActivationRecorder(model.layers, sorted({*spec.layers, final})) as rec:
            model.forward(ids)
            acts = {i: rec.activations[i][0].detach() for i in record_at_or(spec, final)}
        clean_logits = model.unembed(acts[final])

    if spec.selector == "none":
        return AblationResult(clean_logits, clean_logits, spec=spec, ids=ids)

    excluded = None
    if spec.exclude_clean_top > 0:
        excluded = (
            _mask_from_ids(cache.excluded_ids, clean_logits.shape)
            if cache is not None
            else clean_top_mask(clean_logits, spec.exclude_clean_top)
        )

    # --- Direction selection, per band layer ---
    gen = torch.Generator(device="cpu")
    if spec.seed is not None:
        gen.manual_seed(spec.seed)
    bases: dict[int, Basis] = {}
    ref = clean_logits
    for layer in spec.layers:
        h = acts[layer] if acts is not None else ref
        if spec.selector == "random_iso":
            vecs = random_isotropic(
                n_pos, spec.k, model.d_model, gen, device=h.device, dtype=h.dtype
            )
        else:
            ranked = cache.ranked_ids[layer] if cache is not None else None
            if ranked is None:
                lens_logits = model.unembed(lens.transport(h.float(), layer))
            if spec.selector == "topk":
                tok = (ranked[:, : spec.k] if ranked is not None
                       else select_by_rank(lens_logits, spec.k, excluded=excluded))
            elif spec.selector == "next_k":
                tok = (ranked[:, spec.k : 2 * spec.k] if ranked is not None
                       else select_by_rank(lens_logits, spec.k,
                                           rank_offset=spec.k, excluded=excluded))
            elif spec.selector == "random_lens":
                tok = random_lens_tokens(
                    n_pos, spec.k, clean_logits.shape[-1], gen,
                    excluded=excluded, device=clean_logits.device,
                )
            else:
                raise ValueError(f"unknown selector {spec.selector!r}")
            vecs = lens_vectors(unembed_weight, lens.jacobians[layer].to(h.device), tok)
        bases[layer] = orthonormalise(vecs)

    pos_mask = None
    if spec.positions is not None:
        pos_mask = torch.zeros(n_pos, dtype=torch.bool, device=ids.device)
        pos_mask[list(spec.positions)] = True

    # --- Pass 2: ablated ---
    with _Ablator(model.layers, bases, pos_mask, spec.mode):
        with ActivationRecorder(model.layers, [final]) as rec2:
            model.forward(ids)
            ablated_final = rec2.activations[final][0].detach()

    return AblationResult(
        logits=model.unembed(ablated_final),
        clean_logits=clean_logits,
        effective_rank={l: b.rank for l, b in bases.items()},
        spec=spec,
        ids=ids,
    )


def greedy_match(result: AblationResult, answer_id: int, position: int = -1) -> dict:
    """Score one prompt: did the greedy next token match, clean and ablated?

    The Control A metric per DECISION_control_A §4.4 — greedy next-token
    accuracy against probe-swap.json's ``answer`` field.
    """
    return {
        "clean_correct": int(result.clean_logits[position].argmax()) == answer_id,
        "ablated_correct": int(result.logits[position].argmax()) == answer_id,
    }
