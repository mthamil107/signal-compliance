---
title: signalbench leaderboard (IBSC)
emoji: 🛡️
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: true
license: apache-2.0
short_description: One metric for prompt injection + temporal blindness
tags:
- leaderboard
- llm
- benchmark
- ai-safety
- prompt-injection
---

# signalbench leaderboard — In-Band Signal Compliance (IBSC)

Central leaderboard for the **signalbench** benchmark: one metric (Signal-Response Correctness)
that unifies over-compliance (prompt injection) and under-compliance (temporal blindness,
access-deny, memory-label leaks, bot-policy) for LLM agents across 21 systems.

- Code / harness: https://github.com/mthamil107/signal-compliance
- Dataset + raw responses: https://huggingface.co/datasets/thamilvendhan/signalbench
- DOI: https://doi.org/10.5281/zenodo.21223956

Data is bundled in `leaderboard.csv`; regenerate from results via
`scripts/gen_community_evals.py` sibling tooling in the code repo.
