# signalbench → Hugging Face Community Evals

Goal: attach signalbench's **Signal-Response Correctness (SRC)** score to the HF pages of the
12 open-weight models we evaluated, so the score surfaces **passively** on each popular model's
page (and aggregates onto the signalbench leaderboard). This is the highest-leverage discovery
move that needs **no arXiv** and **no model-author approval** — community results show while the
PR is open.

Source of the mechanism: <https://huggingface.co/docs/hub/eval-results> (Community Contributions).

## What's in this folder
- `eval.yaml` — the Benchmark registration for the **dataset** repo (`thamilvendhan/signalbench`).
- `<org>__<model>.yaml` — one ready-to-submit `.eval_results/` file per model, with the **real** SRC
  + per-family scores. 12 files.

## The 12 target model repos (real HF pages)
| SRC | HF model repo |
|----:|---|
| 0.667 | `Qwen/Qwen2.5-72B-Instruct` |
| 0.633 | `meta-llama/Llama-3.1-8B-Instruct` |
| 0.583 | `Qwen/Qwen3-Next-80B-A3B-Instruct` |
| 0.567 | `deepseek-ai/DeepSeek-V3` ⚠️ verify slug (OpenRouter `deepseek-chat` → V3 at eval time) |
| 0.417 | `meta-llama/Llama-3.3-70B-Instruct` |
| 0.417 | `microsoft/phi-4` |
| 0.417 | `mistralai/Mistral-Small-24B-Instruct-2501` |
| 0.400 | `google/gemma-2-27b-it` |
| 0.383 | `Qwen/Qwen2.5-7B-Instruct` |
| 0.367 | `meta-llama/Llama-3.2-3B-Instruct` |
| 0.317 | `mistralai/Mistral-Nemo-Instruct-2407` |
| 0.300 | `NousResearch/Hermes-3-Llama-3.1-70B` |

Closed models (OpenAI/Gemini/Claude) have **no HF model page** — they can't take a community eval.
They live only on the signalbench leaderboard Space.

## Order of operations (this sequence matters)
The model `.eval_results` reference `dataset.id: thamilvendhan/signalbench` with a `task_id`. For
the **leaderboard aggregation** to work, the dataset must first be a registered **Benchmark**.

1. **Register signalbench as a Benchmark.**
   - Push `eval.yaml` to the **root** of `huggingface.co/datasets/thamilvendhan/signalbench`.
   - It's validated at push time. Then (beta) **contact HF to be added to the allow-list**
     (that's a required manual step per the docs).
   - ⚠️ Caveat: `evaluation_framework` must be an HF-maintained enum value. signalbench uses a
     custom action-based grader, so to be *fully* auto-runnable it needs the **inspect-ai port**
     (fill `field_spec`/`solvers`/`scorers`). Until that's done, submit the scores as
     **pre-computed community results** — they still show as "community" and aggregate on the card;
     they just won't carry the "verified" badge (that badge requires the eval to run in HF Jobs).

2. **Submit one PR per model** (12 total). For each model repo:
   - Go to the model page → **Community** tab → open a **Pull Request**.
   - Add the matching file from this folder as `.eval_results/signalbench.yaml`.
   - It shows as **community-provided** while the PR is open.

## Doing it with the API (optional, faster than 12 web PRs)
With `HF_TOKEN` set, `huggingface_hub` can open the PRs programmatically:

```python
from huggingface_hub import HfApi
api = HfApi()  # needs HF_TOKEN with write scope
# For each model file: create a PR (revision) adding .eval_results/signalbench.yaml
api.upload_file(
    path_or_fileobj="Qwen__Qwen2.5-72B-Instruct.yaml",
    path_in_repo=".eval_results/signalbench.yaml",
    repo_id="Qwen/Qwen2.5-72B-Instruct",
    repo_type="model",
    create_pr=True,                       # opens a PR instead of pushing to main
    commit_message="Add signalbench (In-Band Signal Compliance) community eval",
)
```
`create_pr=True` is the key — you never need write access to the model; it opens a PR the
maintainer can accept, ignore, or close. While open, the score is visible.

## Honest caveats (so nothing surprises you)
- **Scores are low for open models** (0.30–0.67). That's the true result and it's *fine* — a
  benchmark that everyone aces is useless. Low scores on a hard, novel axis are the selling point.
- **A model author can close the PR** to remove a disputed score. Ours are defensible (real logged
  actions, deterministic grader, raw responses linked in `source.url`), so disputes are unlikely,
  but it can happen.
- **This is a beta HF feature** (launched ~Feb 2026); schema/flow may shift. Re-check the docs
  before a bulk run.
- **`deepseek-ai/DeepSeek-V3`**: confirm the OpenRouter `deepseek-chat` slug still maps to V3 (not
  V3.1/other) for the eval date before submitting that one.

## Regenerate
`python scripts/gen_community_evals.py` re-emits every file from `results/*.json`.
