#!/usr/bin/env python
"""Run the real-provider study over all IBSC families and rank the models.

Loads API keys from ``~/.claude/servers/llm-Keys.env`` (or ``--env-file`` /
``SIGNALBENCH_ENV``), runs each requested model, writes one RunReport JSON per
model into ``results/``, and prints the combined leaderboard (mock reference
rows included if their JSON is present).

The default is a six-model study:
    OpenAI  : gpt-4o-mini, gpt-4.1, gpt-5.1, gpt-5.5
    Gemini  : gemini-2.5-flash, gemini-2.5-pro

Each model runs inside its own try/except, so an unavailable or failing model
logs an error line and the study continues with the rest.

Usage:
    python scripts/run_real.py                       # default six-model study
    python scripts/run_real.py --reasoning medium    # bump reasoning/thinking
    python scripts/run_real.py --models gpt-4o-mini,gemini-2.5-flash
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from signalbench.families import all_families  # noqa: E402
from signalbench.leaderboard import Leaderboard  # noqa: E402
from signalbench.providers._net import load_env  # noqa: E402
from signalbench.providers.gemini_provider import GeminiProvider  # noqa: E402
from signalbench.providers.openai_provider import OpenAIProvider  # noqa: E402
from signalbench.runner import Runner  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")

DEFAULT_MODELS = [
    "gpt-4o-mini",
    "gpt-4.1",
    "gpt-5.1",
    "gpt-5.5",
    "gemini-2.5-flash",
    "gemini-2.5-pro",
]

# Map a reasoning-effort level onto a bounded Gemini "thinkingBudget" (tokens).
# Values are deliberately small to keep cost down; 2.5-pro may clamp up to its
# enforced minimum server-side.
_THINKING_BUDGET = {
    "minimal": 128,
    "low": 128,
    "medium": 512,
    "high": 2048,
}


def _is_openai_model(model: str) -> bool:
    m = model.strip().lower()
    return m.startswith(("gpt", "o1", "o3", "o4"))


def _build_provider(model: str, reasoning: str):
    """Construct the right provider for a model id, wiring reasoning controls."""
    if _is_openai_model(model):
        return OpenAIProvider(model=model, reasoning_effort=reasoning)
    # Gemini (or anything else) -> Gemini provider with a bounded thinking budget.
    budget = _THINKING_BUDGET.get(reasoning)
    return GeminiProvider(model=model, thinking_budget=budget)


def _run(provider, seed: int) -> None:
    label = provider.name
    safe = label.replace(":", "_").replace("/", "_")
    print(f"\n=== {label} ===")
    report = Runner(provider, all_families(), seed=seed).run()
    report.provider_name = label
    out = os.path.join(RESULTS_DIR, f"{safe}.json")
    report.to_json(out)
    s = report.score
    n_err = sum(1 for v in report.verdicts if v.label.value == "error")
    print(
        f"IBSC-Score={s.ibsc_score:.3f}  LSU={s.lsu:.2f}  ISR={s.isr:.2f}  "
        f"under={s.under_compliance_rate:.2f}  over={s.over_compliance_rate:.2f}  "
        f"FTR={s.ftr:.2f}  errors={n_err}/{s.n_items}"
    )
    if n_err:
        print("  (errors count as non-correct; check keys/model id/network)")
    print(f"  wrote {os.path.relpath(out)}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--models",
        default=None,
        help="comma-separated model ids to run (overrides the default study)",
    )
    ap.add_argument(
        "--reasoning",
        default="low",
        help="reasoning effort for gpt-5*/o* models; maps to a low thinking "
        "budget for gemini-2.5 (minimal|low|medium|high)",
    )
    ap.add_argument("--env-file", default=None)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    loaded = load_env(args.env_file)
    print(f"loaded {len(loaded)} key(s) from env file" if loaded else "no env file loaded")

    if args.models:
        models = [m.strip() for m in args.models.split(",") if m.strip()]
    else:
        models = list(DEFAULT_MODELS)
    print(f"study: {len(models)} model(s) -> {', '.join(models)}  (reasoning={args.reasoning})")

    for model in models:
        try:
            provider = _build_provider(model, args.reasoning)
            _run(provider, args.seed)
        except Exception as exc:  # keep the study going if one model fails
            print(f"\n=== {model} ===")
            print(f"  ERROR: {model} failed/unavailable: {exc}")

    print("\n=== Leaderboard (results/) ===")
    print(Leaderboard.from_results_dir(RESULTS_DIR).to_table())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
