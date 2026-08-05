# Phase 0 Step 1 — J-lens code inspection and adapter-points catalogue

**Repo:** `github.com/anthropics/jacobian-lens`
**Commit inspected:** `581d398613e5602a5af361e1c34d3a92ea82ba8e` (2026-07-02, sole commit on `main`)
**Licence:** Apache-2.0. README: *"Reference implementation. Not maintained and not accepting contributions."*
**Method:** clone + read. Nothing installed, nothing executed, no model loaded.
**Satisfies:** guide Phase 0 exit criterion *"adapter points for a non-language vocabulary identified"*

---

## 1. What the repo contains

~1,050 lines of library code in eight modules, plus tests, prompt data, and a notebook.

| Module | Lines | Role |
|---|---|---|
| `jlens/protocol.py` | 52 | `LensModel` Protocol — **the port boundary** |
| `jlens/hf.py` | 211 | HuggingFace adapter, `Layout` auto-detection |
| `jlens/lens.py` | 216 | `JacobianLens`: save/load/merge/transport/apply |
| `jlens/fitting.py` | 388 | `fit`, `jacobian_for_prompt`, position masking |
| `jlens/hooks.py` | 74 | `ActivationRecorder` — forward hooks |
| `jlens/vis.py` | 515 | slice-page rendering (d3) |
| `jlens/examples.py` | 181 | bundled demo prompts |
| `tests/tiny.py` | 87 | **worked from-scratch `LensModel` adapter** |

Public API (`__all__`), complete: `ActivationRecorder`, `HFLensModel`, `JacobianLens`, `Layout`, `LensModel`, `configure_logging`, `fit`, `from_hf`, `jacobian_for_prompt`.

---

## 2. Step 0's open question, settled

**There is no intervention machinery in the code. Confirmed, not inferred.**

A grep across every `.py` and `.ipynb` for `ablat|steer|intervene|intervention|clamp|patch|swap|zero_out|project_out|set_activation` returns zero hits in library code — the only matches are `monkeypatch` fixtures in `tests/test_vis_modes.py`. Supporting evidence from reading rather than grepping:

- `hooks.py` contains exactly one class, `ActivationRecorder`. It registers forward hooks that **store** each block's output. It never writes back. There is no write-side hook anywhere.
- `JacobianLens.apply()` is decorated `@torch.no_grad()` and detaches all recorded activations.
- Nothing in the package mutates a residual stream.

The release is a **readout instrument**: fit `J_l`, transport `h @ J_l.T`, unembed, rank, visualise.

### 2a. But the intervention *protocols* are specified in prose

`data/experiments/README.md` and `data/evaluations/README.md` document the paper's experimental procedures in reimplementable detail. Two definitions carry most of the weight:

- **Swap** — *"clamping a lens coordinate replaces one token's direction with another's at every band layer at the specified positions, then samples the continuation."*
- **Steering** (from `verbal-introspection`) — the direction is *"the unit-normalized transpose row for that token, scaled by the layer's mean residual norm times a strength scalar,"* added to the residual stream at every band layer over a specified span; strength 0 is the control.

So the harness has to be written, but it is written **to a specification**, not reconstructed from a paper figure. That is a materially better position than Step 0's worst case.

### 2b. The gap that actually matters: no ablation protocol, anywhere

The two documented intervention types are **swap** (replace direction A with direction B) and **steering** (add a scaled direction). Neither is ablation. Nothing in the release specifies zeroing or projecting out a subspace.

Proposal §4.4 words Control A as confirming *"ablation of the identified subspace disproportionately harms multi-step tasks."* **That specific experiment is not in the released materials** — not as code, and not as a documented protocol.

Released prompt sets, in full:

| Set | Items | Nature |
|---|---|---|
| `data/evaluations/lens-eval-{multihop, multilingual, poetry, order-ops, association, typo}` | 93 / 107 / 98 / 55 / 102 / 96 | **Readout-quality** evals. pass@k over lens rank of `intermediates`. No intervention. |
| `data/experiments/probe-swap` | 90 two-hop factual | Swap the bridge entity, score whether the answer follows |
| `data/experiments/{verbal-report, verbal-introspection, top-down-summoning, flexible-generalization}` | — | Swap / steering protocols |
| `data/experiments/{directed-modulation, selectivity-language, selectivity-linecount, capacity, dual-task, ignition}` | — | Readout-based, various |

**Decision this forces (do not let it pass silently).** Control A can be re-specified one of two ways:

- **(a) Adopt a released protocol.** `probe-swap` is the natural candidate: 90 two-hop prompts, baseline greedy answer vs. swapped answer, a clean causal test on multi-step factual reasoning. Control A then becomes a *genuine replication against released prompts*, which is stronger than the alternative and closer to what §4.4 was reaching for. **Open question requiring the paper:** the README says probe-swap replaces a *linear-probe* direction, not a J-lens direction — check §probe-swap in the paper before treating it as a J-lens validation.
- **(b) Implement ablation from the paper's description.** Keeps the proposal's wording, but Control A stops being a replication of released code and becomes a reimplementation validated against nothing.

Recommend (a) if the paper supports it. Either way, proposal §4.4's phrase *"using Anthropic's released code"* must be amended in the paper — record it under `preregistration/amendments.md` or as a proposal correction.

---

## 3. The port boundary

Better than the guide anticipated. Rather than hardcoding architecture assumptions through the codebase, everything is typed against one Protocol, and `tests/tiny.py` is an 87-line working example of implementing it from scratch — a `TinyDecoder` with a toy byte tokenizer, four residual blocks, `vocab_size=32`, CPU only.

`jlens/protocol.py`, `LensModel`, complete requirement list:

```
n_layers: int
d_model:  int
layers:   Sequence[nn.Module]
tokenizer: Any                  # needs .decode(ids) -> str
encode(text, *, max_length) -> Tensor[1, seq_len]
forward(input_ids) -> Any       # residual stack, NO lm head; must build autograd graph
unembed(residual[..., d_model]) -> Tensor[..., vocab_size]
```

**The tokenizer is not used by the science.** The docstring is explicit: *"Tokenizer used by the visualisation helpers … Fitting and `apply()` never touch it."* No tokenizer port is required — a stub mapping item-token id → item title is enough, and would make slice pages readable.

---

## 4. Adapter points for an item-token vocabulary

| # | Requirement | Recommender must supply | Risk |
|---|---|---|---|
| 1 | `layers` — indexable stack of residual blocks, constant `d_model` | GPTRec is GPT-2-based and the GPT-2 layout (`transformer.h`, `ln_f`, `wte`) is already in `_LAYOUTS`. HSTU's pointwise-aggregated blocks are **not** a standard residual stack — verify before choosing it | **High for HSTU, low for GPTRec** |
| 2 | `unembed: [..., d_model] -> [..., vocab]` over the item vocabulary | This is proposal §2's architectural precondition, restated as a concrete method. Semantic-ID models have it | Low |
| 3 | `forward` builds an autograd graph **and is deterministic across batch elements** — the fitting estimator replicates the prompt along the batch axis | Eval mode, dropout off, no sampling, no batch-dependent normalisation | Medium — recommenders commonly use dropout |
| 4 | `encode(text: str, ...)` | Annotated `str`, not enforced. Adapter takes an interaction sequence and returns `[1, seq_len]` ids | Low — but the signature lies; document it |
| 5 | `tokenizer.decode` | Vis only. Stub it | None |
| 6 | **`SKIP_FIRST_N_POSITIONS = 16`** (`fitting.py:42`), exposed as `skip_first=`. Rationale: early positions are attention sinks with atypical residual statistics | Must be **re-derived** for the recommender, not inherited | **Highest.** Interaction sequences truncated at 20–50 discard 30–80% of positions at `skip_first=16`. A wrong value here produces a self-inflicted null indistinguishable from a real one — exactly proposal §4.5's "readout too weak" branch |
| 7 | `max_seq_len=128` default in `fit` | Sequence budget; recommender sequences are typically shorter | Low, but interacts with #6 |
| 8 | `force_bos=True` in `from_hf` — assumes a BOS attention sink | Recommenders may have no BOS. A from-scratch adapter sidesteps the flag but not the underlying assumption | Medium |
| 9 | `dim_batch=8`; cost is 1 forward + `ceil(d_model/dim_batch)` backwards per prompt | Fitting cost scales with `d_model`, not parameter count | Low |

### 4a. The single-token constraint — elevate this

Every released experiment and eval scores **single vocabulary tokens**. `capacity.json` even filters its word pools to entries that *"tokenize to a single token under the target model."* Secondary reporting states multi-token concepts require an extension the paper describes as incomplete.

TIGER-style semantic IDs represent **one item as several codebook tokens**. If one item ≠ one vocabulary token in the chosen architecture, then "read out an item" is not the operation J-lens performs, and the port is on shakier ground than the clean `LensModel` boundary suggests.

**Action for Phase 1 model selection:** confirm the item→token cardinality before committing. GPTRec's SVD tokenization needs checking on exactly this. This belongs in the Phase 1 go/no-go, not discovered in Phase 2.

---

## 5. Incidental findings worth carrying forward

- **`fit()` is already resumable** — `checkpoint_path`, `checkpoint_every=1`, `resume=True`. AI guide §1.4's "build it resumable from the start" is partly free.
- **`use_jacobian=False` in `apply()`** gives a vanilla logit-lens baseline at no cost. A useful comparison control for both Phase 0 and Phase 3.
- **Linearity is structural.** `transport()` is `residual @ J.T`, and `J_l` is a single `[d_model, d_model]` matrix per layer. Proposal §4.5's nonlinear-false-negative concern is inherent to the instrument, not a implementation detail that could be tuned away. The nonlinear sensitivity probe is load-bearing.
- **Lens artifacts are tiny** — `[d_model, d_model]` fp16 per layer; ~1.2 MB/layer at `d_model=768`. Storage and transfer are non-issues.
- **`from_pretrained` imports `huggingface_hub` lazily** — only when the path isn't a local file or directory. HF is blocked in Claude's sandbox (AI guide §1.3); fine on Colab, and local `.pt` loading works anywhere.
- **`merge()` requires agreement on `source_layers` and `d_model`** — shard the sweep accordingly.

---

## 6. Open items requiring the paper (not the code)

1. Does `probe-swap` use a J-lens direction or a separate linear probe? Determines whether Control A option (a) is viable.
2. How is the **workspace band** (the mid-network layer range) determined? Every experiment reports over it; nothing in the code computes it. It must be derived for the recommender, and the method for doing so is not in the release.
3. Which experiment produces the reported multi-hop ablation collapse, and what exactly was ablated? This is the effect magnitude Phase 0 Step 5 needs to record.
