# Pre-registration — Control A band and dose-response

**File:** `preregistration/prereg_controlA.md`
**Drafted:** 2026-07-28 · **Status:** for sign-off before any ablation runs
**Governs:** the band, the three ablation strengths, and what counts as support
**Companion to:** `DECISION_control_A.md` (protocol), `THRESHOLD_headroom.md` (model)

The execution guide requires pre-registration for Phases 3 and 4. Control A is
Phase 0 and is not formally covered — but the reasoning is identical, and a band
chosen after seeing ablation results would be indefensible. This is written
before the first ablation runs on a real model.

---

## 1. Evidence for the band

From `results/raw/band_qwen3-8b/band_stats.json`, Qwen3-8B, 36 layers, lens
covering source layers 0–34, 20 WikiText passages.

| Statistic | Onset | Character |
|---|---|---|
| autocorrelation | L18 at half-peak | gradual rise from L15; peaks L24 |
| effective dimensionality | L19 (1.6×), then **L22 (2.9×)** | second jump is sharp |
| top-k accuracy | L20 leaves the floor | gradual |
| excess kurtosis | minimum L21 | **flat-bottomed L15–22** (0.80–1.02) |

**End:** unambiguous. `topk_acc` crosses 0.5 at L31 and accelerates hardest
across 31→34 (+0.12, +0.12, +0.15). Kurtosis peaks at exactly L31. Effective
dimensionality begins its final climb there. **L31.**

**Start:** genuinely uncertain. Four soft estimates spanning L15–L22; L20 is
their median, not a convergence.

### 1.1 Recorded anomaly — kurtosis does not match the paper's description

The paper describes kurtosis as *"~0 through the first third, rising from ~⅓
depth."* Observed: **3.74 at L0, peaking 4.44 at L3**, falling to a minimum of
0.80 at L21, then rising to 1.94 at L31.

The band-relevant half matches (minimum, then rise through the band, peaking at
the motor boundary). The early spike is an additional feature the paper does not
describe. Two candidate explanations, neither tested:

1. Early layers are dominated by token identity, so transport-and-unembed yields
   a peaked distribution — high kurtosis for a trivial reason.
2. §A.7 notes that targeting the final layer "can sometimes increase the number
   of noisy artifacts in lens-readouts." This lens used `target_layer: null`,
   i.e. the final layer. The spike may be a recipe artifact.

**This anomaly is reported whatever Control A shows.** It does not affect the
band, because "minimum then rise" is unambiguous regardless of L0–L3.

### 1.2 Recorded methodological limitation

All four statistics derive from the J-lens, so a layer effect could be an
artifact of the method rather than a fact about the model. The paper answers
this with the ignition experiment, which uses no lens. **Not implemented here.**
For Phase 0 — replicating a published band on a language model — the four are
accepted as adequate. For Phase 2 in the recommender domain they will not be.

---

## 2. The band and the three strengths

**Band: L20–31** (12 of 36 layers, 57%–89% of depth).

Note for the write-up: the paper's band was 38%–92% of depth, i.e. **54%** of
the stack against our **33%**. Ours is narrower, entirely at the bottom.

**Nesting: shared start** — signed off 2026-07-28.

| Strength | Layers | Width |
|---|---|---|
| light | L20–23 | 4 |
| medium | L20–27 | 8 |
| heavy | L20–31 | 12 |

**Rationale.** The paper fixes k=10 and varies the layer range; its one
documented sub-range is *"the first third of the workspace range"* — the bottom
of the band. Shared-start is the only nesting with a counterpart in the paper,
and Control A is a replication. A shared-*end* nesting would plausibly show a
stronger effect at narrow widths (ablating immediately before readout, with no
downstream layers left to recover in), and choosing it for that reason would be
selecting a design by its expected result.

### 2.1 Pre-registered prediction about `light`

Under shared-start nesting, ablating L20–23 leaves **eight downstream layers** in
which the model may re-establish suppressed content. **`light` may therefore
show little or no effect even if the workspace is real.**

Recorded in advance so that, if observed, it is a predicted outcome rather than
a puzzle rationalised after the fact. A flat light→medium→heavy curve is
therefore *weak* evidence against the workspace interpretation under this
nesting — weaker than it would be under a symmetric nesting.

---

## 3. Band sensitivity — the start is not treated as known

Because §1 shows the start is uncertain across L15–L22, `heavy` is additionally
run at two alternative starts:

| Condition | Layers | Width | Purpose |
|---|---|---|---|
| heavy (primary) | L20–31 | 12 | the band as derived |
| heavy-early | L15–31 | 17 | tests under-ablation: if the workspace extends below L20, the primary band leaves content intact and produces a false negative |
| heavy-late | L24–31 | 8 | tests over-ablation into the sensory block |

**`heavy-late` (L24–31) and `medium` (L20–27) are both 8 layers with different
starts.** Comparing them isolates start position from width, which no other pair
in the design does.

If the result holds across all three starts, the band choice is not load-bearing
and the paper says so. If it does not, that is the single most informative thing
Control A will produce, and it is reported rather than resolved by picking the
start that works.

---

## 4. Criteria — fixed before any run

Clean baseline: **58/90 = 64.4%** strict on probe-swap (`results/raw/headroom_qwen3-8b/`).

| Criterion | Threshold | Rationale |
|---|---|---|
| **Substantial degradation** | heavy ablation reduces strict accuracy by **≥50% relative** (≤32.2% absolute) | The paper saw near-ceiling → near-zero. Absolute-point thresholds do not transfer from a near-ceiling model to a 64.4% one; relative reduction does |
| **Dose-response** | heavy drop exceeds light drop by **≥10 percentage points** | Binomial SE at n=90, p≈0.5 is ~5.3pp. 10pp is roughly 2 SE. Medium is expected between them but small inversions are within noise and are **not** treated as failures |
| **Candidate vs random** | candidate drop exceeds **every** matched random draw, at every strength | see §4.1 |
| **Intact side** | top-1 match on WikiText **≥0.90** at heavy | `PRESERVED_TOP1` in `ablation/intact.py`; the paper gives no numeric criterion, so this is a judgment call recorded rather than buried |

**Pass** = all four. **Partial** = substantial degradation with at least one
other criterion failing; *document which*, since each bounds a different
downstream claim. **Fail** = no degradation, or the random control matches the
candidate, or the intact side collapses (general damage).

Effect **magnitudes** are recorded, not just directions — Phase 3 needs to know
what a real positive effect looks like through this instrument.

### 4.1 Number of random draws — decision required

The current grid uses **5 random draws** per condition. If the candidate must
exceed all of them, the strongest attainable statement under exchangeability is
**p ≈ 1/6 = 0.167**. That is not a meaningful significance level, and proposal
4.8 makes the matched random baseline the load-bearing control for the whole
design.

The timing probe measured the full sweep at **~20 minutes / ~5 units**. Raising
draws is close to free:

| Draws | Best attainable p | Est. sweep time |
|---|---|---|
| 5 (current) | 0.167 | ~20 min |
| 10 | 0.091 | ~35 min |
| **19** | **0.050** | ~60 min |

**Recommendation: 19 draws.** It is the smallest number giving p ≤ 0.05, it
costs about 15 units instead of 5, and a weak random baseline would undermine
Control A and every Phase 3 result that inherits this harness.

**Decision:** ☐ 5 ☐ 10 ☑ 19 ☐ other _______

---

## 5. Fixed parameters

| Parameter | Value | Source |
|---|---|---|
| Model | Qwen/Qwen3-8B, bfloat16 | `DECISION_model_change.md` |
| Lens | `qwen3-8b/.../Qwen3-8B_jacobian_lens.pt`, n=479 | published; **final-layer recipe, a recorded deviation from §A.7** |
| k | 10 | paper's ablation value; not swept in Control A |
| Projection mode | `subspace` | `rspace_ablation/README.md`; `sequential` not run |
| Clean-top-k exclusion | 10 | paper's confound guard; **never 0** |
| Degrading eval | 90 probe-swap prompts, strict scoring | `DECISION_control_A.md` §4.4 |
| Intact eval | 20 WikiText passages, top-1 match primary | `ablation/intact.py` |
| skip_first | 4 | §A.7: position masking gave no meaningful improvement |
| Seeds | recorded per draw | guide §1.2 |

**Reporting is by category as well as in aggregate.** `city-capital` and
`language-capital` are at 100% clean while `multihop` is at 51.7%; ablation can
only show a fall where there is room to fall, so an aggregate number understates
the effect where it matters and overstates it elsewhere.

---

## 6. Sign-off

**Band L20–31:** ☑ accepted ☐ modified _______
**Nesting (shared start):** ☑ accepted 2026-07-28
**Band sensitivity conditions:** ☑ accepted ☐ modified _______
**Criteria §4:** ☑ accepted ☐ modified _______
**Random draws §4.1:** ☐ 5 ☐ 10 ☑ 19

**Signed:** Stanley Zhou **Date:** July 28, 2026

*Committed before the first ablation on a real model. Deviations go in
`amendments.md` with justification — deviating is allowed, hiding it is not.*
