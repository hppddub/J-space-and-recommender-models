"""Tests for the intact side (Stage C2). Synthetic, CPU only."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, "/home/claude/jacobian-lens")

import pytest, torch
import jlens
from tests_tiny import TinyDecoder  # noqa
from ablation.harness import AblationResult, AblationSpec, build_cache, run_ablation
from ablation.intact import (NO_EFFECT_KL, NO_EFFECT_TOP1, aggregate, diagnose,
                             run_intact_side, score_intact)


@pytest.fixture(scope="module")
def setup():
    m = TinyDecoder(n_layers=10, d_model=16, vocab_size=32, seed=0).eval()
    for p in m.parameters():
        p.requires_grad_(False)
    prompts = [f"alpha beta gamma delta number {i} epsilon zeta eta theta" for i in range(6)]
    lens = jlens.fit(m, prompts=prompts, source_layers=[3, 4, 5, 6],
                     target_layer=-2, skip_first=0, max_seq_len=32)
    return m, lens, m.lm_head.weight.detach(), prompts


# --- metric correctness ----------------------------------------------------

def test_identical_logits_give_perfect_scores():
    torch.manual_seed(0)
    lg = torch.randn(12, 40)
    r = score_intact(AblationResult(logits=lg, clean_logits=lg), skip_first=2)
    assert r.top1_match == 1.0
    assert r.top5_overlap == 1.0
    assert abs(r.mean_kl) < 1e-5


def test_unrelated_logits_give_poor_scores():
    torch.manual_seed(1)
    r = score_intact(AblationResult(logits=torch.randn(20, 60),
                                    clean_logits=torch.randn(20, 60)), skip_first=2)
    assert r.top1_match < 0.2
    assert r.top5_overlap < 0.3
    assert r.mean_kl > 0.1


def test_top5_overlap_is_more_sensitive_than_top1():
    """top1 registers nothing until the argmax flips; top5 sees reordering below it.
    That is the reason both are reported."""
    torch.manual_seed(2)
    clean = torch.randn(30, 50)
    ablated = clean.clone()
    # perturb ranks 2-5 without disturbing the argmax
    top = clean.topk(6, dim=-1).indices
    for i in range(30):
        ablated[i, top[i, 1:]] = torch.randn(5) * 0.1
    r = score_intact(AblationResult(logits=ablated, clean_logits=clean), skip_first=0)
    assert r.top1_match == 1.0, "argmax should be untouched by construction"
    assert r.top5_overlap < 1.0, "top5 must detect the reordering top1 cannot"


def test_kl_is_non_negative_and_asymmetric():
    torch.manual_seed(3)
    a, b = torch.randn(15, 40), torch.randn(15, 40)
    fwd = score_intact(AblationResult(logits=b, clean_logits=a), skip_first=0).mean_kl
    rev = score_intact(AblationResult(logits=a, clean_logits=b), skip_first=0).mean_kl
    assert fwd >= 0 and rev >= 0
    assert abs(fwd - rev) > 1e-6, "KL(p||q) != KL(q||p); direction must be clean||ablated"


def test_cross_entropy_computed_when_ids_present():
    torch.manual_seed(4)
    lg = torch.randn(10, 25)
    ids = torch.randint(25, (1, 10))
    r = score_intact(AblationResult(logits=lg, clean_logits=lg, ids=ids), skip_first=2)
    assert r.clean_ce is not None and r.ce_delta is not None
    assert abs(r.ce_delta) < 1e-5, "identical logits -> no CE change"
    r2 = score_intact(AblationResult(logits=lg, clean_logits=lg), skip_first=2)
    assert r2.clean_ce is None and r2.ce_delta is None


def test_skip_first_reduces_scored_positions():
    lg = torch.randn(20, 30)
    assert score_intact(AblationResult(logits=lg, clean_logits=lg), skip_first=0).n_positions == 20
    assert score_intact(AblationResult(logits=lg, clean_logits=lg), skip_first=6).n_positions == 14


# --- the diagnostic --------------------------------------------------------

def test_no_effect_is_not_reported_as_intact():
    """The failure mode this module exists to catch: an ablation that did
    nothing looks identical to a perfectly preserved intact side."""
    d = diagnose({"top1_match": 1.0, "mean_kl": 0.0}, degrading_drop=0.0)
    assert d["verdict"].startswith("NO EFFECT")


def test_selective_pattern_recognised():
    d = diagnose({"top1_match": 0.95, "mean_kl": 0.02}, degrading_drop=0.40)
    assert d["verdict"].startswith("SELECTIVE")
    assert "4.8" in d["reading"], "must point back to the random-baseline requirement"


def test_general_damage_recognised():
    d = diagnose({"top1_match": 0.30, "mean_kl": 2.5}, degrading_drop=0.45)
    assert d["verdict"].startswith("DAMAGE")


def test_missing_degrading_drop_defaults_to_the_cautious_reading():
    d = diagnose({"top1_match": 1.0, "mean_kl": 0.0})
    assert d["verdict"].startswith("NO EFFECT")


# --- end to end ------------------------------------------------------------

def test_none_selector_scores_as_perfectly_intact(setup):
    m, lens, wu, prompts = setup
    out = run_intact_side(m, lens, wu, prompts[:3],
                          AblationSpec(layers=(), k=0, selector="none"),
                          max_seq_len=32, verbose=False)
    assert out["top1_match"] == 1.0 and abs(out["mean_kl"]) < 1e-5


def test_real_ablation_perturbs_the_corpus(setup):
    m, lens, wu, prompts = setup
    out = run_intact_side(m, lens, wu, prompts[:3],
                          AblationSpec(layers=(4, 5), k=4), max_seq_len=32, verbose=False)
    assert out["n_prompts"] == 3
    assert out["mean_kl"] > 0, "ablation that changes nothing means the hooks did not fire"


def test_aggregate_handles_empty_input():
    assert aggregate([])["n_prompts"] == 0


def test_selective_requires_both_sides_not_just_degradation():
    """Regression: an earlier diagnose() called heavy corpus disruption
    'SELECTIVE' as long as the reasoning eval had dropped. Both conditions are
    required, and this is the whole point of the intact side."""
    dmg = diagnose({"top1_match": 0.30, "mean_kl": 2.5}, degrading_drop=0.45)
    sel = diagnose({"top1_match": 0.95, "mean_kl": 0.02}, degrading_drop=0.45)
    assert dmg["verdict"].startswith("DAMAGE")
    assert sel["verdict"].startswith("SELECTIVE")
    assert sel["selectivity_ratio"] > dmg["selectivity_ratio"]


def test_preservation_threshold_is_a_recorded_parameter():
    r = {"top1_match": 0.92, "mean_kl": 0.05}
    assert diagnose(r, 0.4, preserved_top1=0.90)["verdict"].startswith("SELECTIVE")
    assert diagnose(r, 0.4, preserved_top1=0.95)["verdict"].startswith("DAMAGE")
