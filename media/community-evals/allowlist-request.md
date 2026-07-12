# HF Benchmark allow-list request (you send this)

Registering a dataset as a Benchmark is beta and gated on a manual HF allow-list step. Post this
on the **HF forums** (https://discuss.huggingface.co, "Datasets" category) or the
`huggingface/hub-docs` GitHub, or email the HF team if you have a contact.

---

**Subject:** Add `thamilvendhan/signalbench` to the Benchmark allow-list

Hi HF team,

I'd like to register my dataset **`thamilvendhan/signalbench`** as a Benchmark so its leaderboard
aggregates community eval results across the Hub.

- Dataset: https://huggingface.co/datasets/thamilvendhan/signalbench
- `eval.yaml` is pushed to the repo root (validated at push time).
- It's **signalbench / In-Band Signal Compliance (IBSC)** — one metric (Signal-Response
  Correctness) unifying prompt injection (over-compliance) and temporal-blindness / access-deny /
  memory-label / bot-policy failures (under-compliance) for LLM agents. Apache-2.0, DOI
  10.5281/zenodo.21223956, code at github.com/mthamil107/signal-compliance.
- Tasks defined: `src` (overall) + five families (`time`, `access_deny`, `memory_label`,
  `injection`, `bot_policy`).

Could you add it to the Benchmark allow-list? Happy to adjust `eval.yaml` if the schema needs
anything (e.g. completing the `inspect-ai` `field_spec`/`solvers`/`scorers`).

Thanks!

---

**Note:** until allow-listed, the per-model `.eval_results/` community-eval PRs will still show as
"community" scores on the model pages, but won't aggregate onto the signalbench leaderboard card.
So allow-listing is what turns the 12 PRs into a populated leaderboard.
