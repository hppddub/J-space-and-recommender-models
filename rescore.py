"""Re-score headroom generations under documented normalisation rules.

Reads the ALREADY-SAVED generations from the diagnostic run. No GPU, no model,
no regeneration — the continuations are fixed and this only changes how they are
graded, which keeps the amendment auditable.

See preregistration/amendments.md. The rules below were written AFTER seeing the
strict-miss list; that is stated in the amendment and is the reason both numbers
must be reported.
"""
from __future__ import annotations
import json, re, sys

NUM = {"zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5","six":"6",
       "seven":"7","eight":"8","nine":"9","ten":"10","eleven":"11","twelve":"12",
       "thirteen":"13","fourteen":"14","fifteen":"15","sixteen":"16","seventeen":"17",
       "eighteen":"18","nineteen":"19","twenty":"20"}
ARTICLES = {"a", "an", "the"}
#: Modifiers that REVERSE or distance the meaning. R3 credits a two-word phrase
#: whose head is the answer ("honey bee" -> "bee"), but " not red" is also two
#: words with head "red" and must never be credited. Found by adversarial test,
#: not by the dataset — no negation appears in the 90 items, but ablated output
#: in Control A plausibly will.
NEGATORS = {"not", "no", "never", "non", "un", "without", "except", "besides",
            "other", "another", "different", "opposite", "unlike"}


def answer_phrase(gen: str) -> str:
    """The model's answer, cut at the first sentence end or template header."""
    s = gen.strip()
    s = re.split(r"[.\n?!;,]", s)[0]
    return s.strip().strip("'\"").lower()


def norm_number(tok: str) -> str:
    """R1 — numeral/number-word equivalence. Applies in both directions."""
    return NUM.get(tok, tok)


def strip_articles(words: list[str]) -> list[str]:
    """R2 — drop a leading determiner."""
    return words[1:] if words and words[0] in ARTICLES else words


def score(answer: str, gen: str, strict: bool) -> tuple[bool, str]:
    """Returns (credited, which_rule).

    MONOTONE BY CONSTRUCTION: a strict pass is always credited. The rules can
    only add. This is not a stylistic choice — the phrase-level rules are not a
    superset of first-token matching (the key `North` is a strict pass against
    " North America", but the phrase is "north america"), so without this an
    "amendment" would silently remove items it was never meant to touch.
    """
    a = answer.strip().lower()
    if strict:
        return True, "strict"
    phrase = answer_phrase(gen)
    if phrase == a:
        return True, "strict"

    words = strip_articles(phrase.split())
    if not words:
        return False, "-"

    # R2: article-stripped exact match
    if " ".join(words) == a:
        return True, "R2 article"

    # R1: numeral <-> word, single token only
    if len(words) == 1 and norm_number(words[0]) == norm_number(a):
        return True, "R1 numeral"

    # R3: two-word compound whose HEAD is the answer ("honey bee" -> "bee").
    # Capped at two words to keep the blast radius small; a longer phrase is a
    # different answer, not a compound form of this one.
    if len(words) == 2 and words[-1] == a and words[0] not in NEGATORS:
        return True, "R3 compound"

    return False, "-"


def main(path: str) -> None:
    rows = json.load(open(path))
    n = len(rows)
    strict = sum(r["strict"] for r in rows)
    credited, flips = 0, []
    for r in rows:
        ok, rule = score(r["answer"], r["generated_full"], r["strict"])
        credited += ok
        if ok and not r["strict"]:
            flips.append((r["name"], r["answer"], r["generated_full"], rule))
        r["amended"], r["rule"] = ok, rule

    def wilson(k, m, z=1.96):
        p = k / m; d = 1 + z**2 / m
        c = (p + z**2 / (2*m)) / d
        h = z * ((p*(1-p)/m + z**2/(4*m**2))**0.5) / d
        return max(0, c-h), min(1, c+h)

    print(f"strict  : {strict}/{n} = {strict/n:.1%}  CI {wilson(strict,n)[0]:.1%}-{wilson(strict,n)[1]:.1%}")
    print(f"amended : {credited}/{n} = {credited/n:.1%}  CI {wilson(credited,n)[0]:.1%}-{wilson(credited,n)[1]:.1%}")
    print(f"\n{len(flips)} items flipped by the rules:")
    for name, ans, gen, rule in flips:
        print(f"  [{rule:<12}] {name:<26} want={ans!r:<14} got={gen.strip()[:28]!r}")

    json.dump(rows, open("rescored_rows.json", "w"), indent=2)
    print("\nwrote rescored_rows.json")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "diagnostic_rows.json")
