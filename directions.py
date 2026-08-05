"""Direction selection and subspace projection for J-space / R-space ablation.

Implements the direction-set half of the ablation harness. Every selector here
produces a set of residual-stream directions of a specified size; the harness
projects them out. Keeping selection separate from projection is what makes the
matched controls of proposal 4.8 cheap: same projection, different selector.

Terminology (guide 2.1): nothing here is "the workspace". These are candidate
directions until Phase 3 says otherwise.
"""

from __future__ import annotations

from dataclasses import dataclass

import torch


# --- J-lens vector construction -------------------------------------------

def lens_vectors(
    unembed_weight: torch.Tensor, jacobian: torch.Tensor, token_ids: torch.Tensor
) -> torch.Tensor:
    """The J-lens vectors for ``token_ids`` at one layer.

    Paper §2.1 defines the J-lens vectors as the rows of ``W_U J_l``. Only the
    requested rows are materialised: the full product is ``[vocab, d_model]``
    and is far too large to hold for a real vocabulary.

    Args:
        unembed_weight: ``W_U``, shape ``[vocab, d_model]``.
        jacobian: ``J_l``, shape ``[d_model, d_model]``.
        token_ids: Shape ``[..., k]``.

    Returns:
        Shape ``[..., k, d_model]``.
    """
    rows = unembed_weight.index_select(0, token_ids.reshape(-1).to(unembed_weight.device))
    rows = rows.to(jacobian.dtype) @ jacobian
    return rows.reshape(*token_ids.shape, jacobian.shape[-1])


# --- Selectors -------------------------------------------------------------

def select_by_rank(
    lens_logits: torch.Tensor,
    k: int,
    *,
    rank_offset: int = 0,
    excluded: torch.Tensor | None = None,
) -> torch.Tensor:
    """Token ids ranked ``rank_offset .. rank_offset + k`` by lens score.

    ``rank_offset=0`` gives the top-k the paper ablates. ``rank_offset=k`` gives
    the next-k, which is the "matched but not selected" control: same lens, same
    size, adjacent rank band. A candidate subspace that matters no more than the
    next-k has not earned H1 (proposal 4.8, extended per the probe-swap design).

    Args:
        lens_logits: Shape ``[n_positions, vocab]``.
        k: Number of directions.
        rank_offset: Rank to start from.
        excluded: Boolean mask ``[n_positions, vocab]``; True entries are never
            selected. This carries the clean-pass exclusion — see
            :func:`clean_top_mask`.

    Returns:
        Shape ``[n_positions, k]``.
    """
    scores = lens_logits.clone()
    if excluded is not None:
        scores = scores.masked_fill(excluded, float("-inf"))
    top = scores.topk(rank_offset + k, dim=-1).indices
    return top[:, rank_offset:]


def random_lens_tokens(
    n_positions: int,
    k: int,
    vocab_size: int,
    generator: torch.Generator,
    *,
    excluded: torch.Tensor | None = None,
    device: torch.device | None = None,
) -> torch.Tensor:
    """Uniformly random token ids — matched-size random control (proposal 4.8).

    Drawn from the lens dictionary rather than isotropically, so the control
    asks "is it *these* lens directions, or any lens directions?". Strictly the
    harder question of the two; run both.
    """
    out = torch.empty(n_positions, k, dtype=torch.long, device=device)
    for p in range(n_positions):
        while True:
            cand = torch.randint(
                vocab_size, (k,), generator=generator, device=generator.device
            ).to(device)
            if excluded is None or not bool(excluded[p, cand].any()):
                out[p] = cand
                break
    return out


def random_isotropic(
    n_positions: int, k: int, d_model: int, generator: torch.Generator,
    *, device: torch.device | None = None, dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """Isotropic random unit directions — the paper's random-direction control."""
    v = torch.randn(
        n_positions, k, d_model, generator=generator, device=generator.device,
        dtype=torch.float32,
    ).to(device=device, dtype=dtype)
    return v / v.norm(dim=-1, keepdim=True).clamp_min(1e-12)


def clean_top_mask(
    clean_next_token_logits: torch.Tensor, n_exclude: int = 10
) -> torch.Tensor:
    """Mask marking the clean pass's top-``n_exclude`` predictions per position.

    **This is the confound guard, and it is not optional.** Paper: "we do not
    ablate any tokens that appear in the top-10 tokens of a clean forward pass,
    so as to specifically target the J-space's effects on internal reasoning
    rather than report." Without it, ablation suppresses whatever the model was
    about to say, performance drops for a trivial reason, and H1 gets
    "confirmed" by an artifact.

    Args:
        clean_next_token_logits: Shape ``[n_positions, vocab]`` from an
            unablated forward pass.

    Returns:
        Boolean ``[n_positions, vocab]``, True where a token must not be ablated.
    """
    mask = torch.zeros_like(clean_next_token_logits, dtype=torch.bool)
    top = clean_next_token_logits.topk(n_exclude, dim=-1).indices
    return mask.scatter(-1, top, True)


# --- Projection ------------------------------------------------------------

@dataclass(frozen=True)
class Basis:
    """An orthonormal-row basis with a validity mask for rank-deficient sets."""

    rows: torch.Tensor   # [n_positions, k, d_model], orthonormal rows
    keep: torch.Tensor   # [n_positions, k], float 1/0
    rank: torch.Tensor   # [n_positions], effective rank actually removed


def orthonormalise(vectors: torch.Tensor, *, rtol: float = 1e-6) -> Basis:
    """Orthonormal basis for the span of each position's direction set.

    J-lens vectors are overcomplete and non-orthogonal (paper §2.3), so a set of
    k of them may span fewer than k dimensions. Small singular values are masked
    out rather than dropped, which keeps the operation batched and makes the
    effective rank observable — report it, because "we ablated k directions" is
    false if the span was smaller.
    """
    vectors = vectors.to(torch.float32)
    _, s, vh = torch.linalg.svd(vectors, full_matrices=False)
    keep = (s > rtol * s[..., :1].clamp_min(1e-30)).to(vectors.dtype)
    return Basis(rows=vh, keep=keep, rank=keep.sum(-1))


def project_out(
    hidden: torch.Tensor, basis: Basis, *, mode: str = "subspace"
) -> torch.Tensor:
    """Remove the component of ``hidden`` inside the spanned subspace.

    Args:
        hidden: Shape ``[n_positions, d_model]``.
        mode: ``"subspace"`` projects onto the orthogonal complement of the span
            in one step. ``"sequential"`` removes each direction in turn, which
            is order-dependent for non-orthogonal vectors and therefore removes
            *less* than the full span.

    The paper's phrasing — "zero out the residual stream's projection onto
    each" — does not disambiguate these, and for non-orthogonal J-lens vectors
    they differ. ``"subspace"`` is the default because it is the one that
    actually removes the content; ``"sequential"`` is provided so the choice can
    be tested rather than assumed. Record which was used.
    """
    h = hidden.to(torch.float32)
    if mode == "subspace":
        coeffs = torch.einsum("prd,pd->pr", basis.rows, h) * basis.keep
        return (h - torch.einsum("pr,prd->pd", coeffs, basis.rows)).to(hidden.dtype)
    if mode == "sequential":
        for i in range(basis.rows.shape[1]):
            v = basis.rows[:, i, :] * basis.keep[:, i : i + 1]
            h = h - (h * v).sum(-1, keepdim=True) * v
        return h.to(hidden.dtype)
    raise ValueError(f"unknown mode {mode!r}")
