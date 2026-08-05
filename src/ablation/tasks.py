"""Coarse-output intact tasks — completing `DECISION_control_A.md` §4.5.

§4.5 specified the intact side as pretraining-corpus top-1 match **plus** public
tasks the paper found essentially unaffected at heavy ablation: MMLU, SQuAD,
sentiment, CoLA — "any subset is adequate; two is enough". Only the corpus half
was built for the first Control A run, and it failed (top-1 0.577 at heavy).

That failure is real, but it was measured on the most *sensitive* of the
specified measures. Next-token match over a 151,936-token vocabulary registers
any distributional shift. A multiple-choice task does not: the answer only
changes if the shift specifically reorders four candidate tokens. That asymmetry
is almost certainly why the paper reported those tasks as intact, and it is why
the two measures answer different questions.

**Constrained-choice scoring.** Rather than taking the argmax over the whole
vocabulary, this compares logits only at the first token of each candidate
answer. That is the operation that makes a task coarse.

**These tasks need their own headroom check.** MMLU is 25% at chance, SST-2 is
50%. A model near chance cannot be degraded, and "intact" would then be vacuous
rather than reassuring — the same trap as `diagnose()`'s NO EFFECT branch.
:func:`check_headroom` refuses to certify a task whose clean score is not
clearly above chance.

SQuAD is deliberately excluded: it is extractive and generative, so it cannot be
scored from a single forward pass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Sequence

import torch

from .harness import AblationSpec, build_cache, run_ablation


@dataclass
class ChoiceTask:
    """A multiple-choice task scored from one forward pass."""

    name: str
    prompts: list[str]
    choices: list[list[str]]      # candidate answer strings, per prompt
    answers: list[int]            # index of the correct choice
    chance: float                 # accuracy of random guessing
    choice_ids: list[list[int]] = field(default_factory=list)

    def tokenise(self, tok: Any) -> None:
        """First token of each candidate, with a leading space.

        Raises if two candidates share a first token — the task would then be
        unscoreable from one forward pass, and silently collapsing them would
        produce a meaningless accuracy rather than an error.
        """
        self.choice_ids = []
        for i, ch in enumerate(self.choices):
            ids = []
            for c in ch:
                t = " " + c.strip()
                try:
                    enc = tok(t, add_special_tokens=False).input_ids
                except TypeError:
                    enc = tok(t).input_ids
                    if torch.is_tensor(enc):
                        enc = enc[0].tolist()
                ids.append(enc[0])
            if len(set(ids)) != len(ids):
                raise ValueError(
                    f"{self.name} item {i}: candidates {ch} do not have distinct "
                    "first tokens, so the task cannot be scored from one forward pass"
                )
            self.choice_ids.append(ids)


def mmlu_prompt(item: dict) -> str:
    letters = "ABCD"
    body = "\n".join(f"{letters[i]}. {c}" for i, c in enumerate(item["choices"]))
    return (f"The following are multiple choice questions (with answers) about "
            f"{item.get('subject','general knowledge').replace('_',' ')}.\n\n"
            f"{item['question']}\n{body}\nAnswer:")


def load_mmlu(n: int = 150, seed: int = 0) -> ChoiceTask:
    from datasets import load_dataset
    ds = load_dataset("cais/mmlu", "all", split="test").shuffle(seed=seed).select(range(n))
    return ChoiceTask(
        name="mmlu",
        prompts=[mmlu_prompt(x) for x in ds],
        choices=[["A", "B", "C", "D"] for _ in ds],
        answers=[int(x["answer"]) for x in ds],
        chance=0.25,
    )


def load_sst2(n: int = 150, seed: int = 0) -> ChoiceTask:
    from datasets import load_dataset
    ds = load_dataset("stanfordnlp/sst2", split="validation").shuffle(seed=seed).select(range(n))
    return ChoiceTask(
        name="sst2",
        prompts=[f"Review: {x['sentence'].strip()}\nSentiment:" for x in ds],
        choices=[["negative", "positive"] for _ in ds],
        answers=[int(x["label"]) for x in ds],
        chance=0.50,
    )


@torch.no_grad()
def score_task(
    model: Any, lens: Any, unembed_weight: torch.Tensor, task: ChoiceTask,
    specs: dict[str, AblationSpec], *, all_layers: Sequence[int], k_max: int = 20,
    max_seq_len: int = 512, verbose: bool = True, checkpoint_every: int = 25,
    on_checkpoint=None,
) -> dict[str, dict[str, Any]]:
    """Score every condition on the task, looping prompts outer.

    Prompt-outer because MMLU prompts are long: caching all of them would hold
    ``[n_positions, vocab]`` clean logits per prompt and run to tens of GB. One
    cache at a time, reused across all conditions for that prompt, is both
    bounded in memory and free of redundant clean passes.
    """
    if not task.choice_ids:
        task.tokenise(model.tokenizer)

    hits = {name: 0 for name in specs}
    flips = {name: 0 for name in specs}          # answer changed vs the clean pass
    n_done = 0

    for i, (prompt, cids, ans) in enumerate(zip(task.prompts, task.choice_ids, task.answers)):
        cache = build_cache(model, lens, prompt, all_layers, k_max=k_max,
                            max_seq_len=max_seq_len)
        clean_choice = None
        for name, spec in specs.items():
            r = run_ablation(model, lens, unembed_weight, prompt, spec,
                             cache=cache, max_seq_len=max_seq_len)
            # constrained choice: compare ONLY the candidate tokens
            sel = int(torch.tensor([r.logits[-1, c] for c in cids]).argmax())
            hits[name] += (sel == ans)
            if spec.selector == "none":
                clean_choice = sel
            elif clean_choice is not None:
                flips[name] += (sel != clean_choice)
        n_done += 1
        if verbose and n_done % checkpoint_every == 0:
            print(f"  [{n_done}/{len(task.prompts)}] " +
                  "  ".join(f"{n}={hits[n]/n_done:.3f}" for n in list(specs)[:3]))
            if on_checkpoint:
                on_checkpoint({n: hits[n] / n_done for n in specs}, n_done)

    return {name: {"acc": hits[name] / n_done, "k": hits[name], "n": n_done,
                   "answer_flip_rate": flips[name] / n_done if name != "clean" else 0.0}
            for name in specs}


def check_headroom(clean_acc: float, chance: float, *, margin: float = 0.15) -> dict[str, Any]:
    """Can this task serve as an intact-side control at all?

    A task at chance cannot be degraded, so "the ablated model still scores at
    chance" is not evidence of preservation. Mirrors the headroom gate applied to
    the degrading eval, and the NO EFFECT branch of ``intact.diagnose``.
    """
    ok = clean_acc >= chance + margin
    return {
        "clean_acc": clean_acc, "chance": chance, "margin_required": margin,
        "usable": ok,
        "reading": (
            f"Clean {clean_acc:.1%} vs chance {chance:.1%}. Usable as an intact "
            "control: there is room to fall."
            if ok else
            f"Clean {clean_acc:.1%} is not clearly above chance {chance:.1%}. "
            "This task CANNOT serve as an intact-side control — a preserved "
            "score would be indistinguishable from guessing. Report the clean "
            "number and exclude the task from the intact verdict."
        ),
    }


def summarise(results: dict[str, dict], task: ChoiceTask,
              *, primary: str = "heavy|topk") -> dict[str, Any]:
    """Retention relative to clean, plus the headroom gate."""
    clean = results["clean"]["acc"]
    head = check_headroom(clean, task.chance)
    out: dict[str, Any] = {"task": task.name, "clean": clean, "chance": task.chance,
                           "headroom": head, "conditions": {}}
    for name, r in results.items():
        if name == "clean":
            continue
        # retention above chance: what fraction of the model's ABOVE-CHANCE
        # performance survived. Raw accuracy overstates preservation, because a
        # fully destroyed model still scores at chance rather than zero.
        above = clean - task.chance
        out["conditions"][name] = {
            "acc": r["acc"], "retention_raw": r["acc"] / clean if clean else None,
            "retention_above_chance": ((r["acc"] - task.chance) / above) if above > 0 else None,
            "answer_flip_rate": r["answer_flip_rate"],
        }
    if primary in out["conditions"]:
        out["primary"] = {primary: out["conditions"][primary]}
    return out
