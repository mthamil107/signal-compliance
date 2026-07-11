---
license: apache-2.0
pretty_name: In-Band Signal Compliance (IBSC) / signalbench leaderboard
tags:
- llm
- benchmark
- ai-safety
- ai-security
- prompt-injection
- llm-agents
- llm-evaluation
size_categories:
- n<1K
configs:
- config_name: leaderboard
  data_files: leaderboard.csv
  default: true
- config_name: items
  data_files: items.jsonl
---

# In-Band Signal Compliance (IBSC) — signalbench leaderboard

**One metric for prompt injection *and* temporal blindness.** LLM agents read control
instructions and ordinary data through the same channel, so they must decide whether to obey each
instruction.

The benchmark measures two symmetric failure modes: **over-compliance** (obeying illegitimate
signals — prompt injection) and **under-compliance** (ignoring legitimate ones). The
Signal-Response Correctness (SRC) metric ranges 0–1 per item; a one-sided always-comply /
always-refuse policy scores 0.5.

## Dataset viewer
- **`leaderboard`** config (default) — one row per evaluated system with overall SRC, LSU, ISR,
  and per-family scores (`time`, `access_deny`, `memory_label`, `injection`, `bot_policy`).
- **`items`** config — the 75 benchmark items (`item_id`, `family`, `legitimacy`, `correct_action`).

Raw per-item model responses and verdicts for all 21 systems are in the `results/` folder (one
JSON per system) for offline re-grading.

**Key Resources:**
- Code / harness: https://github.com/mthamil107/signal-compliance
- DOI: https://doi.org/10.5281/zenodo.21223956

**Headline finding:** No model — open or closed — exceeds ~0.85. Frontier API models
(Gemini 2.5 Pro, GPT-4o-mini) reach 0.83–0.85; best open-weight models score 0.63–0.67.
Evaluation covers 21 systems across 75 items (single seed, July 2026). Across bare models the five
families are all positively correlated (mean Pearson r ≈ 0.73) — evidence they measure one
underlying ability, not five separate skills.

**Methodology:** Failures are detected only through observed actions (secret emission, forbidden
tool calls, spoofed-value adoption) — never via phrasing analysis. Grading is deterministic and
standard-library only (no LLM judge). Reproducible via the provided scripts.
