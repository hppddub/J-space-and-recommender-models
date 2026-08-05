# R-Space Generalization Test

Does anything structurally analogous to J-space — a small, causally load-bearing
subspace identified via the Jacobian lens in language models — exist in open
generative recommender architectures?

This is framed as an **empirical generalization test**, not an application of a
settled result. A properly controlled negative result is a valid outcome and is
planned for. Target venue: Interp4Discovery, NeurIPS 2026.

The construct under test is deliberately named **R-space**, not J-space, to
prevent silently importing J-space's other reported properties (compactness,
verbalizability) by association. Verbalizability is explicitly **not** tested here.

## Hypotheses

Three separate claims, reported separately, never bundled:

- **H1** — causal importance: a subspace whose ablation disproportionately affects output
- **H2** — compactness: measured by a sweep over subspace size, never assumed
- **H3** — legibility: grounded only in item metadata that predates this project

## Status

Phase 0 (toolchain validation, Control A) complete. Gate G0 taken as **partial**:
three of four pre-registered criteria passed, one failed. See
`decisions/GATE_G0.md` for what each result licenses and what the failure bounds.

Phase 1 (model and task setup) is next.

## Layout

```
proposal/          proposal, execution guide, AI collaboration guide, compliance guide
docs/              phase overviews, consolidated logs, handoffs
decisions/         signed decision records and gate entries
preregistration/   pre-registrations and amendments
logs/              lab_log.md — append-only
lit/               literature review: claim ledger, search log, candidates
compliance/        page budget, responsible-use statement, licences
src/               ablation harness, band derivation, evaluation
tests/             unit tests, runnable without a GPU
scripts/           runnable entry points
notebooks/         Colab notebooks
configs/           run configurations
results/raw/       one directory per run, with config snapshot and commit hash
third_party/       vendored upstream, never modified
```

## Conventions

- **The lab log is append-only.** Corrections are added as later entries. The
  wrong version stays.
- **Every run records** its config snapshot, git commit hash, and every seed.
- **Pre-registrations are committed before the run they govern.** Deviations go
  in `preregistration/amendments.md`, timestamped and justified.
- **Negative and broken runs are logged.** Diagnosing a null depends on knowing
  what was tried.
- **Entries written after the fact say so.** A reconstruction acknowledged as
  such is admissible; a backfilled entry presented as contemporaneous is not.

## Reproducing

Phase 0 used Qwen3-8B with published Neuronpedia lenses, on Colab A100.
Unit tests run on CPU without downloading a model:

```
python -m pytest tests/
```

## Licences

Upstream artifacts keep their own terms. See `compliance/LICENCES.md`.

## Note on AI assistance

An AI assistant was used for code drafting and document preparation. All outputs,
including every reference, were verified by the author. The assistant is not an
author.
