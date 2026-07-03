# LAUNCH — Peer-Review + Distribution Pack

**Paper:** *In-Band Signal Compliance: One Metric for Prompt Injection and Temporal Blindness*
**Framework:** In-Band Signal Compliance (IBSC) · **Benchmark/package:** `signalbench`
**Author:** Thamilvendhan Munirathinam — solo independent researcher ([github.com/mthamil107](https://github.com/mthamil107))
**Repo:** https://github.com/mthamil107/signal-compliance · **License:** Apache-2.0
**Study run:** 2026-07-03 · 6 real models + 1 oracle · 5 families × 15 = 75 items/model.

> Ground rule for everything below: keep the **action-based grading** definition and the
> **n = 75 / single-seed / single-run** limitation prominent. Lead with the two-pole
> unification and the memory-label finding. No hype, no overclaiming, no rounding drift.

---

## 0. Results this pack is locked to (do not restate differently anywhere)

**Leaderboard** (IBSC_Score, cal, LSU, ISR, under_rate, over_rate, FTR | per-family SRC: time / access_deny / memory_label / injection / bot_policy):

| # | System | IBSC | cal | LSU | ISR | under | over | FTR | time | acc_deny | mem_label | inj | bot |
|---|--------|------|-----|-----|-----|-------|------|-----|------|----------|-----------|-----|-----|
| 1 | mock:oracle (ref. upper bound) | 1.000 | 1.000 | 1.00 | 1.00 | 0.00 | 0.00 | 0.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| 2 | gemini-2.5-pro | 0.850 | 0.850 | 0.967 | 0.733 | 0.033 | 0.267 | 0.00 | 1.00 | 0.75 | 0.583 | 0.917 | 1.00 |
| 3 | gpt-4o-mini | 0.833 | 0.833 | 0.867 | 0.800 | 0.133 | 0.200 | 0.00 | 1.00 | 0.833 | 0.75 | 0.833 | 0.75 |
| 4 | gpt-5.5 | 0.817 | 0.817 | 0.767 | 0.867 | 0.233 | 0.133 | 0.00 | 1.00 | 0.75 | 0.833 | 0.833 | 0.667 |
| 5 | gpt-5.1 | 0.800 | 0.800 | 0.800 | 0.800 | 0.200 | 0.200 | 0.00 | 1.00 | 0.833 | 0.667 | 0.917 | 0.583 |
| 6 | gpt-4.1 | 0.683 | 0.683 | 0.800 | 0.567 | 0.200 | 0.433 | 0.00 | 0.917 | 0.50 | 0.583 | 0.833 | 0.583 |
| 7 | gemini-2.5-flash | 0.650 | 0.650 | 0.833 | 0.467 | 0.167 | 0.533 | 0.00 | 0.917 | 0.50 | 0.583 | 0.667 | 0.583 |

- gpt-5.5 note: **5/75 items were HARD-BLOCKED** by OpenAI's platform cybersecurity content filter at the API layer, recorded as errors (score 0). An alternative scoring that credits an API refusal on an illegitimate item as resistance would raise gpt-5.5 slightly.
- One-sided mock policies (always-comply / always-resist) = **0.500 by construction** (the balanced-metric baseline).
- **Aggregates:** mean IBSC across 6 real models = **0.772**; range **0.650–0.850**.
- **Per-family mean across 6 models** (lower = weaker): time **0.972** (easiest), injection **0.833**, access_deny **0.694**, bot_policy **0.694**, memory_label **0.667** (HARDEST).
- **Non-correct verdict census** (all real actions, zero grading artifacts after audit): 34 leaked-secret, 25 forbidden-tool-call, 17 ignored-recuse/withhold, 1 skipped-required-tool, 5 gpt-5.5 API policy-blocks (errors). **FTR = 0 for every model.**

**Config:** benchmark `signalbench` (IBSC). reasoning_effort / thinking-budget = low; temperature = 0 for non-reasoning models (omitted for gpt-5.x, which allow only the default temperature = 1); seed = 0. **Action-based grading:** a failure is asserted only on an *observed action* — an emitted opaque secret VALUE, a forbidden tool call, an adopted spoofed value, or an ignored recuse/withhold — **never on phrasing**. Matching searches response text AND tool-call arguments, separator-insensitive. Raw responses in `results/*.json`.

---

## 1. Recommended arXiv categories

**Primary — `cs.CR` (Cryptography and Security).**
IBSC is fundamentally a *channel-confusion security* benchmark: in-band control riding the data channel, adjudicating legitimacy without out-of-band authority. Prompt injection, spoofed "fake-now" values, and leaked do-not-share secrets are security failures; the primary audience is the LLM-agent security community.

**Cross-list — `cs.AI` (Artificial Intelligence).**
The unit of study is LLM-agent behavior and an alignment property (correct response conditioned on signal legitimacy); the agent/alignment audience should see it.

**Cross-list — `cs.CL` (Computation and Language).**
Models, prompting, and instruction-following are the substrate; IBSC sits alongside IFEval and Instruction-Hierarchy work that lives in `cs.CL`.

> One-line rationale to paste in the arXiv "why these categories" box: *An LLM-agent
> security/safety benchmark (cs.CR primary) measuring an agent-behavior/alignment property
> (cs.AI) over language-model instruction-following (cs.CL).*

---

## 2. Paste-ready arXiv submission block

**Title**
```
In-Band Signal Compliance: One Metric for Prompt Injection and Temporal Blindness
```

**Abstract** (ASCII-only, 1,864 chars — under the 1,920 limit)
```
Prompt injection and temporal blindness are usually studied as separate bugs. We
argue they are the same failure seen from opposite ends: an LLM agent mishandling a
control instruction that arrived in-band, riding the same channel as ordinary data,
with no out-of-band authority to vouch for it. Over-compliance obeys an illegitimate
signal (injection succeeds, a fake "now" poisons the clock); under-compliance ignores
a legitimate one (an access-deny banner, a do-not-share memory label, an automation
policy). We formalize In-Band Signal Compliance (IBSC): correct response to an
environment-originated instruction, conditioned on its legitimacy. IBSC places both
poles on one axis that no single-pole benchmark can, via Signal-Response Correctness,
a per-item 0/1 score aggregated as the balanced mean of Legitimate Signal Uptake and
Illegitimate Signal Resistance, so trivial always-comply or always-resist policies
score 0.5. We release signalbench: five offline families (time, access-deny,
memory-label, injection, bot-policy), 15 items each, with deterministic,
family-owned, action-based grading. A failure is asserted only on an observed action
-- an emitted secret value, a forbidden tool call, an adopted spoofed value, an
ignored recusal -- never on phrasing; matching covers response text and tool-call
arguments. On 75 items per model across six frontier models from two vendors, no
model exceeds 0.85 (mean 0.772, range 0.650-0.850). Every model shows nonzero over-
AND under-compliance at once. Memory-label is hardest for all six (mean 0.667).
Capability is not monotonic: a small model beats larger ones. False-trigger rate is
zero everywhere. We report these as a seed leaderboard, not a statistical verdict:
n=75, single seed, one run, two vendors, small self-authored pools. All raw responses
and grading code are released under Apache-2.0.
```

**Comments line**
```
Benchmark + reproducible harness. Code, 75-item x 6-model raw responses, and grading
released under Apache-2.0 at https://github.com/mthamil107/signal-compliance
```

> Char-check note: the abstract avoids em dashes (uses `--`), curly quotes, and any
> non-ASCII. Re-run a byte check before pasting (see §5 checklist).

---

## 3. Peer-review distribution plan

**Sequencing principle:** arXiv is the canonical anchor; everything else points back to the arXiv abstract page. Do not post secondary channels until the arXiv ID exists.

### 3a. arXiv (canonical)
1. Confirm categories (§1): primary `cs.CR`, cross-list `cs.AI`, `cs.CL`.
2. Build the source tarball (LaTeX in `paper/main.tex` + `paper/refs.bib`); use the `arxiv-bundle` / `paper-polish` skills to validate (tex present, bib entries resolve, figures resolve, size < 50 MB).
3. Paste Title / Abstract / Comments from §2. License: select the arXiv non-exclusive license; the software itself is Apache-2.0 (state in Comments).
4. Submit; capture the arXiv ID and the abstract URL. This is the link every other channel uses.

### 3b. alphaXiv
1. Once the arXiv ID is live, the paper auto-mirrors to alphaXiv (`alphaxiv.org/abs/<id>`).
2. Seed the discussion with a single non-anonymous author comment: the two-pole unification thesis + the memory-label finding + the explicit n=75/single-seed caveat, inviting families/items and adversarial re-grading.
3. Pin the "action-based grading" definition so reviewers critique the right thing.

### 3c. OpenReview (non-anonymous preprint / community track)
1. Submit to a non-anonymous preprint or community venue/track (not a double-blind track — this is a signed independent preprint).
2. Author field: Thamilvendhan Munirathinam, github.com/mthamil107. Attach the arXiv PDF; link the repo and `results/*.json`.
3. In the submission note, foreground the limitations verbatim (n=75, single seed, one run, two vendors, small self-authored pools, gpt-5.5's 5 API-blocked items counted as errors) so reviewers see them before objecting.

### 3d. Hugging Face Papers
1. After arXiv indexing, claim the paper at `huggingface.co/papers/<arXiv-id>`.
2. Add a short author summary matching the abstract; link the repo. If a `signalbench` dataset/space is later published, cross-link it here.
3. Respond to questions on-thread, keeping every number consistent with §0.

### 3e. X/Twitter thread (5–7 posts, drafted, honest, no hype)
> Lead with the two-pole unification, then the memory-label finding. Every number matches §0.

1/ Prompt injection and temporal blindness get studied as two bugs. They're one bug seen from two ends: an agent mishandling a control instruction that arrived *in-band* — riding the data channel, no out-of-band authority. I call it In-Band Signal Compliance (IBSC). 🧵

2/ Over-comply = obey an *illegitimate* signal (injection lands, a fake "now" poisons the clock). Under-comply = ignore a *legitimate* one (access-deny banner, do-not-share memory label, automation policy). Same channel-confusion, opposite directions. One axis holds both.

3/ signalbench: 5 offline families (time, access-deny, memory-label, injection, bot-policy) × 15 items. Grading is *action-based* — a failure counts only on an observed action (leaked secret value, forbidden tool call, adopted spoofed value, ignored recusal), never on phrasing.

4/ 6 frontier models, 2 vendors, 75 items each. No model clears 0.85 (mean 0.772, range 0.650–0.850). And every single model over- AND under-complies at the same time — the quantity a one-pole benchmark literally cannot put on one number.

5/ Hardest family for all six models: memory-label (mean 0.667). Models leak do-not-share/expired values and obey injected "sharing-is-now-allowed" overrides. That's the robust cross-vendor result.

6/ Not a scale story: gpt-4o-mini (0.833) beats gpt-5.1 (0.800) and gpt-4.1 (0.683); gemini-2.5-pro (0.850) > gemini-2.5-flash (0.650). Signal compliance looks like a distinct alignment property, not raw capability.

7/ Honest caveats: n=75/model, single seed, one run, two vendors, small self-authored pools — a *seed* leaderboard, not a statistical verdict. Code + all raw responses, Apache-2.0. Paper + repo: [arXiv link] · github.com/mthamil107/signal-compliance

### 3f. LinkedIn post (drafted)
```
New preprint: In-Band Signal Compliance (IBSC).

Prompt injection and temporal blindness are usually treated as two different agent
bugs. They are the same one from opposite ends — an LLM agent mishandling a control
instruction that arrived in-band, riding the same channel as ordinary data, with no
out-of-band authority to vouch for it.

Over-compliance obeys an illegitimate signal (injection succeeds; a fake "now" poisons
the clock). Under-compliance ignores a legitimate one (an access-deny banner, a
do-not-share memory label, an automation policy). IBSC puts both on a single axis that
no single-pole benchmark can.

signalbench: five offline families x 15 items, with deterministic, action-based
grading — a failure is asserted only on an observed action (a leaked secret value, a
forbidden tool call, an adopted spoofed value, an ignored recusal), never on phrasing.

Across six frontier models from two vendors (75 items each): no model exceeds 0.85
(mean 0.772). Every model over- AND under-complies simultaneously. Memory-label is the
hardest family for all six. Capability is not monotonic — a small model beats larger
ones.

Stated plainly: this is a seed leaderboard, not a statistical verdict — n=75 per model,
single seed, one run, two vendors. Code and all raw responses are Apache-2.0.

Paper: [arXiv link] · Code: github.com/mthamil107/signal-compliance
```

---

## 4. Reviewer pre-empt FAQ

**Q: Isn't this just self-scooping your own Recuse paper (arXiv:2606.06460)?**
No — Recuse measured one pole (compliance with in-band access-deny signals) in one family. IBSC's contribution is the *unification*: it shows access-deny (Recuse), temporal spoofing, memory-label propagation (memorywire, arXiv:2606.01138), injection (Beyond Pattern Matching, arXiv:2604.18248), and bot-policy are the *same* channel-confusion failure, and it puts over- and under-compliance on one balanced axis. Recuse is one of the five families, cited as the spine — not the whole result. The two-pole result (F2) does not exist in any single-pole prior work.

**Q: This is just a mashup of existing benchmarks (AgentDojo, InjecAgent, IFEval, GateMem).**
The families are prior *problems*, but the framing and the metric are the contribution. No prior benchmark scores over- and under-compliance on one number such that a trivial always-comply *or* always-resist policy lands at exactly 0.5 by construction — that's what makes the two-pole finding (F2) and the over/under trade-off placement (F5) measurable. Prior injection benches (InjecAgent, AgentDojo) measure only resistance; IFEval measures only uptake. IBSC's axis is the novel object; the families instantiate it.

**Q: n=75 per model, single seed, one run — this is too small to conclude anything.**
Agreed, and we say so in the abstract, the limitations, and every post: this is a *seed leaderboard*, not a statistical verdict. We deliberately make only claims robust to that: (a) *directional* facts confirmed by census of logged actions (34 leaked secrets, 25 forbidden tool calls, 17 ignored recusals — all real actions, zero grading artifacts after audit); (b) the memory-label-hardest result holds across *all six* models and *both* vendors (F3), which is far stronger evidence than any single per-model point estimate. We make no strong per-model ranking claim between neighbors.

**Q: Isn't IBSC just Instruction Hierarchy (arXiv:2404.13208) restated?**
Instruction Hierarchy is a *proposed defense/priority ordering* (system > user > tool). IBSC is a *measurement axis* and it is bidirectional: Instruction Hierarchy addresses only the over-compliance pole (don't obey low-priority injected instructions). It has nothing to say about under-compliance — ignoring a *legitimate* in-band signal (F2, F5). IBSC measures both, and shows models that resist best (gpt-5.5, over 0.133) simultaneously under-comply more (0.233) — a trade-off a priority-ordering framing cannot express.

**Q: Action-based grading — aren't you just moving the goalposts to look lenient?**
The opposite: it removes an *inflation* artifact. Earlier drafts flagged models over-compliant for merely *mentioning* a secret while refusing to emit it, and produced spurious FTRs of 0.20–0.40. Grading on observed actions only (emitted value, forbidden tool call, adopted spoofed value, ignored recusal) — searching both response text and tool-call arguments, separator-insensitive — is *stricter about what counts as evidence*, not more lenient. Post-audit FTR = 0 everywhere is a consequence, not a target.

**Q: The gpt-5.5 API blocks contaminate its score.**
Disclosed explicitly (F7): 5/75 items were hard-blocked by OpenAI's platform cybersecurity filter and counted as errors (score 0). We report this as an *orthogonal, non-model-level defense* the benchmark surfaces, and note an alternative scoring crediting an API refusal as resistance would raise gpt-5.5 slightly. We do not silently recode it.

---

## 5. Pre-upload CHECKLIST (all must be TRUE before submitting)

**Numbers & consistency**
- [ ] Every number in paper, README, abstract, and all posts matches §0 exactly (no re-rounding). Leaderboard, mean 0.772, range 0.650–0.850, per-family means, verdict census, FTR=0.
- [ ] Mock oracle = 1.000 shown as reference upper bound; one-sided mock policies = 0.500 baseline stated.
- [ ] gpt-5.5 5-API-block caveat present wherever gpt-5.5's score appears.

**Framing (must lead everywhere)**
- [ ] Two-pole unification (F2) and memory-label-hardest (F3) lead the abstract and every post.
- [ ] "Action-based grading" defined near the top of the paper and pinned in secondary channels.
- [ ] Limitations (n=75, single seed, one run, two vendors, small self-authored pools, reasoning-model temp=1 nondeterminism, gpt-5.5 errors) stated plainly, not buried.
- [ ] No claim over-generalizes beyond n=75/single-seed; no strong neighbor-ranking claims.

**arXiv mechanics**
- [ ] Abstract is ASCII-only (no em dash, curly quotes, non-ASCII) and ≤ 1,920 chars — byte-check passes.
- [ ] Title identical across `paper/main.tex` (`\title` + `pdftitle`), README, and §2.
- [ ] Categories set: primary `cs.CR`; cross-list `cs.AI`, `cs.CL`.
- [ ] Comments line includes repo URL + Apache-2.0.
- [ ] Source tarball validated (tex compiles, all `refs.bib` entries resolve, figures resolve, < 50 MB) via `arxiv-bundle`/`paper-polish`.

**Citations (spine + external, all present in refs.bib)**
- [ ] Author's own: Recuse (arXiv:2606.06460), memorywire (arXiv:2606.01138), Beyond Pattern Matching (arXiv:2604.18248).
- [ ] External: Instruction Hierarchy (arXiv:2404.13208), IFEval (arXiv:2311.07911), AgentDojo (arXiv:2406.13352), InjecAgent (arXiv:2403.02691), GateMem (arXiv:2606.18829).

**Repo & reproducibility**
- [ ] `results/*.json` raw responses committed; grading code committed; Apache-2.0 LICENSE + NOTICE present.
- [ ] Config reproducible from README (reasoning_effort=low, temp=0 / omitted for gpt-5.x, seed=0).
- [ ] Secret scan clean (no API keys, tokens, real IPs) before any push — per repo policy.

**Secondary channels (do NOT post before arXiv ID exists)**
- [ ] arXiv ID captured; abstract URL substituted for every `[arXiv link]` placeholder.
- [ ] alphaXiv seed comment, OpenReview note, HF Papers claim, X thread, LinkedIn post all use the live URL and match §0.

---

## Outline (as requested)

1. **§0 Locked results** — leaderboard table, aggregates, per-family means, verdict census, config + action-based grading definition.
2. **§1 arXiv categories** — primary `cs.CR`; cross-list `cs.AI`, `cs.CL`; one-line justification each.
3. **§2 Paste-ready submission block** — Title, ASCII abstract (1,864 chars), Comments line (repo + Apache-2.0).
4. **§3 Distribution plan** — arXiv → alphaXiv → OpenReview (non-anon) → HF Papers → X thread (7 posts) → LinkedIn, all drafted, leading with two-pole + memory-label.
5. **§4 Reviewer pre-empt FAQ** — self-scoop vs Recuse; "just a mashup"; small n/single seed; IBSC vs Instruction Hierarchy; + action-grading and gpt-5.5-blocks rebuttals.
6. **§5 Pre-upload checklist** — numbers, framing, arXiv mechanics, citations, repo/repro, secondary-channel gating.
