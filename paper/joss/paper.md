---
title: 'signalbench: A benchmark for In-Band Signal Compliance in LLM agents'
tags:
  - Python
  - large language models
  - LLM agents
  - AI safety
  - AI security
  - prompt injection
  - benchmark
authors:
  - name: Thamilvendhan Munirathinam
    orcid: 0000-0000-0000-0000
    affiliation: 1
affiliations:
  - name: Independent Researcher
    index: 1
date: 2027-01-01
bibliography: paper.bib
---

# Summary

An LLM agent reads control instructions and ordinary data through the *same* input
channel: the system prompt, a tool's result, a retrieved web page, a recalled memory, a
fetched usage policy. When an instruction arrives in that channel from the **environment**
rather than the user, the agent must decide — from content alone — whether to obey it. It
fails in two symmetric ways. It **over-complies**, obeying an illegitimate instruction it
should have refused (the canonical case is *prompt injection*). And it **under-complies**,
ignoring a legitimate instruction it should have taken up (ignoring an injected date;
disregarding an access-deny signal; leaking a `do-not-share` memory; scraping a page whose
policy forbids automation).

`signalbench` is a zero-dependency Python benchmark that scores both failure modes on one
metric, **Signal-Response Correctness (SRC)** — a per-item 0/1 score aggregated as the
balanced mean of legitimate-signal uptake and illegitimate-signal resistance, so a trivial
always-comply or always-refuse policy scores 0.5. It ships five self-contained, offline
signal families (`time`, `access-deny`, `memory-label`, `injection`, `bot-policy`), a
deterministic **action-based** grader (a failure is asserted only on an observed action — an
emitted secret value, a forbidden tool call, an adopted spoofed value — never on phrasing),
a mock provider for offline reproduction, and adapters for OpenAI-, Anthropic-, Google-, and
any OpenAI-compatible endpoint (Ollama, Hugging Face, OpenRouter). The harness, metric, and
five families run with no API key and no network.

# Statement of need

Prompt injection and the ignoring of legitimate control signals are usually studied as
separate problems, each with its own single-pole benchmark: adversarial-only suites such as
AgentDojo [@agentdojo] and InjecAgent [@injecagent] measure resistance; instruction-following
suites such as IFEval [@ifeval] measure uptake of *user* instructions. No prior tool places
*environment-originated* legitimate-signal uptake and adversarial-signal resistance on a
single axis, which is what practitioners actually need when an agent must adjudicate every
in-band instruction on every turn. `signalbench` fills that gap and makes the resulting
measurement reproducible: it is deterministic, LLM-judge-free, and ships the raw per-item
responses for every evaluated model so results can be re-graded offline.

The tool is designed for two audiences: safety/security researchers who need a common,
extensible measurement of agent compliance, and practitioners who want to compare candidate
models before deploying an agent that touches tools, retrieved content, or memory. New signal
families and providers are added by implementing one small interface each.

# Research use

`signalbench` underpins a study of 21 systems (frontier API models, open-weight models, and a
deployed-agent contrast). Two findings illustrate its use: no evaluated model exceeds an SRC
of 0.85, and — across models with full coverage — the five signal families are all positively
correlated (mean Pearson $r \approx 0.73$ on bare models), evidence that they measure one
underlying ability rather than five separate skills. The benchmark, leaderboard, and raw
results are archived with a DOI [@ibsc-zenodo].

# AI usage disclosure

Generative AI tools (Claude) were used to assist with software implementation, documentation,
and drafting of this paper. All design decisions, the metric definition, the family designs,
the evaluation methodology, and all reported results were directed and verified by the author.

# Acknowledgements

The `access-deny`, `memory-label`, and `injection` families build on the author's prior work
on in-band access-deny signals, agent memory wire formats, and prompt-injection detection.

# References
