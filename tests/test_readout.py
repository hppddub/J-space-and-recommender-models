"""Tests for Stage B2 readout verification. Synthetic, CPU only."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, "/home/claude/jacobian-lens")

import pytest, torch, jlens
from tests_tiny import TinyDecoder  # noqa
from band.readout import ReadoutRecord, measure_readout, summarise, verdict


@pytest.fixture(scope="module")
def setup():
    m = TinyDecoder(n_layers=10, d_model=16, vocab_size=32, seed=0).eval()
    for p in m.parameters():
        p.requires_grad_(False)
    prompts = [f"alpha beta gamma delta number {i} epsilon zeta eta" for i in range(5)]
    lens = jlens.fit(m, prompts=prompts, source_layers=[3, 4, 5],
                     target_layer=-2, skip_first=0, max_seq_len=32)
    return m, lens, m.lm_head.weight.detach(), prompts


def rec(layer, rank, loading=0.5, foil=False, n=1):
    return ReadoutRecord("x", layer, "t", n, rank, 0, loading, loading, foil)


# --- measurement -----------------------------------------------------------

def test_measure_returns_one_record_per_layer(setup):
    m, lens, wu, prompts = setup
    out = measure_readout(m, lens, wu, prompts[0], "gamma", [3, 4, 5],
                          skip_first=1, max_seq_len=32)
    assert [r.layer for r in out] == [3, 4, 5]
    assert all(0 <= r.best_rank < 32 for r in out), "rank must lie inside the vocab"
    assert all(-1.0001 <= r.max_loading <= 1.0001 for r in out), "cosine out of range"


def test_loading_is_a_cosine_not_a_dot_product(setup):
    """Scaling the target's lens direction must not change the loading."""
    m, lens, wu, prompts = setup
    a = measure_readout(m, lens, wu, prompts[0], "gamma", [4], skip_first=1, max_seq_len=32)
    lens.jacobians[4] = lens.jacobians[4] * 3.0
    b = measure_readout(m, lens, wu, prompts[0], "gamma", [4], skip_first=1, max_seq_len=32)
    lens.jacobians[4] = lens.jacobians[4] / 3.0
    assert abs(a[0].max_loading - b[0].max_loading) < 1e-4


def test_foil_flag_is_carried_through(setup):
    m, lens, wu, prompts = setup
    out = measure_readout(m, lens, wu, prompts[0], "delta", [4],
                          is_foil=True, skip_first=1, max_seq_len=32)
    assert out[0].is_foil is True


# --- summary ---------------------------------------------------------------

def test_summary_computes_topk_and_gaps():
    recs = ([rec(4, 0, 0.9) for _ in range(7)] + [rec(4, 50, 0.1) for _ in range(3)]
            + [rec(4, 60, 0.1, foil=True) for _ in range(10)])
    s = summarise(recs, [4])["per_layer"][4]
    assert s["true"]["top10"] == 0.7 and s["foil"]["top10"] == 0.0
    assert abs(s["top10_gap"] - 0.7) < 1e-9
    assert s["loading_gap"] > 0


def test_median_rank_reported_not_mean():
    """One catastrophic rank should not swamp the summary."""
    recs = [rec(4, 1) for _ in range(9)] + [rec(4, 100000)]
    assert summarise(recs, [4])["per_layer"][4]["true"]["median_rank"] == 1


# --- verdict ---------------------------------------------------------------

def test_strong_readout_recognised():
    recs = [rec(4, 0, 0.8) for _ in range(6)] + [rec(4, 500, 0.1) for _ in range(4)] \
         + [rec(4, 900, 0.1, foil=True) for _ in range(10)]
    v = verdict(summarise(recs, [4]), [4])
    assert v["verdict"].startswith("READOUT SURFACES")


def test_no_gap_over_foils_is_flagged_even_when_topk_looks_good():
    """The failure this control exists to catch: a high top-10 rate that is
    just the lens favouring common words."""
    recs = [rec(4, 2, 0.5) for _ in range(9)] + [rec(4, 2, 0.5, foil=True) for _ in range(9)]
    v = verdict(summarise(recs, [4]), [4])
    assert v["verdict"].startswith("NO SIGNAL OVER FOILS")
    assert "4.5" in v["reading"], "must point back to the readout-too-weak branch"


def test_weak_but_real_signal_distinguished_from_none():
    recs = [rec(4, 1, .7) for _ in range(2)] + [rec(4, 900, .1) for _ in range(8)] \
         + [rec(4, 900, .1, foil=True) for _ in range(10)]
    v = verdict(summarise(recs, [4]), [4])
    assert v["verdict"].startswith("WEAK")


def test_thresholds_are_parameters_not_hidden_constants():
    recs = [rec(4, 1) for _ in range(4)] + [rec(4, 900) for _ in range(6)] \
         + [rec(4, 900, foil=True) for _ in range(10)]
    s = summarise(recs, [4])
    assert verdict(s, [4], min_top10=0.30)["verdict"].startswith("READOUT SURFACES")
    assert verdict(s, [4], min_top10=0.60)["verdict"].startswith("WEAK")
