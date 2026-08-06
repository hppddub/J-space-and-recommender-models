"""Tests for the coarse-output intact tasks. Synthetic, CPU only."""
import sys, os, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
# jlens: use JLENS_PATH if set, else rely on it being pip-installed.
_jl = os.environ.get("JLENS_PATH")
if _jl:
    sys.path.insert(0, _jl)

import pytest, torch, jlens
from tests_tiny import TinyDecoder  # noqa
from ablation.harness import AblationSpec
from ablation.tasks import ChoiceTask, check_headroom, score_task, summarise


class FakeTok:
    """Distinct first token per word, matching the HF calling convention."""
    def __init__(self, mapping): self.m = mapping
    def __call__(self, text, add_special_tokens=True):
        from types import SimpleNamespace
        return SimpleNamespace(input_ids=[self.m[text.strip()]])


def task(choices, answers, chance):
    return ChoiceTask("t", ["p"] * len(answers), choices, answers, chance)


# --- tokenisation ----------------------------------------------------------

def test_distinct_first_tokens_accepted():
    t = task([["A", "B"]], [0], 0.5)
    t.tokenise(FakeTok({"A": 10, "B": 11}))
    assert t.choice_ids == [[10, 11]]


def test_colliding_first_tokens_raise_rather_than_silently_collapse():
    """Two candidates sharing a first token cannot be told apart from one
    forward pass. Failing loudly beats reporting a meaningless accuracy."""
    t = task([["yes", "yellow"]], [0], 0.5)
    with pytest.raises(ValueError, match="distinct first tokens"):
        t.tokenise(FakeTok({"yes": 7, "yellow": 7}))


# --- headroom gate ---------------------------------------------------------

def test_task_at_chance_is_refused():
    h = check_headroom(0.27, 0.25)
    assert not h["usable"] and "CANNOT serve" in h["reading"]


def test_task_well_above_chance_is_accepted():
    assert check_headroom(0.62, 0.25)["usable"]


def test_margin_is_a_parameter():
    assert check_headroom(0.42, 0.25, margin=0.15)["usable"]
    assert not check_headroom(0.42, 0.25, margin=0.25)["usable"]


# --- retention arithmetic --------------------------------------------------

def test_retention_above_chance_is_stricter_than_raw():
    """A destroyed 4-way model scores 25%, not 0%. Raw retention would call
    that 40% preserved; above-chance retention correctly calls it 0%."""
    res = {"clean": {"acc": 0.625, "k": 0, "n": 1, "answer_flip_rate": 0.0},
           "heavy|topk": {"acc": 0.25, "k": 0, "n": 1, "answer_flip_rate": 1.0}}
    s = summarise(res, task([["A","B","C","D"]], [0], 0.25))
    c = s["conditions"]["heavy|topk"]
    assert abs(c["retention_raw"] - 0.4) < 1e-6
    assert abs(c["retention_above_chance"]) < 1e-6


def test_full_preservation_gives_retention_one():
    res = {"clean": {"acc": 0.6, "k": 0, "n": 1, "answer_flip_rate": 0.0},
           "heavy|topk": {"acc": 0.6, "k": 0, "n": 1, "answer_flip_rate": 0.0}}
    c = summarise(res, task([["A","B","C","D"]], [0], 0.25))["conditions"]["heavy|topk"]
    assert abs(c["retention_above_chance"] - 1.0) < 1e-6


def test_headroom_gate_is_carried_into_the_summary():
    res = {"clean": {"acc": 0.26, "k": 0, "n": 1, "answer_flip_rate": 0.0},
           "heavy|topk": {"acc": 0.26, "k": 0, "n": 1, "answer_flip_rate": 0.0}}
    s = summarise(res, task([["A","B","C","D"]], [0], 0.25))
    assert s["headroom"]["usable"] is False, "a vacuous task must be flagged in the summary"


# --- end to end ------------------------------------------------------------

def test_score_task_runs_and_tracks_flips():
    m = TinyDecoder(n_layers=8, d_model=16, vocab_size=32, seed=0).eval()
    for p in m.parameters():
        p.requires_grad_(False)
    prompts = [f"alpha beta gamma delta {i} epsilon" for i in range(4)]
    lens = jlens.fit(m, prompts=prompts, source_layers=[3, 4], target_layer=-2,
                     skip_first=0, max_seq_len=32)
    t = ChoiceTask("toy", prompts, [["a", "b"]] * 4, [0, 1, 0, 1], 0.5)
    t.tokenise(FakeTok({"a": 5, "b": 6}))
    out = score_task(m, lens, m.lm_head.weight.detach(), t,
                     {"clean": AblationSpec(layers=(), k=0, selector="none"),
                      "heavy|topk": AblationSpec(layers=(3, 4), k=4)},
                     all_layers=(3, 4), max_seq_len=32, verbose=False)
    assert out["clean"]["n"] == 4 and out["clean"]["answer_flip_rate"] == 0.0
    assert 0.0 <= out["heavy|topk"]["answer_flip_rate"] <= 1.0
