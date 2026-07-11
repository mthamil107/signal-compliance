# IBSC / signalbench — media kit

**Rule of this kit:** lead with the *finding*, not the repo. Links are citations, not ads.
The hook is the reframe — "prompt injection and temporal blindness are the same bug" — plus
one hard number (none of 21 systems > 0.85) and one non-obvious result (the five families
correlate at r=0.73, so it's one axis, not five benchmarks stapled together).

Canonical links:
- Writeup: https://mthamil107.github.io/writing/in-band-signal-compliance.html
- Repo: https://github.com/mthamil107/signal-compliance
- Data (HF): https://huggingface.co/datasets/thamilvendhan/signalbench
- DOI: https://doi.org/10.5281/zenodo.21223956

---

## Channel plan (ranked by fit × safety)

| Channel | Fit | Flag risk | Action |
|---|---|---|---|
| **LessWrong / AI Alignment Forum** | ★★★ agent safety = their remit | Low (author writeups welcome) | Post the essay below |
| **X/Twitter thread** | ★★★ where ML/agent researchers are | Low if finding-first | Post thread; tag no one on v1 |
| **LinkedIn** | ★★ your own network + credibility | Very low | Post the note below |
| **HF Community Evals** | ★★★ passive distribution on 12 popular model pages | None (sanctioned PR flow) | Submit SRC scores as community evals |
| **HF leaderboard Space** | ★★★ the discovery hub (like MTEB/GAIA) — replaces a self-hosted domain | None | Convert the Space into a leaderboard |
| **Bluesky (AI research feed)** | ★★ growing ML crowd | Low | Repost the X thread |
| **HF Community / blog article** | ★★ dataset already lives there | Low | Optional community post |
| ~~Papers With Code~~ | — | **shut down 24 Jul 2025** | dead — do not use |
| ~~Hacker News~~ | — | **domain flagged** | skip |
| ~~Reddit r/ML, r/LocalLLaMA~~ | — | karma/self-promo gated | skip for now |

Sequencing (evidence-based — the SAD benchmark launched all channels *together*, not drip-fed):
**coordinated same-day launch** — LessWrong post + X thread + LinkedIn go out the *same day*,
the thread and LinkedIn linking the LW post as the "full writeup" (a durable URL, not the raw
repo). The HF Community Evals + leaderboard Space are seeded *before* launch day so anyone the
thread sends to a model page already sees the SRC score there. Amplification by a recognized
researcher (a quote-boost, not a cold @) is the single biggest multiplier — worth one warm ask.

---

## 1) X / Twitter thread (finding-first)

**1/**
Prompt injection and "temporal blindness" look like two different LLM-agent bugs.

They're the same bug — seen from opposite ends.

I put 21 LLM systems through both. None scored above 0.85. 🧵

**2/**
An agent reads *instructions* and *data* through the same channel: system prompt, a tool's
output, a fetched web page, a recalled memory.

When an instruction shows up in that channel, it has to decide from content alone: obey, or ignore?

It fails two ways.

**3/**
OVER-comply — obey an illegitimate instruction it should've refused. (This is prompt injection.)

UNDER-comply — ignore a legitimate one it should've taken: an injected date, an access-deny
signal, a "do-not-share" memory label, a page whose policy forbids scraping.

Same decision. Mirror-image errors.

**4/**
So I scored both on ONE metric — Signal-Response Correctness (SRC): the balanced mean of
legitimate-signal uptake and illegitimate-signal resistance.

An always-obey OR always-refuse policy scores 0.5. You only win by adjudicating.

5 families, 75 items/model, deterministic, no LLM judge.

**5/**
Result across 21 systems (frontier APIs + open weights):

• None exceed SRC 0.85.
• Capability doesn't save you — a small model beat gpt-5.1 and gpt-4.1.
• Hardest family: memory-label (do-not-share leaks), and it's hard across *every* vendor.

**6/**
"But isn't that just five separate benchmarks?"

No — and this is the part I didn't expect. Across bare models, all five families are
POSITIVELY correlated: mean Pearson r = 0.73.

That's evidence they measure one underlying ability, not five skills.

**7/**
Everything is open and reproducible — the harness, the 21-system leaderboard, and the raw
per-item model responses so you can re-grade offline. No API key needed to run it.

Writeup: https://mthamil107.github.io/writing/in-band-signal-compliance.html
Code + data + DOI in the post.

*(Optional reply, only after it gets traction — tag AgentDojo/InjecAgent authors as prior art you build on, never as a cold @.)*

---

## 2) LinkedIn post

I kept seeing two "different" LLM-agent problems treated separately:

→ prompt injection (the agent obeys an instruction it should have refused), and
→ temporal blindness / ignored access controls (the agent ignores a signal it should have obeyed).

They're the same bug. An agent reads instructions and data through the same input channel, and
on every turn it has to decide — from content alone — whether an in-band instruction is
legitimate. Over-comply and you get prompt injection; under-comply and you get an agent that
scrapes a no-automation page, leaks a "do-not-share" note, or acts on a stale date.

So I built **signalbench** — one metric (Signal-Response Correctness) that scores both failure
modes together — and ran 21 systems through it.

Findings:
• No system — frontier or open-weight — exceeds 0.85.
• Bigger isn't safer: a small model beat two much larger ones.
• The five signal families correlate at r ≈ 0.73, i.e. this is *one* underlying ability, not
five separate skills.

It's fully open: benchmark, leaderboard, raw per-item responses, and a citable DOI. Built to be
re-run and re-graded without trusting my numbers.

Writeup + links in comments. Curious what agent builders think — especially about the
memory-label result, which was the hardest family across every vendor.

#LLM #AIsafety #AIsecurity #LLMagents #promptinjection

*(First comment: paste the 4 canonical links. LinkedIn suppresses posts with outbound links in
the body, so links go in the comment.)*

---

## 3) LessWrong / AI Alignment Forum post

**Title:** Prompt injection and temporal blindness are the same failure — and no model I tested scores above 0.85

**Body:**

Two agent failures are usually studied apart:

- **Over-compliance:** the agent obeys an instruction that arrived in-band from the environment
  and should have been refused. The canonical case is prompt injection.
- **Under-compliance:** the agent ignores a legitimate in-band signal it should have taken up —
  an injected current date, an access-deny notice, a `do-not-share` memory label, a page whose
  usage policy forbids automation.

I think these are one phenomenon. An LLM agent reads control instructions and ordinary data
through the *same* channel, so on every turn it must adjudicate, from content alone, whether an
in-band instruction is legitimate. Over- and under-compliance are the two ways that single
judgment goes wrong. Calling one "security" and the other "capability" hides that they trade off
on one axis.

**Measuring it.** I scored both on one metric, Signal-Response Correctness (SRC): a per-item 0/1
score aggregated as the balanced mean of legitimate-signal uptake and illegitimate-signal
resistance. A degenerate always-obey or always-refuse policy pins to 0.5 — you can only exceed it
by actually distinguishing legitimate from illegitimate signals. The benchmark (signalbench) has
five self-contained families — time, access-deny, memory-label, injection, bot-policy — 75 items
per model, a deterministic action-based grader (a failure is asserted only on an *observed
action*: an emitted secret value, a forbidden tool call, an adopted spoofed value — never on
phrasing), and no LLM judge.

**Results across 21 systems** (frontier APIs, open-weight models, and a deployed-agent contrast):

1. **No system exceeds SRC ≈ 0.85.** The ceiling is low and universal.
2. **Capability is non-monotonic.** A small model outscored two substantially larger ones. Scale
   does not buy compliance.
3. **The hardest family is memory-label** (leaking a `do-not-share` value under an injected
   override), and it's hard across every vendor.
4. **It's one axis, not five.** Across models with full coverage, the five families are all
   positively correlated — mean Pearson r ≈ 0.73. That's the load-bearing result: it's evidence
   the families measure a single underlying ability rather than five stapled-together skills.

**Limits I want to be upfront about:** single seed, 75 items per model, deterministic grader (so
no judge noise but also no partial credit), and the transfer correlation is across models, not a
causal intervention. The obvious next step is an intervention: does a single fix (training or
prompting) that lifts one family lift the others? If yes, the single-axis claim gets much
stronger.

Everything is open — harness, leaderboard, and raw per-item responses so you can re-grade without
trusting my aggregation — with a citable DOI. I'd genuinely value disagreement on the framing:
is "one legitimacy axis" carving reality at a joint, or am I collapsing two things that deserve
to stay separate?

Writeup: https://mthamil107.github.io/writing/in-band-signal-compliance.html
Code: https://github.com/mthamil107/signal-compliance
Data + DOI: https://doi.org/10.5281/zenodo.21223956

---

## 4) Hugging Face Community Evals (the highest-leverage, permission-free move)

*Papers With Code shut down 24 Jul 2025 — it is no longer a channel. HF Community Evals + a
leaderboard Space are the replacement, and they're stronger: the scores live on the model pages
people already visit.*

HF now lets **any** user submit eval results for **any** model via a PR — including models you
don't own — shown as "community" results without the model author's approval. That means you can
attach signalbench's SRC score to the HF pages of the 12 open-weight models you tested, so the
score surfaces passively on each popular model's page.

- Mechanism: a result YAML in the model repo's `.eval_results/` (Inspect-AI eval format).
- Scope: the 12 open-weight systems with real HF pages (see `media/community-evals/` for the
  ready-to-submit per-model files and the exact repo IDs). Closed models (OpenAI/Gemini/Claude)
  have no HF model page — they live only on the signalbench leaderboard Space.
- Seed this *before* launch day so the thread lands on pages that already show the score.

---

## Do-not list (keeps you off the self-promo tripwires)
- No cold-posting the *repo URL* as the lead; lead with the finding, link the writeup.
- No @-tagging researchers on v1 of the thread (a warm quote-boost ask is fine — it's the #1 multiplier).
- No cross-posting the identical text to five subreddits (that's the pattern filters catch).
- Launch the finding across channels the *same day* (coordinated), then let it stand on the result.
