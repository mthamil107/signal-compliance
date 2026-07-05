#!/usr/bin/env python
"""Run signalbench on OPEN / OFFLINE models via an OpenAI-compatible backend.

Backends:
  ollama      local, fully offline (default host http://localhost:11434) -- no key
  hf          Hugging Face Inference router                 -- needs HF_TOKEN
  openrouter  OpenRouter                                    -- needs OPENROUTER_API_KEY
  custom      any OpenAI-compatible endpoint via --base-url and optional --key-env

Examples:
  # local offline models (after: ollama pull qwen2.5:7b llama3.2:3b mistral:7b)
  python scripts/run_open.py --backend ollama --models qwen2.5:7b,llama3.2:3b,mistral:7b

  # hosted open models (export HF_TOKEN=...)
  python scripts/run_open.py --backend hf --models meta-llama/Llama-3.1-8B-Instruct,Qwen/Qwen2.5-7B-Instruct

  # anything OpenAI-compatible
  python scripts/run_open.py --backend custom --base-url http://host:8000/v1/chat/completions --models my-model

Results are written to results/<label>_<model>.json, same format as the API runs,
so they drop straight into the leaderboard.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from signalbench.families import all_families  # noqa: E402
from signalbench.leaderboard import Leaderboard  # noqa: E402
from signalbench.providers._net import load_env  # noqa: E402
from signalbench.providers.openai_compatible import (  # noqa: E402
    HFProvider,
    OllamaProvider,
    OpenAICompatibleProvider,
    OpenRouterProvider,
)
from signalbench.runner import Runner  # noqa: E402

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "..", "results")


def _make(backend: str, model: str, args):
    if backend == "ollama":
        return OllamaProvider(model, host=args.host)
    if backend == "hf":
        return HFProvider(model)
    if backend == "openrouter":
        return OpenRouterProvider(model)
    if backend == "custom":
        if not args.base_url:
            raise SystemExit("--base-url is required for --backend custom")
        return OpenAICompatibleProvider(
            model, base_url=args.base_url, key_env=args.key_env, label=args.label
        )
    raise SystemExit(f"unknown backend {backend!r}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", required=True,
                    choices=["ollama", "hf", "openrouter", "custom"])
    ap.add_argument("--models", required=True, help="comma-separated model ids")
    ap.add_argument("--host", default="http://localhost:11434", help="ollama host")
    ap.add_argument("--base-url", default=None, help="custom OpenAI-compatible endpoint")
    ap.add_argument("--key-env", default=None, help="env var holding the api key (custom)")
    ap.add_argument("--label", default="open", help="leaderboard label prefix (custom)")
    ap.add_argument("--env-file", default=None)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    load_env(args.env_file)  # picks up HF_TOKEN / OPENROUTER_API_KEY if present
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    print(f"backend={args.backend}  models={models}")

    for model in models:
        try:
            provider = _make(args.backend, model, args)
            print(f"\n=== {provider.name} ===")
            report = Runner(provider, all_families(), seed=args.seed).run()
            report.provider_name = provider.name
            safe = provider.name.replace(":", "_").replace("/", "_")
            out = os.path.join(RESULTS_DIR, f"{safe}.json")
            report.to_json(out)
            s = report.score
            n_err = sum(1 for v in report.verdicts if v.label.value == "error")
            print(f"IBSC={s.ibsc_score:.3f}  LSU={s.lsu:.2f}  ISR={s.isr:.2f}  "
                  f"errors={n_err}/{s.n_items}  wrote {os.path.relpath(out)}")
            if n_err:
                print("  (errors: model may not support tools, or endpoint/key issue)")
        except Exception as exc:
            print(f"\n=== {model} ===\n  ERROR: {exc}")

    print("\n=== Leaderboard (results/) ===")
    print(Leaderboard.from_results_dir(RESULTS_DIR).to_table())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
