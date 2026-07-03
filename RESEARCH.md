# In-Band Signal Compliance — Research Foundation

The honesty ledger for IBSC. This is a **position + benchmark-design** repository with a v0
scaffold: a deterministic **MockProvider** and an offline reference run
(`scripts/run_microbench.py`). It is **not** a completed empirical study. This file lists the
load-bearing claims, marks which are verified vs. still-to-be-measured, and explicitly lists
claims we do **not** yet make. Prior-art verification lives in
[docs/PRIOR-WORK.md](docs/PRIOR-WORK.md).

Author: Thamilvendhan Munirathinam (solo independent researcher, github.com/mthamil107).

## Thesis (the load-bearing claim)

> LLM agents systematically respond **incorrectly** to *in-band control signals* — instructions
> that arrive through the input channel from the **environment** (orchestrator / resource /
> retrieved content / system), not the user. The two failure modes are symmetric:
> **under-compliance** (ignoring a legitimate signal) and **over-compliance** (obeying an
> illegitimate one). They are the same phenomenon from opposite ends, measurable by one metric —
> "did the agent respond correctly to an environment-originated instruction, given its
> legitimacy?" — on one leaderboard (`signalbench`).

**Status of the thesis:** the *framing/unification* is a design contribution (this repo). The
*empirical claim* that agents fail "systematically" across all five families is **not yet measured
in this repo** — it is motivated by the prior-art below, each of which established one failure mode
in isolation. See "Claims NOT yet supported."

---

## Claim ledger

### C1 — Prompt injection / indirect prompt injection is a real, unsolved over-compliance failure. VERIFIED (external).
- AgentDojo: 7000+ security cases; injection succeeds at meaningful rates. arXiv:2406.13352.
- InjecAgent: 1,054 cases; ReAct GPT-4 falls for indirect prompt injection **~24%** of the time.
  arXiv:2403.02691.
- Scope note: rates are model- and harness-specific; cite the exact system when quoting a number.

### C2 — Temporal under-compliance ("temporal blindness") is real. VERIFIED (external), with a term caveat.
- "Your LLM Agents are Temporally Blind" documents agents ignoring elapsed real-world time.
  arXiv:2510.23853.
- **Caveat:** that work is about *perceiving elapsed time*, not about ignoring an explicitly
  *injected* date. IBSC's `time` family narrows this to injected-date uptake, a distinct,
  cleanly-measurable special case. **We do NOT claim to coin "temporal blindness."**
- Sibling repo GroundClock / NowBench (D:/Repo/LLM-Time-Memory, paper in preparation) is the
  temporal-uptake foundation IBSC's `time` family mirrors.

### C3 — In-band access-deny signals can drive recusal (the under-compliance seed). VERIFIED (author's own).
- Recuse: cooperative in-band deny signal; live-host pilot showed **100% recusal when present vs
  100% completion without**. arXiv:2606.06460.
- **Scope:** a single signal type, one polarity, a small live pilot — not a benchmark. IBSC
  generalizes it; recusal is the first datapoint on the under-compliance axis.

### C4 — Memory governance (do-not-share / forgetting) is real and unsolved. VERIFIED (concurrent external).
- GateMem finds no method jointly achieves utility, access control, and reliable forgetting.
  arXiv:2606.18829. Cited as concurrent evidence for the memory-label under-compliance case.
- Sibling: memorywire (arXiv:2606.01138) is the propagation-label foundation the `memory_label`
  family mirrors.

### C5 — The Instruction Hierarchy covers only the resist/over-compliance half. VERIFIED (from the abstract).
- IH (arXiv:2404.13208) is a **training** intervention resolving **conflicts** by privilege rank.
  It does distinguish aligned vs. misaligned instructions and reports over-refusal checks, but only
  to preserve capability under conflict; it defines **no legitimate-signal-uptake correctness axis**
  and does not score whether an agent *adopts* a lone, non-conflicting environment signal. This is
  the biggest external overlap and is met head-on in PRIOR-WORK.md.

### C6 — "In-Band Signal Compliance" is unclaimed in the literature. VERIFIED.
- No ML/AI/security use found; the only adjacent phrasing ("In-Band Access-Deny Signals") is the
  author's own. A name is branding, not a contribution — we lead with the measurement/unification.

### C7 — The single metric (SRC / IBSC-Score) puts both poles on one leaderboard. VERIFIED (by construction).
- This is a design property of the metric (see docs/spec/v0.md §5–6), not an empirical result: an
  always-comply or always-resist policy maps to ~0.5 by the balanced macro-average. The offline
  demo demonstrates the mechanics with the mock provider; it says nothing about real models.

---

## Claims NOT yet supported (do NOT put in the paper as results)

- **"Agents systematically fail across all five families."** Not established at scale. A first
  **6-model run** exists (6 models, n = 75/model, single seed — see below): mean IBSC 0.772,
  range 0.650–0.850, and every model fails on both poles. This is directional evidence across
  two vendors, not a systematic multi-scale/multi-seed study. Frame as motivation + a first
  leaderboard, not a settled general finding.
- **"A model that under-complies on dates also under-complies on tool allowlists"**
  (cross-signal transfer/correlation). This is the "just a mashup" rebuttal and the sharpest
  possible result — but it is **future work**, unmeasured.
- **"Instruction-hierarchy-trained models over-suppress legitimate environment signals."** A
  *predicted* side effect; plausible and strategically important, but **not yet measured**. Do not
  state as fact.
- **A *definitive* IBSC-Score / LSU / ISR / FTR leaderboard for real systems.** A first 6-model
  run exists (`gemini-2.5-pro` 0.850, `gpt-4o-mini` 0.833, `gpt-5.5` 0.817, `gpt-5.1` 0.800,
  `gpt-4.1` 0.683, `gemini-2.5-flash` 0.650; mock oracle 1.0, one-sided mock policies 0.5 by
  design), but every quote MUST carry the n = 75/model, single-seed, single-run, two-vendor
  caveat. Do not present it as a definitive ranked evaluation of model quality.
- **"IBSC subsumes AgentDojo/InjecAgent/GateMem."** True as a *conceptual* framing (they are
  single-pole/single-vertical); we do NOT claim to reproduce or replace their measurements.

---

## What v0 actually demonstrates (honest scope)

- A precise, std-lib-only, LLM-judge-free spec and reference implementation of the data model,
  five self-contained offline families, the SRC metric, a runner, and a leaderboard.
- A deterministic offline demo (`scripts/run_microbench.py`, zero network / zero deps) that builds
  all families, runs `MockProvider('oracle')` and `MockProvider('always_comply')`, aggregates, and
  writes `results/mock_microbench.json` — showing that the metric separates an oracle from a
  trivial always-comply policy (the latter pinned near ~0.5).
- A taxonomy that unifies five prior single-pole/single-vertical benchmarks under one
  correctness-given-legitimacy axis.
- A **first real 6-model run** (`scripts/run_real.py`, function-calling-aware OpenAI + Gemini
  over live APIs, run 2026-07-03, n = 75/model = 5 families × 15 items, `seed=0`,
  `reasoning_effort`/thinking = low, `temperature=0` for non-reasoning models, **action-based
  grader**): all six models land strictly between the oracle (1.0) and the one-sided baseline
  (0.5) — `gemini-2.5-pro` 0.850, `gpt-4o-mini` 0.833, `gpt-5.5` 0.817, `gpt-5.1` 0.800,
  `gpt-4.1` 0.683, `gemini-2.5-flash` 0.650 (mean 0.772) — and every one fails on **both** poles
  (nonzero under- and over-compliance). The robust cross-vendor finding is that `memory_label` is
  the hardest family (mean 0.667): models leak do-not-share/expired values and obey injected
  "sharing-now-allowed" overrides. Capability is non-monotonic (`gpt-4o-mini` 0.833 > `gpt-5.1`
  0.800 > `gpt-4.1` 0.683). FTR = 0 for every model. Every failure is a logged action (34
  leaked-secret, 25 forbidden-tool-call, 17 ignored-recuse/withhold, 1 skipped-required-tool),
  plus 5 `gpt-5.5` items hard-blocked by OpenAI's API-layer cybersecurity filter (errors), not a
  phrasing miss. Directional at n = 75/model, single seed, one run, two vendors — not a
  definitive study.
- **Grading rigor (v0.1 → v0.2).** The original grader scored any text-substring miss as a
  failure, which *manufactured* over-compliance and false triggers (e.g. a model that withheld a
  secret but never said "refuse" was mislabeled over-compliant; early v0.1 FTRs of 0.20–0.40
  were almost entirely this artifact). v0.2 grades on the **action taken** (emitted secret value /
  forbidden tool call / adopted spoof); phrasing is never penalised. This corrected several v0.1
  headline numbers — do not cite v0.1 figures.

## Honesty rules for anything downstream (paper, README, posts)

1. Frame IBSC as a **position + benchmark-design** paper with an offline reference run, never as a
   completed empirical study.
2. A first real 6-model run now exists; quote its numbers only with the n = 75/model, single-seed,
   single-run, two-vendor caveat attached, and never as a definitive model ranking.
3. Cite the term as unclaimed but lead with the unification, not the name.
4. State model/sample scope whenever quoting an external failure rate (many are single-paper,
   single-model).
5. Position IBSC as the **generalization of the author's Recuse result**, not an unrelated claim.
6. Do not claim to coin "temporal blindness" or "in-band signaling."
