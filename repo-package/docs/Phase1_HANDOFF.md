# Phase 1 handoff — what Phase 0 learned that changes how Phase 1 should be done

**Written:** 2026-08-02, immediately after gate G0 (partial, proceed).
**Purpose:** the forward-looking distillate of Phase 0. Not a summary — the
consolidated log and `Phase0_OVERVIEW.md` cover what happened. This covers what
*changes* as a result.
**Read alongside:** `EXECUTION_GUIDE.md` Phase 1; proposal §2, §4.5, §7, §5 row 1.

---

## 1. The model criteria grew from three to six

The guide's Phase 1 §1a lists three. Phase 0 added three more, and two of them
were learned the hard way.

| # | Criterion | Source | How to check |
|---|---|---|---|
| 1 | Autoregressive over a discrete token vocabulary | guide, proposal §2 | Architectural precondition — if false, J-lens has no target |
| 2 | Intermediate activations and output projection accessible | guide | Concretely: the `LensModel` protocol, §2 below |
| 3 | Fits compute with room for the Phase 3 sweep | guide | Much weaker than expected — §6 |
| 4 | **Homogeneous, indexable residual stack at constant `d_model`** | session 11 | Read `config.layer_types` — **and look inside sub-configs**, §3 |
| 5 | **Forward pass deterministic across batch elements** | session 03 | Fitting replicates the prompt along the batch axis; dropout, sampling, or batch-dependent normalisation break it |
| 6 | **Item-to-token cardinality — conditional, not hard** | sessions 03, 06 | §4 |

Criterion 4 exists because Qwen3.5-4B was selected, used for a full headroom run,
and only then discovered to be a hybrid: 24 of its 32 layers are linear-attention
(SSM/Mamba-style), with a vision tower attached. The criterion had been written
for Phase 1 and was never applied to the Phase 0 model because "a Qwen" was
assumed to be a conventional transformer.

**The generalisable lesson: check the architecture from the config, not from the
name.** Three days and a full headroom run were spent before this surfaced.

## 2. The port boundary is exactly seven members

Better than the guide anticipated. `jlens/protocol.py` types everything against
one Protocol, so there is no scattered hardcoding to hunt down:

```
n_layers: int
d_model:  int
layers:   Sequence[nn.Module]      # indexable stack of residual blocks
tokenizer: Any                     # needs .decode(ids) -> str
encode(text, *, max_length) -> Tensor[1, seq_len]
forward(input_ids) -> Any          # residual stack, NO lm head; builds autograd graph
unembed(residual[..., d_model]) -> Tensor[..., vocab_size]
```

Three things worth knowing before Phase 2:

**`tests/tiny.py` is a working 87-line from-scratch implementation.** It is the
template for the recommender adapter — a toy decoder with a byte tokenizer, four
residual blocks, `vocab_size=32`, CPU only. Read it before writing anything.

**The tokenizer is not used by the science.** `protocol.py` states it outright:
*"Fitting and `apply()` never touch it."* It is used only by the visualisation
helpers. A stub mapping item-token id → item title is sufficient, and would make
readouts legible for free.

**`_LAYOUTS` already supports GPT-2** — `Layout("transformer", layers="h",
norm="ln_f", embed="wte")` — so a GPT-2-based recommender inherits a working HF
adapter and may need no custom `LensModel` at all. Verified by direct read.

### Recommendation: write the adapter in Phase 1, not Phase 2

The guide places the port in Phase 2. Doing it in Phase 1 is a change worth
making, because writing the adapter is **the definitive test of criteria 2, 4 and
5** — the three that are otherwise judgement calls from a config file. Phase 1's
exit criterion "activation access confirmed" is best satisfied by a working
adapter and a passing smoke test, not by reading documentation.

It also front-loads Phase 2's main risk into the phase that has slack.

## 3. Read `layer_types` from nested sub-configs

A concrete bug worth not repeating. The first architecture check looked for
`layer_types` and `hidden_size` at the top level of the config dict. Qwen3.5
nests them inside `text_config`, so the check reported "uniform stack" on a model
that is 75% linear-attention.

`scripts/step0_verify_model.py` has the fixed version — `find_nested()` searches
the top level and one level of sub-configs, and the script prints the full config
JSON so an unexpected shape is visible rather than silently missed. **Reuse it,
pointed at the recommender.** It also checks the model is not a
`*ForConditionalGeneration` and reports any hybrid/SSM indicator fields
(`mamba_ssm_dtype`, `full_attention_interval`, `linear_conv_kernel_dim`,
`mtp_num_hidden_layers`).

## 4. The single-token constraint is conditional, not disqualifying

Session 03 concluded that an architecture whose items span several semantic-ID
tokens would be blocked, because the J-lens is vocabulary-indexed. Session 06
read §A.9 and found that too strong.

**The template lens** derives a per-concept vector without using the vocabulary
or the unembedding at all. For each concept: generate contexts where it is the
natural continuation, ending just before it appears; average the residual stream
at the final position; centre against the mean of all other concepts and whiten
by `(Σ_ℓ + λI)⁻¹`. The resulting vectors are used exactly as J-lens vectors are,
minus the unembedding step.

**Its precondition maps onto recommenders unusually well:**

| Template lens needs | Recommender supplies |
|---|---|
| An enumerable concept vocabulary | The item catalogue, by construction |
| Contexts where concept *w* is the natural continuation, ending just before it | **Every interaction sequence ending just before item *i***, naturally varied across users |
| Residual-stream access at a chosen layer | Same requirement as the J-lens |
| No vocabulary/unembedding involvement | Multi-token semantic IDs become irrelevant |

The step that is laborious in the language domain — having a model write hundreds
of passages per word — is **free here**, because the dataset already contains
exactly those sequences. This is the one place so far where the port looks easier
than the original.

**The counterweight is serious and must not be lost.** The paper states the
template lens "has some properties more similar to the tuned lens, and inherits
some related pathologies." Documented shortcomings: it sometimes **skips to the
answer prematurely in early layers** rather than surfacing intermediates; its
final-layer readouts contain the next sampled word in the top ten only **67%** of
the time; a small set of words appear spuriously often, mitigated by filtering
them out, which the paper calls effective but unprincipled.

The first of those is a **false-positive route for H1**: proposal §4.1 defines the
construct as a subspace with *disproportionate causal influence*, and a
correlational readout that skips to the predicted next item would surface
directions that look causally important but are partly just the output.

**Practical guidance:** prefer one item = one vocabulary token, for instrument
quality rather than feasibility. If the chosen architecture uses multi-token
semantic IDs, the template lens is a viable fallback — but it means implementing
an appendix method on top of everything else, and the resulting H1 evidence is
weaker in a specific, statable way.

**The oracle lens is out of scope.** It requires fine-tuning two auxiliary
models. Do not consider it.

## 5. `skip_first` — the highest-risk inherited default

`SKIP_FIRST_N_POSITIONS = 16` in `jlens/fitting.py`, exposed as `skip_first=`.
Rationale in-source: early positions are attention sinks with atypical residual
statistics.

**Interaction sequences are short.** At length 20–50, `skip_first=16` discards
30–80% of positions. Inheriting it unexamined is a direct route to a null that
looks genuine and is not — proposal §4.5's "readout too weak" branch,
self-inflicted.

**§A.7 resolves this cheaply.** The paper tested position masking, including
"excluding the first several tokens to let the model burn in," and reports:
*"None of these yielded a meaningful improvement over the default."* Since
skipping buys nothing measurable, **set `skip_first` low or zero and record the
choice.** Do not spend a sweep re-deriving it.

Phase 0 used `skip_first=4` throughout.

## 6. Compute is not the constraint, and lens fitting is nearly free

AI guide §1.4 predicted Phase 0 would be the most expensive phase. That held, but
for the wrong reason: the expense was in *discovery* — that the release contains
no ablation code, that band derivation is a step absent from the plan, that no
affordable open model reaches near-ceiling — not in GPU time.

Measured costs on an A100-80GB:

| Task | Cost |
|---|---|
| Headroom check, 90 prompts | minutes |
| Band derivation, 4 statistics × 35 layers × 20 passages | ~2 units |
| Readout verification, 90 prompts × 24 layers × 2 (true + foil) | ~1 unit |
| **Control A — 241 conditions × 73 prompts + intact side** | **~18 units** |
| Coarse intact tasks, 2 × 150 items × 18 conditions | ~8 units |

**§A.7's corpus-size finding:** *"J-lens beats the logit lens and tuned lens
baselines with as few as 10 prompts, with modest improvements coming from
additional data."* The published Qwen3-8B lens stopped at 479 of a requested 1000
on its own convergence criterion. Fitting is close to free; the expense is the
ablation evals.

Phase 1 models are two orders of magnitude smaller than Qwen3-8B. HSTU-BLaIR is
four transformer blocks with four attention heads; GPTRec is GPT-2-based.
**Both run on a free-tier T4.**

That said — fitting cost scales as `ceil(d_model / dim_batch)` backward passes
per prompt with the graph retained, so it tracks `d_model`, not parameter count.
For a small recommender this is trivial. Confirm rather than assume.

## 7. Two process lessons that cost real time

**Keep everything in one process.** Session 09 aborted on CUDA OOM because a
model loaded in the notebook kernel and a second copy loaded by a `!python`
subprocess coexisted on one T4. Either run everything in-kernel or shell
everything out — never both in one session.

**Use `PYTHONPATH`, not `pip install -e`.** The editable install of `jlens`
silently failed to register in Colab, and more importantly `!python` subprocesses
do not inherit `sys.path` edits made in a notebook kernel. `os.environ["PYTHONPATH"]`
**is** inherited. `notebooks/` all use this pattern.

## 8. Task construction — one design constraint Phase 0 did not anticipate

This is the most consequential forward-looking item in this document, and it is a
**suggestion, not an established requirement.**

Stage B2 (session 14) verified that the J-lens readout surfaces the *unspoken
intermediate* before ablating anything: for the Amazon-River prompt, `Brazil`
reaches median rank **1** at L30, against 8.9% top-10 for matched foils. That
check was possible only because `probe-swap.json` carries an `intermediate` field
for every prompt.

It turned out to be one of the most valuable things Phase 0 produced, because it
separates two null hypotheses that are otherwise indistinguishable: *the content
was never in the readout* versus *the content was there and ablating it did not
matter*.

**Phase 2 will want the same check in the recommender domain, and it is only
possible if the hard tasks have an identifiable intermediate.**

The complication: the J-lens readout is over *item* tokens. If a hard task's
intermediate is an abstract inferred preference ("this user has shifted toward
sci-fi"), the readout cannot surface it directly. Two constructions that would
work:

1. **Intermediate as a representative item.** Construct hard tasks where the
   inferred preference is expressible as one or more specific catalogue items,
   and check whether the readout surfaces those.
2. **Intermediate as a category, scored over its members.** Check whether items of
   the inferred category are over-represented in the top-k readout relative to a
   matched foil category.

Either is implementable and either enables a Stage B2 analogue. **Both require
recording the intended intermediate at task-construction time** — which means
deciding this during Phase 1, not discovering the need in Phase 2.

**This does not override the guide.** Guide Phase 1 §1c defines the easy/hard
split, proposal §4.5 gives the worked examples (preference shift across
distractors; cross-category taste transfer), and §10 step 3 requires the split
frozen before Phase 3. This adds a field to record, not a change to the split.

## 9. Development steps

Roughly in order. Steps 1–3 need no GPU.

**Step 1 — Verify the candidate architecture** *(no GPU, ~30 min)*
Run `scripts/step0_verify_model.py`, pointed at the recommender. Confirm criteria
1, 4, 5. Read `config.layer_types` from nested sub-configs. If it is a
`*ForConditionalGeneration`, or has SSM indicators, or has mixed layer types —
stop and reassess before investing.

**Step 2 — Check item-to-token cardinality** *(no GPU)*
Does one catalogue item map to one vocabulary token? GPTRec's SVD tokenisation
needs checking on exactly this. If not, §4 applies and the template lens becomes a
Phase 2 dependency that needs scoping now.

**Step 3 — Write the `LensModel` adapter** *(CPU, laptop)*
Seven members, `tests/tiny.py` as the template. Smoke-test on CPU with random
weights. This is the definitive check on criteria 2, 4 and 5, and it front-loads
Phase 2's main risk.

Specific things to verify while writing it:
- `forward()` must build an autograd graph and be **deterministic across batch
  elements** — `model.eval()`, dropout off, no sampling.
- `unembed()` must map `[..., d_model] → [..., vocab]` over the item vocabulary.
- `encode()` is annotated `text: str` but not enforced; the adapter takes an
  interaction sequence and returns `[1, seq_len]` ids. **The signature lies —
  document it.**
- `force_bos=True` in `from_hf` assumes a BOS attention sink. A from-scratch
  adapter sidesteps the flag but not the underlying assumption.

**Step 4 — Dataset selection** *(guide §1b)*
Proposal §7: Amazon Reviews 2023 subsets (Video Games, Office Products, Musical
Instruments), MovieLens-1M, Steam. Two criteria that bite later:

- **Item metadata must be pre-existing and rich enough for Phase 5.** Verify
  provenance now — it must predate and be independent of this analysis. If the
  dataset has no independent category/tag/description metadata, H3 is untestable
  on it and you should know before investing.
- **Sequence lengths must support the hard-task construction** — and must survive
  whatever `skip_first` you set. Check this against step 1's model choice.

**Step 5 — Construct the easy/hard task gradient** *(guide §1c — the important part)*
- Easy: single-hop next-item prediction from recent history.
- Hard: compositional or multi-step preference inference. Proposal §4.5's worked
  examples: inferring a preference shift across a sequence containing distractor
  interactions; transferring an inferred taste across categories.
- **Record the intended intermediate per hard item** (§8).
- Match confounds where possible: sequence length, item popularity distribution,
  category coverage. Otherwise a differential ablation effect might just be
  tracking sequence length.
- **Freeze and commit with a timestamp predating any Phase 3 work.**

**Step 6 — Validate the gradient is real → G1**
Confirm the base model performs measurably worse on hard than easy. If it is
equally good or equally bad at both, the split is not capturing difficulty and
Phase 4 cannot distinguish anything.

**Do this the way Phase 0 did the headroom check:** commit the threshold — what
size of easy-vs-hard gap counts as a real gradient — **before looking at the
number.** That discipline is what made the headroom result usable across three
models rather than something to argue about after the fact.

## 10. Best practices that earned their place in Phase 0

**Commit the threshold before seeing the number.** Used at the headroom gate and
again in `prereg_controlA.md`. When Qwen3.5-4B came in at 63.3% against a 70%
threshold, the pre-written 50–70% band already specified the consequence
("partial by construction"), so there was nothing to argue about.

**Pre-register the prediction, including the boring one.** `prereg_controlA.md`
§2.1 predicted `light` might show little effect because eight downstream layers
could re-establish content. It came in weakest at 24%, and that was a prediction
tested rather than a puzzle rationalised.

**Build controls that can fail.** `test_guard_actually_changes_what_gets_selected`
asserts the clean-top-k guard is not a no-op on its input. A control that cannot
fail is not a control. Four tests in Phase 0 exist for this reason and each caught
a real bug.

**Test on real data, not just synthetic.** Three bugs survived synthetic tests and
were caught only against real data or real dtypes: the participation-ratio
overflow, the `prepare_lens` dtype cast, and the monotonicity bug in the rescorer.
The toy model was float32 with a 64-token vocabulary and could not have caught any
of them.

**Report by category, not just aggregate.** Control A's clean baseline hid a
factor-of-two spread: `city-capital` and `language-capital` at 100%, `multihop` at
51.7%. Ablation can only show a fall where there is room to fall.

**Write the correction, don't edit the record.** Session 03 recommended one Control
A design; session 04 reversed it after reading the paper properly. The reversal is
logged as a correction rather than the earlier entry being edited. Same for the
band heuristic that returned the wrong start — it was **not** retuned to the data
that broke it, because fixing a measurement to its own result is the failure mode
the whole project exists to avoid.

**Estimates from Claude have run consistently optimistic.** Compute savings from
caching were estimated at 37×, then 2–2.5×, and measured at 1.4×. Discount and
prefer measurement — the timing probe cost ~1 unit and replaced three wrong
guesses with a number.

## 11. Open items Phase 1 inherits

1. **The ignition experiment is not implemented.** All four band statistics are
   lens-derived, so a layer effect could be an artifact of the method. The paper
   answers this with an experiment that uses no lens: replace a concept token's
   input embedding with a mixture `(1-α)·e_B + α·e_A`, sweep α, and measure where
   the activation sits along the line joining that trial's pure-B and pure-A
   activations. Adequate to skip in Phase 0; **required for Phase 2**, where only
   kurtosis and effective dimensionality port without reinterpretation. The
   recommender version — mixing two item embeddings in a carrier interaction
   sequence — is directly constructible, and `ignition.json` (40 carrier
   templates, 66 pairs, plus idiom and scrambled controls) is a usable template.

2. **Band derivation is a step in neither the proposal nor the execution guide.**
   Phase 0 added it. Phase 2 needs it again, and it belongs in the guide as a
   Phase 2 exit criterion rather than being rediscovered.

3. **Control A is partial.** Every downstream claim is bounded by an instrument
   validated under partial headroom, on a model that answers 68.5% of two-hop
   items correctly, with a failed intact-side criterion whose bound is narrow but
   real. Three statements are required in the paper — see `GATE_G0.md`.

4. **`prereg_phase3.md` §5–§8 are blocked on Phases 1–2.** §1–§4 are fixed. Gate
   G2 blocks Phase 3 until the whole thing is committed.
