#!/usr/bin/env python3
"""Generate Hugging Face Community Evals files from signalbench results.

Emits, under media/community-evals/:
  - eval.yaml                      : the signalbench Benchmark registration (dataset repo root)
  - <hf_org>__<hf_name>.yaml       : one .eval_results/ file per open-weight model with a real HF page

Only open-weight systems have HF model pages; closed models (OpenAI/Gemini/Claude) are omitted
(they live only on the signalbench leaderboard Space). Values are the real SRC scores.
"""
import json
import os
import glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(REPO, "results")
OUT = os.path.join(REPO, "media", "community-evals")

DATASET_ID = "thamilvendhan/signalbench"

# OpenRouter system id  ->  canonical Hugging Face model repo id.
# deepseek-chat mapped to DeepSeek-V3 (the model behind that OpenRouter slug at eval time) — VERIFY before PR.
HF_MAP = {
    "openrouter:qwen/qwen-2.5-72b-instruct": "Qwen/Qwen2.5-72B-Instruct",
    "openrouter:qwen/qwen-2.5-7b-instruct": "Qwen/Qwen2.5-7B-Instruct",
    "openrouter:qwen/qwen3-next-80b-a3b-instruct": "Qwen/Qwen3-Next-80B-A3B-Instruct",
    "openrouter:meta-llama/llama-3.1-8b-instruct": "meta-llama/Llama-3.1-8B-Instruct",
    "openrouter:meta-llama/llama-3.2-3b-instruct": "meta-llama/Llama-3.2-3B-Instruct",
    "openrouter:meta-llama/llama-3.3-70b-instruct": "meta-llama/Llama-3.3-70B-Instruct",
    "openrouter:google/gemma-2-27b-it": "google/gemma-2-27b-it",
    "openrouter:microsoft/phi-4": "microsoft/phi-4",
    "openrouter:mistralai/mistral-nemo": "mistralai/Mistral-Nemo-Instruct-2407",
    "openrouter:mistralai/mistral-small-24b-instruct-2501": "mistralai/Mistral-Small-24B-Instruct-2501",
    "openrouter:nousresearch/hermes-3-llama-3.1-70b": "NousResearch/Hermes-3-Llama-3.1-70B",
    "openrouter:deepseek/deepseek-chat": "deepseek-ai/DeepSeek-V3",
}

FAMILIES = ["time", "access_deny", "memory_label", "injection", "bot_policy"]

SOURCE_URL = "https://huggingface.co/datasets/thamilvendhan/signalbench"


def main():
    os.makedirs(OUT, exist_ok=True)

    # --- eval.yaml : Benchmark registration for the dataset repo root ---
    tasks = "\n".join(
        f"  - id: {t}" for t in (["src"] + FAMILIES)
    )
    eval_yaml = f"""# signalbench Benchmark registration — place at the ROOT of the dataset repo
# ({DATASET_ID}) to register it as a Hugging Face Benchmark.
# NOTE: evaluation_framework must be an HF-maintained enum value. signalbench's grader is a
# custom action-based grader (std-lib, no LLM judge). To make this fully auto-runnable you must
# either (a) port the grader to inspect-ai format and fill field_spec/solvers/scorers below, or
# (b) ask HF to add a 'signalbench' framework to their enum. Until then, scores are submitted as
# pre-computed community results (still valid; they show as 'community' and aggregate on the card).
name: signalbench (In-Band Signal Compliance)
description: >
  One benchmark and one metric (Signal-Response Correctness, SRC) that unify over-compliance
  (prompt injection) and under-compliance (temporal blindness, access-deny, memory-label leaks,
  bot-policy) for LLM agents. SRC is the balanced mean of legitimate-signal uptake and
  illegitimate-signal resistance; a trivial always-comply or always-refuse policy scores 0.5.
  Five families, 75 items/model, deterministic action-based grading, no LLM judge.
evaluation_framework: inspect-ai   # TODO: complete field_spec/solvers/scorers via the inspect-ai port

tasks:
{tasks}
"""
    with open(os.path.join(OUT, "eval.yaml"), "w", encoding="utf-8") as f:
        f.write(eval_yaml)

    # --- per-model .eval_results/ files ---
    made = []
    for path in sorted(glob.glob(os.path.join(RESULTS, "*.json"))):
        d = json.load(open(path, encoding="utf-8"))
        system = d["system"]
        if system not in HF_MAP:
            continue
        hf_id = HF_MAP[system]
        s = d["score"]
        pf = s["per_family"]

        lines = [
            f"# signalbench community eval for {hf_id}",
            f"# Submit as a PR: add this file to  {hf_id}/.eval_results/signalbench.yaml",
            f"# Source system id (OpenRouter): {system}   |   seed {d['seed']}   |   n={s['n_items']}",
            "",
            "- dataset:",
            f"    id: {DATASET_ID}",
            "    task_id: src",
            f"  value: {round(s['ibsc_score'], 4)}",
            f'  date: "2026-07-08"',
            "  source:",
            f"    url: {SOURCE_URL}",
            "    name: signalbench raw per-item responses",
            "    user: thamilvendhan",
            '  notes: "SRC overall; deterministic action-based grader, no LLM judge; seed 0, n=75"',
        ]
        for fam in FAMILIES:
            fam_n = pf[fam]["n"]
            lines += [
                "- dataset:",
                f"    id: {DATASET_ID}",
                f"    task_id: {fam}",
                f"  value: {round(pf[fam]['src_balanced'], 4)}",
                f'  date: "2026-07-08"',
                "  source:",
                f"    url: {SOURCE_URL}",
                "    user: thamilvendhan",
                f'  notes: "family={fam}; n={fam_n}"',
            ]
        fname = hf_id.replace("/", "__") + ".yaml"
        with open(os.path.join(OUT, fname), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        made.append((hf_id, round(s["ibsc_score"], 3)))

    print(f"eval.yaml + {len(made)} model files written to {OUT}")
    for hf_id, src in sorted(made, key=lambda x: -x[1]):
        print(f"  {src:.3f}  {hf_id}")


if __name__ == "__main__":
    main()
