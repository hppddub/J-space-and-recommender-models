"""Synthetic tests for the ablation harness. No model download, CPU only."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, "/home/claude/jacobian-lens")

import pytest, torch
import jlens
from tests_tiny import TinyDecoder  # noqa
from ablation.directions import (
    Basis, clean_top_mask, lens_vectors, orthonormalise, project_out,
    random_isotropic, select_by_rank,
)
from ablation.harness import AblationSpec, run_ablation
from ablation.sweep import build_conditions, run_sweep


@pytest.fixture(scope="module")
def setup(tmp_path_factory):
    m = TinyDecoder(n_layers=8, d_model=16, vocab_size=32, seed=0).eval()
    for p in m.parameters():
        p.requires_grad_(False)
    prompts = [f"alpha beta gamma delta number {i} epsilon zeta eta" for i in range(6)]
    lens = jlens.fit(m, prompts=prompts, source_layers=[2, 3, 4, 5],
                     target_layer=-2, skip_first=0, max_seq_len=32)
    return m, lens, m.lm_head.weight.detach(), prompts[0]


# --- projection correctness ------------------------------------------------

def test_subspace_projection_removes_the_span():
    torch.manual_seed(0)
    v = torch.randn(4, 3, 16)
    b = orthonormalise(v)
    h = torch.randn(4, 16)
    out = project_out(h, b)
    # residual must be orthogonal to every original direction
    assert torch.einsum("pkd,pd->pk", v, out).abs().max() < 1e-4


def test_rank_deficiency_is_detected_not_hidden():
    v = torch.randn(2, 4, 16)
    v[:, 3] = v[:, 0] * 2.0          # collinear -> span is 3, not 4
    b = orthonormalise(v)
    assert torch.allclose(b.rank, torch.tensor([3.0, 3.0]), atol=1e-5)


def test_sequential_removes_no_more_than_subspace():
    torch.manual_seed(1)
    v = torch.randn(3, 5, 16)
    b = orthonormalise(v)
    h = torch.randn(3, 16)
    sub = project_out(h, b, mode="subspace")
    seq = project_out(h, b, mode="sequential")
    assert sub.norm(dim=-1).max() <= seq.norm(dim=-1).max() + 1e-5


# --- the confound guard ----------------------------------------------------

def test_clean_top_mask_blocks_those_tokens_from_selection():
    torch.manual_seed(2)
    lens_logits = torch.randn(5, 32)
    excl = clean_top_mask(lens_logits, 10)      # same tensor as proxy for clean
    tok = select_by_rank(lens_logits, 4, excluded=excl)
    assert not excl.gather(-1, tok).any(), "guard leaked: an excluded token was selected"


def test_guard_actually_changes_what_gets_selected():
    torch.manual_seed(3)
    lens_logits = torch.randn(5, 32)
    unguarded = select_by_rank(lens_logits, 4)
    guarded = select_by_rank(lens_logits, 4, excluded=clean_top_mask(lens_logits, 10))
    assert not torch.equal(unguarded, guarded), (
        "guard was a no-op here; a test that cannot fail is not a control"
    )


# --- end-to-end ------------------------------------------------------------

def test_none_selector_is_exactly_the_clean_pass(setup):
    m, lens, wu, prompt = setup
    r = run_ablation(m, lens, wu, prompt, AblationSpec(layers=(), k=0, selector="none"))
    assert torch.equal(r.logits, r.clean_logits)


def test_ablation_changes_output_and_more_than_nothing(setup):
    m, lens, wu, prompt = setup
    r = run_ablation(m, lens, wu, prompt, AblationSpec(layers=(3, 4), k=4))
    delta = (r.logits - r.clean_logits).abs().max()
    assert delta > 1e-5, "ablation had no effect at all — hooks likely not firing"


def test_effective_rank_is_reported(setup):
    m, lens, wu, prompt = setup
    r = run_ablation(m, lens, wu, prompt, AblationSpec(layers=(3,), k=4))
    assert 3 in r.effective_rank and r.effective_rank[3].max() <= 4


def test_random_selector_requires_a_seed():
    with pytest.raises(ValueError, match="require an explicit seed"):
        AblationSpec(layers=(3,), k=4, selector="random_lens")


def test_same_seed_reproduces_same_result(setup):
    m, lens, wu, prompt = setup
    s = AblationSpec(layers=(3,), k=4, selector="random_iso", seed=42)
    a = run_ablation(m, lens, wu, prompt, s)
    b = run_ablation(m, lens, wu, prompt, s)
    assert torch.equal(a.logits, b.logits)


def test_different_seeds_give_a_distribution_not_a_point(setup):
    m, lens, wu, prompt = setup
    outs = [
        run_ablation(m, lens, wu, prompt,
                     AblationSpec(layers=(3,), k=4, selector="random_iso", seed=s)).logits
        for s in (1, 2, 3)
    ]
    assert not torch.equal(outs[0], outs[1]) and not torch.equal(outs[1], outs[2])


def test_positions_argument_restricts_the_edit(setup):
    m, lens, wu, prompt = setup
    full = run_ablation(m, lens, wu, prompt, AblationSpec(layers=(3,), k=4))
    one = run_ablation(m, lens, wu, prompt, AblationSpec(layers=(3,), k=4, positions=(2,)))
    assert (one.logits - one.clean_logits).abs().max() < (full.logits - full.clean_logits).abs().max()


# --- sweep bookkeeping -----------------------------------------------------

def test_every_candidate_condition_has_matched_controls():
    conds = build_conditions({"med": [3, 4]}, ks=[2, 4], n_random_draws=3)
    sel = [c.selector for c in conds]
    for k in (2, 4):
        assert sum(1 for c in conds if c.k == k and c.selector == "random_lens") == 3
        assert sum(1 for c in conds if c.k == k and c.selector == "random_iso") == 3
        assert any(c.k == k and c.selector == "next_k" for c in conds)
    assert "none" in sel


def test_sweep_is_resumable(tmp_path):
    conds = build_conditions({"med": [3]}, ks=[2], n_random_draws=1)
    calls = []
    def ev(spec):
        calls.append(spec.key())
        return {"score": 1.0}
    run_sweep(conds, ev, tmp_path, verbose=False)
    n_first = len(calls)
    run_sweep(conds, ev, tmp_path, verbose=False)   # second pass: all cached
    assert len(calls) == n_first and n_first == len(conds)


def test_config_snapshot_and_commit_are_written(tmp_path):
    conds = build_conditions({"med": [3]}, ks=[2], n_random_draws=1)
    run_sweep(conds, lambda s: {"score": 0.0}, tmp_path, verbose=False)
    import json
    cfgs = list(tmp_path.glob("*/config.json"))
    assert cfgs
    body = json.loads(cfgs[0].read_text())
    assert "git_commit" in body and "spec" in body


# --- caching must not change results ---------------------------------------

def test_cache_gives_identical_results(setup):
    """The whole point of the cache is speed, not different numbers."""
    m, lens, wu, prompt = setup
    from ablation.harness import build_cache
    cache = build_cache(m, lens, prompt, layers=(3, 4), k_max=8, max_seq_len=32)
    for spec in [
        AblationSpec(layers=(3, 4), k=4, selector="topk"),
        AblationSpec(layers=(3, 4), k=4, selector="next_k"),
        AblationSpec(layers=(3, 4), k=4, selector="random_iso", seed=7),
        AblationSpec(layers=(3, 4), k=4, selector="random_lens", seed=7),
    ]:
        a = run_ablation(m, lens, wu, prompt, spec, max_seq_len=32)
        b = run_ablation(m, lens, wu, prompt, spec, cache=cache)
        assert torch.allclose(a.logits, b.logits, atol=1e-5), f"cache changed {spec.selector}"


def test_cache_refuses_k_beyond_what_it_holds(setup):
    m, lens, wu, prompt = setup
    from ablation.harness import build_cache
    cache = build_cache(m, lens, prompt, layers=(3,), k_max=4, max_seq_len=32)
    with pytest.raises(ValueError, match="k_max"):
        run_ablation(m, lens, wu, prompt,
                     AblationSpec(layers=(3,), k=4, selector="next_k"), cache=cache)


def test_cache_clean_pass_matches_uncached(setup):
    m, lens, wu, prompt = setup
    from ablation.harness import build_cache
    cache = build_cache(m, lens, prompt, layers=(3,), k_max=8, max_seq_len=32)
    r = run_ablation(m, lens, wu, prompt,
                     AblationSpec(layers=(), k=0, selector="none"), max_seq_len=32)
    assert torch.allclose(cache.clean_logits, r.clean_logits, atol=1e-5)


# --- dtype: the case that broke Stage B --------------------------------------
#
# NOTE ON COVERAGE. The full bf16 path cannot be exercised on CPU: torch's CPU
# layer_norm rejects bf16 parameters ("expect parameter to have scalar type of
# Float"). So the end-to-end bf16 test is GPU-only and the invariant is tested
# directly instead. Treat the bf16 path as verified by invariant + reasoning,
# not by an end-to-end CPU run.


def test_prepare_lens_does_not_change_dtype():
    """The bug that broke Stage B, as a one-line assertion.

    `JacobianLens.__init__` forces float32. `apply()` casts residuals to float32
    to match. Casting the Jacobians to the model's dtype breaks that contract and
    raises inside `transport`.
    """
    import jlens
    from ablation.harness import prepare_lens

    m = TinyDecoder(n_layers=6, d_model=16, vocab_size=32, seed=0).eval()
    for p in m.parameters():
        p.requires_grad_(False)
    lens = jlens.fit(m, prompts=["alpha beta gamma delta epsilon zeta eta"],
                     source_layers=[2, 3], target_layer=-2, skip_first=0, max_seq_len=24)
    before = {k: v.dtype for k, v in lens.jacobians.items()}
    lens = prepare_lens(lens, torch.device("cpu"))
    assert all(v.dtype == torch.float32 for v in lens.jacobians.values())
    assert {k: v.dtype for k, v in lens.jacobians.items()} == before


def test_transport_needs_float32_and_float_cast_fixes_it():
    """Documents *why* the `.float()` calls in build_cache and run_ablation exist."""
    import jlens
    m = TinyDecoder(n_layers=6, d_model=16, vocab_size=32, seed=0).eval()
    for p in m.parameters():
        p.requires_grad_(False)
    lens = jlens.fit(m, prompts=["alpha beta gamma delta epsilon zeta eta"],
                     source_layers=[2, 3], target_layer=-2, skip_first=0, max_seq_len=24)

    acts_bf16 = torch.randn(5, 16, dtype=torch.bfloat16)
    with pytest.raises(RuntimeError, match="same dtype"):
        lens.transport(acts_bf16, 2)
    out = lens.transport(acts_bf16.float(), 2)      # the fix, as applied in harness
    assert out.dtype == torch.float32 and torch.isfinite(out).all()


@pytest.mark.skipif(not torch.cuda.is_available(),
                    reason="CPU layer_norm rejects bf16 parameters; GPU-only test")
def test_harness_works_with_a_bfloat16_model_on_gpu():
    import jlens
    from ablation.harness import build_cache, prepare_lens

    dev = torch.device("cuda")
    m = TinyDecoder(n_layers=8, d_model=16, vocab_size=32, seed=0).eval()
    for p in m.parameters():
        p.requires_grad_(False)
    prompts = [f"alpha beta gamma delta number {i} epsilon zeta" for i in range(4)]
    lens = jlens.fit(m, prompts=prompts, source_layers=[2, 3, 4],
                     target_layer=-2, skip_first=0, max_seq_len=32)
    m_bf = m.to(device=dev, dtype=torch.bfloat16)
    lens = prepare_lens(lens, dev)
    cache = build_cache(m_bf, lens, prompts[0], (3, 4), k_max=8, max_seq_len=32)
    r = run_ablation(m_bf, lens, m_bf.lm_head.weight.detach(), prompts[0],
                     AblationSpec(layers=(3, 4), k=4), cache=cache)
    assert torch.isfinite(r.logits.float()).all()
