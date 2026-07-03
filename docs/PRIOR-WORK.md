# Prior Work & Naming Rationale

**Framework:** In-Band Signal Compliance (IBSC) · **Benchmark / package / CLI:** `signalbench`

This document does two things: (1) explains why the term **In-Band Signal Compliance** is worth
owning, and (2) states, honestly and defensibly, how IBSC differs from every closely related
work — including the biggest overlap risks. All differentiations here are meant to survive
review. For the empirical honesty ledger (what is verified vs. still-to-be-measured), see
[../RESEARCH.md](../RESEARCH.md).

---

## 1. Naming rationale

### Canonical gloss (reprint verbatim)
> IBSC = the correct response to an environment-originated instruction, conditioned on its
> legitimacy.

### Why the name is load-bearing
- **It coins a category, not a paper.** The field has no existing handle for "did the agent
  respond correctly to an instruction that came through the input channel from the environment,
  given that instruction's legitimacy?" You cite IBSC the way you cite "prompt injection" or
  "sycophancy."
- **"In-band" is borrowed on purpose** from a 50-year telecom/security lineage (in-band vs.
  out-of-band signaling; the 2600 Hz / Captain-Crunch in-band-signaling attack where control
  tones rode the same channel as voice). That heritage does the argument for free: mixing control
  and data on one channel is a known-dangerous pattern, so obeying an illegitimate in-band signal
  (prompt injection) and ignoring a legitimate one (temporal blindness, access-deny, do-not-share,
  tool-allowlist) are visibly the *same* channel-confusion bug from opposite ends.
- **"Compliance" is bidirectional** — comply when legitimate, refuse when not — which is exactly
  the unification nobody has named.
- **It survives being wrong about any single failure mode.** Injection benchmarks age out as
  models patch; temporal-blindness demos are one-offs. IBSC outlives both because it owns the
  *union*, the *single metric*, and the *single leaderboard* (`signalbench`).

### Acronym hygiene
IBSC is a clean 4-letter initialism, pronounced letter-by-letter. It collides with unrelated
real-world entities (International Bomber Command Centre; various banks / business schools) but
**none in ML/AI/security**, so there is no field collision. Rules we follow:
1. Always spell out "In-Band Signal Compliance (IBSC)" on first use; never ship the bare acronym
   in a title or abstract.
2. Bind the acronym to its three artifacts every time — framework **IBSC**, benchmark/package
   **signalbench**, CLI **signalbench**.
3. Let the distinctive, un-collided **signalbench** carry pip/SEO discoverability; let **IBSC**
   carry the conceptual/citation load.
4. No cute backronym — the phrase is already self-descriptive.

### Term availability
Verified: **"In-Band Signal Compliance" appears unclaimed in the ML/AI/security literature.** The
only adjacent existing phrasing is "In-Band Access-Deny Signals," which is the author's own prior
work (arXiv:2606.06460). A name alone is not a contribution; we lead with the
measurement/unification result and treat the term as branding, not the claim.

### Alternatives considered (and why IBSC won)
| candidate | pro | why rejected |
|---|---|---|
| Environment Instruction Fidelity (EIF) | plain, no telecom background needed; "fidelity" reads bidirectional | loses the in-band/out-of-band lineage that makes the unification feel inevitable; "fidelity" is overloaded in ML; weak, collided acronym |
| Channel-Confusion Robustness (CCR) | names the root cause; resonates with security | "robustness" biases toward the adversarial pole and buries the legitimate-uptake half — the novel part; jargon-heavy |
| Signal Legitimacy Compliance (SLC) | foregrounds legitimacy; adjacent to "signalbench" | drops "in-band" (the channel-provenance insight); "legitimacy compliance" is clunky; bland collided acronym |

---

## 2. Prior-art differentiation (verified)

### 2.1 The Instruction Hierarchy (Wallace et al., OpenAI, 2024) — biggest external overlap
**arXiv:2404.13208.** Argues prompt injection stems from LLMs treating system prompts and
untrusted user/third-party text as equal priority, and proposes a **trained** instruction
hierarchy (system > user > tool/environment) that resolves **conflicts** between privilege levels
by teaching models to ignore misaligned lower-privilege instructions.

**How IBSC differs (met head-on):**
- IH is a **training intervention** that resolves **conflicts** by rank. IBSC is a
  **measurement framework** (benchmark + metric) for whether an agent responds correctly to a
  **lone** environment-originated instruction when **no conflict is present**.
- IH is centered on the **over-compliance half** (resist wrongly-ranked / misaligned instructions).
  It does have an *aligned vs. misaligned* distinction and reports **over-refusal** checks (so that
  legitimate lower-privilege instructions are still followed) — but those exist to *preserve
  capability under conflict*, framed by privilege rank. IH defines no **legitimate-signal uptake**
  correctness axis: it does not score whether an agent *adopts* a lone, non-conflicting,
  environment-originated signal it should take up (injected date, access-deny, do-not-share label,
  tool allowlist), which is the **under-compliance** half IBSC measures.
- IBSC's contribution is the **unification**: legitimate-signal uptake and adversarial-signal
  resistance are the same axis (correct response given legitimacy) on one leaderboard. IH treats
  resistance as the whole problem; IBSC shows resistance is one pole of a symmetric spectrum.
- IBSC can even be read as the evaluation that reveals IH-trained models now **over-suppress**
  legitimate environment signals — a predicted, novel side-effect finding (not yet measured; see
  RESEARCH.md).

Follow-on IH work (Reasoning Up the Instruction Ladder, arXiv:2511.04694; Where Instruction
Hierarchy Breaks, arXiv:2606.07808; Many-Tier Instruction Hierarchy, arXiv:2604.09443) all stay
within the conflict-resolution-by-privilege paradigm and the over-compliance framing. None
measure lone-signal uptake or unify the two poles under one metric. Their momentum is exactly why
IBSC must plant the flag on the unification and the name.

### 2.2 IFEval (Zhou et al., 2023)
**arXiv:2311.07911.** ~500 prompts with 25 programmatically verifiable constraints (word counts,
formatting, keywords) issued by the **user**; strict/loose accuracy, no LLM judge.

**How IBSC differs:** IFEval measures following an explicit **user** instruction (trusted,
single-source, always legitimate). It has no legitimacy axis and no adversarial pole — it cannot
express over-compliance as a failure. IBSC measures **environment**-channel instructions and asks
"did it comply *given legitimacy*," scoring non-compliance as CORRECT for illegitimate signals.
IBSC borrows IFEval's programmatic-verifiability idea and applies it to environment signals with a
legitimacy label.

### 2.3 AgentDojo (Debenedetti et al., 2024)
**arXiv:2406.13352, NeurIPS D&B 2024.** Dynamic tool-use environment (workspace, Slack, travel,
banking), 97 tasks + 7000+ security cases, measuring indirect prompt-injection attack success and
task utility.

**How IBSC differs:** AgentDojo measures only the **adversarial pole** — resistance to
illegitimate injected instructions (over-compliance). It has no notion of a **legitimate**
environment signal the agent should obey; ignoring injected content is always right there. IBSC
generalizes the channel insight to both polarities: the same delivery mechanism can be legitimate
OR illegitimate, and the single metric is correctness-given-legitimacy. AgentDojo is effectively
the over-compliance sub-benchmark of IBSC's unified axis.

### 2.4 InjecAgent (Zhan et al., 2024)
**arXiv:2403.02691, Findings of ACL 2024; code: uiuc-kang-lab/InjecAgent.** 1,054 test cases over
17 user tools and 62 attacker tools; direct-harm vs. data-exfiltration intents; ReAct GPT-4 falls
for IPI ~24% of the time.

**How IBSC differs:** A static IPI vulnerability benchmark scoring **only** adversarial
over-compliance (attack success rate). No legitimate-signal axis, no reward for correct uptake.
IBSC subsumes InjecAgent's measurement as one endpoint and reframes "attack success" as
"over-compliance to an illegitimate in-band signal" — on the same ruler as "under-compliance to a
legitimate in-band signal." IBSC's `injection` family mirrors this line of work.

### 2.5 GateMem (2026)
**arXiv:2606.18829; code: rzhub/GateMem.** Benchmarks memory-augmented agents on utility, access
control across authorization boundaries, and active forgetting after deletion requests; finds no
method jointly achieves all three.

**How IBSC differs:** GateMem is domain-specific to shared-**memory** governance. IBSC treats a
memory "do-not-share" label as **one instance** of a legitimate in-band signal whose uptake is
measured, alongside injected dates, access-deny banners, and tool allowlists — GateMem is one
vertical; IBSC is the horizontal abstraction. GateMem also lacks the adversarial over-compliance
pole and the unifying legitimacy metric. We cite it as concurrent evidence that the
under-compliance failure is real and unsolved.

### 2.6 Recuse — author's own prior work, closest term match
**Munirathinam, T. (2026). Will the Agent Recuse Itself? Measuring LLM-Agent Compliance with
In-Band Access-Deny Signals. arXiv:2606.06460.** Proposes the "Recuse Signal," a cooperative
in-band deny signal (SSH banner, PostgreSQL NOTICE, k8s webhook) asking an agent to voluntarily
withdraw; live-host pilot shows 100% recusal when present vs 100% completion without. Metric =
recusal rate.

**How IBSC differs (and self-scoop mitigation):** This is the direct predecessor and the only
work using the "in-band ... signal" phrasing, but it is (a) a **single** signal type
(access-deny), (b) **one polarity** (uptake of a legitimate deny signal), and (c) a small live
pilot, not a benchmark/leaderboard. IBSC generalizes it into a full framework: many signal types
(date, deny, do-not-share, allowlist) × **both** polarities (legitimate uptake AND adversarial
resistance) × one unified correctness-given-legitimacy metric × a leaderboard. We frame IBSC
explicitly as the **generalization of the recusal result** — recusal is the first datapoint on
the under-compliance axis, not an unrelated new claim. This is both honest and strengthens the
narrative.

### 2.7 Temporal Blindness (2025/2026) — term-collision caveat
**Your LLM Agents are Temporally Blind, arXiv:2510.23853.** Documents that agents treat each turn
as timeless — failing to reason about *elapsed* real-world time and to recognize stale cached
information.

**How IBSC differs (and honesty note):** That work's "temporal blindness" is about failure to
**perceive elapsed time**, not about ignoring an explicitly **injected** date signal. IBSC's
temporal case is narrower and cleaner — a legitimate current-date signal is placed in-band and
the metric is whether the agent **adopts** it. IBSC cites this to name the phenomenon but
operationalizes it as a special case of in-band under-compliance (measurable, binary). **We do
not claim to have coined "temporal blindness."**

---

## 3. Comparison table

| work | legitimate-signal uptake? | adversarial resistance? | unified single metric? | leaderboard? | scope |
|---|---|---|---|---|---|
| Instruction Hierarchy (2404.13208) | no | yes (via training) | no (conflict resolution) | no | training intervention |
| IFEval (2311.07911) | user-only, always legitimate | no | no | no | user-instruction following |
| AgentDojo (2406.13352) | no | yes | no | attack-success | injection attacks/defenses |
| InjecAgent (2403.02691) | no | yes | no | no | IPI vulnerability |
| GateMem (2606.18829) | memory only | no | no | no | memory governance |
| Recuse (2606.06460, author) | access-deny only | no | no | no (live pilot) | single in-band deny signal |
| Temporal Blindness (2510.23853) | elapsed-time perception | no | no | no | time perception |
| **IBSC / signalbench (this work)** | **yes (4+ signal types)** | **yes** | **yes (SRC / IBSC-Score)** | **yes** | **environment-signal compliance, both poles** |

---

## 4. Honest risk register

- **Self-scoop / incremental novelty (highest):** the closest work is the author's own Recuse
  paper. Mitigation: position IBSC as the generalization (many types × both polarities × one
  metric × leaderboard), cite recusal as the seed datapoint, and make the *unification* the
  headline — not the term.
- **Instruction Hierarchy overlap (biggest external):** a reviewer may say "this is just
  evaluating IH compliance." Mitigation: IH is training + conflict-resolution and covers only the
  resist half; IBSC is measurement of lone-signal uptake plus the under-compliance half plus the
  unifying metric. The predicted "IH models over-suppress legitimate signals" finding, once
  measured, is the sharpest separator.
- **Term-collision (temporal blindness):** already claimed for elapsed-time perception. We cite,
  reuse, and distinguish; we do not claim to coin it.
- **"Just a mashup":** each sub-case has a dedicated benchmark. Mitigation: the contribution is
  the theoretical claim that these are one phenomenon on one metric — demonstrated by cross-signal
  correlation/transfer no single-vertical benchmark can show (future work; see RESEARCH.md).
- **Name is weakly defensible alone:** verified unclaimed, but a name is not a result. Mitigation:
  publish promptly to plant the flag; lead with measurement/unification.

---

## 5. What this is NOT / does NOT claim to invent

- IBSC does **not** claim to invent prompt injection, indirect prompt injection, the instruction
  hierarchy, memory governance, temporal blindness, or the term "in-band signaling."
- IBSC does **not** claim to *defend against* injection — it **measures** susceptibility as
  over-compliance.
- IBSC does **not** present real multi-vendor empirical results in v0; the shipped run is an
  offline reference run with a deterministic mock provider.
- The **contribution** is the unification of legitimate-signal uptake and adversarial-signal
  resistance under one correctness-given-legitimacy metric on one leaderboard, plus the naming of
  the category.
