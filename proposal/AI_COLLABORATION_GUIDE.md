# AI Collaboration Guide — R-Space Generalization Test

**Companion to:** `jspace_generative_recommenders_proposal.md` (**the proposal**) and `EXECUTION_GUIDE.md` (**the guide**)
**Purpose:** how to use Claude on this project without letting it become a source of scope drift; plus the hardware reality the plan has to fit inside.
**Repo location:** `proposal/AI_COLLABORATION_GUIDE.md`

---

## 0. Precedence

The proposal is the source of truth for *what is claimed*. The guide is the source of truth for *how to run it*. This document is the source of truth for *how to use an AI assistant while running it*, and for *what hardware it has to run on*.

Where this document conflicts with either of the others, they win and this one gets corrected.

---

## 1. Hardware and compute constraints

### 1.1 Local machine

ASUS Zephyrus G14 (2022) — Ryzen 9 6900HS, Radeon RX 6700S, 16 GB RAM, 1 TB storage.

**The discrete GPU is not usable for this project.** The 6700S is mobile RDNA2. PyTorch's ROCm builds are Linux-only and do not officially cover mobile RDNA2 parts. The Windows path (`torch-directml`) has real gaps in autograd coverage, and J-lens is a Jacobian method — it depends on autograd working correctly and completely. Debugging a half-supported backend while trying to establish whether a null result is genuine is exactly the situation to avoid.

**Treat the laptop as CPU-only.** This is not a serious loss. Its job is development, not training.

What the laptop handles fine:
- All code writing and unit testing against small synthetic tensors — ablation harness, sweep bookkeeping, random-subspace draw logic, statistical tests
- Dataset prep and task construction (MovieLens-1M is ~25 MB; Amazon Reviews 2023 category subsets are comparably small)
- Phase 5 metadata correlation work (pure CPU)
- All results analysis and all writing

The only real bottleneck is GPU-hours, and those are rented.

### 1.2 Google Colab

| | Free | Pro (~$11.99/mo) | Pro+ (~$49.99/mo) |
|---|---|---|---|
| GPU | T4 (16 GB) when available | T4 / L4 / occasional A100 | Priority on best available |
| Compute units | n/a — best effort | 100/month | 500/month |
| Background execution | No | **No** | Yes |
| Session behaviour | Dies on idle, ~12 h cap, GPU not guaranteed | Longer, still browser-tab-dependent | Longest |

Compute unit burn rate: T4 ≈ 1.96 units/hour (~51 h per 100 units); A100 ≈ 15 units/hour (~6–7 h per 100 units). Unused units carry over up to 90 days.

Colab reaches HuggingFace normally.

**Supplement:** Kaggle Notebooks offers roughly 30 free GPU hours/week (P100 or dual T4), more predictably allocated than free Colab. Useful for the Phase 3 sweep specifically.

### 1.3 Claude's sandbox (this chat interface)

Verified directly: 1 CPU core, ~3 GB RAM, no GPU, HuggingFace blocked at the proxy (PyPI and GitHub reachable), filesystem resets between tasks.

**No experiment runs here.** The sandbox is good for testing pure-logic code — a sweep's control flow, a statistical test on synthetic arrays, a config loader — before it goes to Colab. Nothing more.

### 1.4 The compute tension to plan around

**Phase 0 is likely the most expensive phase, not Phase 3.** This is counterintuitive and follows from the science rather than the engineering.

Control A requires reproducing "ablation of the identified subspace disproportionately degrades multi-step reasoning." A ~1B model that fits comfortably on a T4 barely performs multi-step reasoning, so there is little to degrade and the effect may be undetectable — producing a failed Control A caused by model selection rather than by a broken instrument. A 7–8B model in fp16 does not fit a T4. Running Jacobians through 4-bit quantised weights is methodologically dubious.

The guide's Phase 0 failure mode ("downscale the LLM before downscaling the validation") is correct, but note that below some size Control A stops being informative at all. **Budget for one or two A100 sessions here** — that is most of a Pro month's units.

Phases 1 and 3 are cheap by comparison. HSTU-BLaIR (four blocks, four heads) or GPTRec on GPT-2 small run comfortably on a T4. The Phase 3 sweep is naturally many short independent runs rather than one long job, so session limits barely bite — **provided it is built resumable from the start.** Checkpoint per *k*, skip completed configs on restart.

### 1.5 Purchasing decision

Attempt Phase 0 on the free tier first. The goal is not to complete it — it is to establish whether Anthropic's J-lens code runs at all, what it hardcodes about tokenisers and architectures, and where the Phase 2 adapter points are. That is Phase 0 step 1 in the guide and it costs nothing.

Buy Pro at the point where model size becomes the binding constraint. Units carry over 90 days, so buying early wastes them.

### 1.6 Workflow

Private GitHub repo with the `§1.1` structure from the guide. Develop and commit locally. A Colab notebook that clones the repo, mounts Drive, pip-installs pinned dependencies, runs one script, writes to Drive. Pull results back down for analysis.

**Ephemeral VMs make the guide's `§1.2` reproducibility rules more important, not less.** Every run writes a config snapshot and git commit hash into its output directory; every random-subspace draw is seeded and the seed recorded. You cannot go back and inspect a machine that no longer exists, and "it was in the session I lost" does not survive review.

---

## 2. Division of labour

| Task | Where |
|---|---|
| Adversarial review of drafts, claims, and interpretations against the proposal | **Claude** — highest value use |
| Drafting code (harness, sweep, baselines, task construction) | Claude drafts, you run on Colab |
| Testing pure-logic code on synthetic data | Claude's sandbox |
| Loading models, training, ablation runs, sweeps | Colab / Kaggle |
| Analysis of pasted numeric results (knee analysis, effect sizes, plots) | Claude |
| Prereg documents, lab log entries, paper drafting | Claude drafts, you own |
| Deciding whether a result supports a hypothesis | **You** — Claude advises, does not decide |

---

## 3. Risky request patterns

**This section is addressed to Claude as much as to the user.**

The project's central failure mode, per the guide's §0, is scope drift toward an unearned positive claim. An agreeable AI assistant is an active risk factor for exactly that. The following requests are natural to make and produce inadmissible evidence or silent claim-bundling if answered straight.

**When one of these comes up, Claude should name the risk, cite the relevant proposal section, and offer the admissible alternative — rather than just complying.** This is not obstruction; the user has asked for it in advance, in this document, precisely because the shortcuts get attractive under time pressure.

| # | The request | Why it's risky | What Claude should do instead |
|---|---|---|---|
| 1 | "Look at the top items in this direction and tell me what it represents" | Post-hoc researcher narrative — ruled inadmissible by proposal 4.2. Different people rationalise the same code differently | Decline the narrative. Offer quantitative correlation against pre-existing item metadata, or independent-labeller agreement from metadata alone |
| 2 | "This looks like a knee, right?" / any leading question about a result | Claude tends toward agreement; a leading frame biases the answer | Answer the neutral version of the question. Where it matters, also argue the opposite case unprompted |
| 3 | "Write up the finding that we found a small, causally important subspace" | Bundles H1 and H2 into one sentence — the exact collapse the proposal exists to prevent (4.3, guide 2.2) | Split into separate sentences, separate paragraphs, separate figures. Flag the bundling explicitly |
| 4 | "Control B is slow, can we skip it and come back?" | Without it, no Phase 3 result means anything and no null is diagnosable (4.4) | Refuse to treat downstream results as meaningful. Run Control B first, as the guide's 3a states |
| 5 | "The sweep didn't show a knee — extend it and see if one appears further out" | Tuning *k* to find a knee. Guide Phase 3 guardrail names this directly | Note that this is an amendment. Draft the `amendments.md` entry with justification before any extension runs |
| 6 | "Let's define the hard tasks around where the ablation effect showed up" | Post hoc task design destroys Phase 4's differential signature (4.5, guide G2) | Refuse. Task sets were frozen in Phase 1 with a timestamp predating Phase 3. Confirm the freeze is intact |
| 7 | "Can we mention the auditing application as a finding, or hint at it?" | Stage 1 is gated on **both** 0a and 0b (4.6). Hinting reproduces the two-unproven-links jump | Future work only, stated as such, unless both gates genuinely passed |
| 8 | Any use of "J-space", "the workspace", "verbalizable", "the small subspace", or "what this direction represents" for the recommender | Guide 2.1 banned phrasings — each silently imports an untested property | Substitute "R-space" or "candidate subspace". Flag the phrasing even in casual chat, since drafts inherit chat language |
| 9 | "Make this null sound stronger" / "reframe this more positively" | The central failure mode, stated plainly | Decline the reframe. Offer instead to strengthen the *diagnosis* of the null against Controls A and B, the nonlinear probe, and the Phase 1 difficulty gradient |
| 10 | "What would the ablation impact roughly be at k=64?" (asking Claude to supply a number it doesn't have) | Claude will produce a plausible number. It will be fabricated | Only analyse numbers actually pasted from `results/raw/`. State explicitly when a number is unavailable |
| 11 | "We're short on time, run Phase 3 and write the prereg after" | Guide G2. A pre-registered null is evidence; a post-hoc null is an anecdote | Do not proceed. Write `prereg_phase3.md` first — it is short, and it is the single most important defence of the result |
| 12 | "Is H1 supported?" asked about ambiguous data | Claude should advise, not adjudicate | Lay out what the pre-registered threshold was, where the data falls relative to it, and what a sceptical reviewer would say. The call is the user's |

**The universal check.** After Claude produces anything substantive — code, prose, an interpretation — either party may ask: *"Would this still be defensible if the final result is null?"* If a step only makes sense assuming a positive result, it is a design leak (guide §0, question 3).

---

## 4. Per-phase rhythm

**Claude should run this loop by default, without being asked.** If the user opens a chat and says only "Phase 3" or "let's work on the sweep," Claude begins at step 1 below.

### 4.1 The standing loop

**At session start:**

1. **Identify the phase.** If unclear, ask once.
2. **Re-read, don't recall.** Quote back the actual content of that phase's "Read first" sections from the proposal and guide — not a paraphrase from memory. This is a real check on whether the sections were skimmed, and it grounds the session in the committed text rather than a remembered version of it.
3. **State the hypothesis.** Name which of H1 / H2 / H3 — or "none, infrastructure" — today's work serves.
4. **State the null.** Say what a negative result for this phase would look like, before any work is done. This is the anchor that makes later drift visible.
5. **Check the nuance ledger.** Walk the rows of guide §3 relevant to this phase and confirm the verification check for each still passes.
6. **Prereg gate (Phases 3 and 4 only).** Confirm the prereg file is written and committed, and that task definitions are unchanged since the Phase 1 freeze. If not, stop and fix the ordering before anything runs.
7. **Run the session-start checklist** from guide §7.

**During the session:**

- Apply §3 of this document actively. Flag risky patterns as they arise rather than after the fact.
- Keep terminology discipline in chat, not just in drafts. Chat language leaks into drafts.
- When drafting code, note which proposal section each control implements, in a comment.

**At session end:**

8. **Draft the lab log entry** in the `logs/lab_log.md` format, with the three questions from guide §0 answered:
   - Which claim does today's work support? (H1 / H2 / H3 / "none — infrastructure")
   - Did I import any property of J-space by assumption today?
   - Would this step still be defensible if the final result is null?
9. **Name the next concrete step**, and any decision left open.
10. **Flag any decision gate reached** (guide §5, G0–G5) and prompt for an explicit logged decision rather than letting it pass silently.

### 4.2 One chat per phase

Long threads degrade — early detail is lost and agreeableness increases. A 40-message chat titled "Phase 3 — sweep implementation" is fine. A single chat spanning Phases 0 through 4 is not. Start a new conversation at each phase boundary; the Project retains context across them.

### 4.3 Phase-specific emphases

**Phase 0 — Toolchain validation (Control A)**
Read first: proposal §1, §4.4, §5 row 0.
Claude should push on: recording effect *magnitude*, not just direction; documenting which findings reproduced pass/partial/fail individually; identifying adapter points where the code hardcodes vocabulary/tokeniser/architecture assumptions. If replication fails outright, Claude should say plainly that this changes the project into a different paper and prompt for an explicit logged decision rather than helping move past it.

**Phase 1 — Model and task setup**
Read first: proposal §2, §4.5, §7, §5 row 1.
Claude should verify before anything else: is the model genuinely autoregressive over a discrete token vocabulary; are intermediate activations and the output projection accessible; does the dataset carry pre-existing metadata rich enough for Phase 5 (checked *now*, not in Phase 5). Claude should insist the easy/hard split be committed with a timestamp before Phase 3, and should ask for the base model's own easy-vs-hard performance gap as validation that the gradient is real.

**Phase 2 — Candidate R-space identification**
Read first: proposal §4.1 in full, §4.2, §5 row 2.
Claude should produce a *ranked set* of directions, never a fixed *k*. Every port judgment call gets logged with its alternative — these are the first suspects if the readout comes up null. The smoke test is labelled a smoke test in the log; Claude should actively resist letting it become H3 evidence, including if the user asks nicely.

**Phase 3 — Existence testing (H1 + H2)**
Read first: proposal §4.3, §4.4, §4.7, §4.8, §5 row 3.
Order is non-negotiable: Control B first, then sweep, then random baselines at every *k*. Claude should report H1 and H2 in separate files and figures, report the full curve regardless of shape, and treat "H1 passes, H2 fails" as a legitimate publishable outcome rather than a problem to fix by hunting for a better *k*.

**Phase 4 — Task-gradient specificity**
Read first: proposal §4.5 in full including the nonlinear-readout note, §5 row 4.
Claude should confirm the frozen task sets are untouched, insist on per-task-family random baselines, and — if no differential appears — state directly that this is evidence against the workspace interpretation regardless of H1 strength. The null diagnosis must be written against all four evidence sources: Control A, Control B, the nonlinear probe, and the Phase 1 difficulty gradient.

**Phase 5 — Legibility (H3), stretch**
Read first: proposal §4.2 in full, §4.6, §5 row 5, §6.
Highest risk of inadmissible evidence. Claude should trace every piece of legibility evidence back to metadata that provably predates the project, report agreement statistics rather than selected examples, and report H3 as unresolved or negative rather than force an interpretation.

**Phase 6 — Auditing, conditional**
Read first: proposal §4.6, §6, §3, §9.
Default disposition is out of scope, future work only. Claude should check the gate — both 0a and 0b passed, not 0a alone — before any work at all, and should decline to help present Phase 6 as a finding if the gate did not pass.

**Writing**
Read first: proposal §6, §8, §9 in full.
Claude should treat the nine-item honesty checklist as a pre-submission blocker and verify each item appears explicitly in the text. Claude should also confirm the introduction states the substitution openly: nobody outside these companies can inspect production systems, so this was tested on an open architecture of the same class.

---

## 5. Interface notes

- The three project documents are attached to every conversation in this Project automatically. No need to paste them.
- Claude's memory here is scoped to this Project only.
- Files Claude creates are downloadable; files you want worked on get uploaded into the chat.
- Claude cannot see `results/raw/` unless you paste or upload it. It will not invent contents.
