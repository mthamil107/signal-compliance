"""argparse CLI entrypoint for signalbench."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from .families import FAMILIES, all_families, get_family
from .leaderboard import Leaderboard
from .providers._net import load_env
from .providers.gemini_provider import GeminiProvider
from .providers.mock import MockProvider
from .providers.openai_provider import OpenAIProvider
from .runner import Runner

__all__ = ["main"]


def _build_provider(args: argparse.Namespace):
    if args.provider == "mock":
        return MockProvider(
            policy=args.policy, seed=args.seed, compliance=args.compliance
        )
    if args.provider == "openai":
        return OpenAIProvider(model=args.model) if args.model else OpenAIProvider()
    if args.provider == "gemini":
        return GeminiProvider(model=args.model) if args.model else GeminiProvider()
    raise SystemExit(f"unknown provider {args.provider!r}")


def _select_families(spec: str):
    spec = spec.strip()
    if spec in ("all", "*", ""):
        return all_families()
    names = [s.strip() for s in spec.split(",") if s.strip()]
    families = []
    for name in names:
        if name not in FAMILIES:
            raise SystemExit(
                f"unknown family {name!r}; choose from all,{','.join(FAMILIES)}"
            )
        families.append(get_family(name))
    return families


def _cmd_run(args: argparse.Namespace) -> int:
    if args.provider != "mock":
        loaded = load_env(args.env_file)
        if loaded:
            print(f"loaded {len(loaded)} key(s) from env file")
    provider = _build_provider(args)
    families = _select_families(args.families)
    runner = Runner(provider, families, seed=args.seed)
    report = runner.run(n_per_family=args.n)
    score = report.score

    if args.system:
        system_name = args.system
    elif args.provider == "mock":
        system_name = f"{provider.name}:{args.policy}"
    else:
        system_name = provider.name
    report.provider_name = system_name

    if args.out:
        report.to_json(args.out)

    print(f"System: {system_name}   seed={args.seed}   n_items={score.n_items}")
    print(f"  IBSC-Score        : {score.ibsc_score:.3f}")
    print(f"  IBSC-Score (cal)  : {score.ibsc_score_cal:.3f}")
    print(f"  LSU / ISR         : {score.lsu:.3f} / {score.isr:.3f}")
    print(
        f"  under/over-comply : {score.under_compliance_rate:.3f} / "
        f"{score.over_compliance_rate:.3f}"
    )
    print(f"  FTR / abstain     : {score.ftr:.3f} / {score.abstain_rate:.3f}")
    print(f"  SRC_micro         : {score.src_micro:.3f}")
    print("  per-family SRC_balanced:")
    for fam, block in score.per_family.items():
        print(
            f"    {fam:<14} {block['src_balanced']:.3f}  "
            f"(LSU={block['lsu']:.2f} ISR={block['isr']:.2f} n={block['n']})"
        )
    if args.out:
        print(f"  wrote {args.out}")
    return 0


def _cmd_leaderboard(args: argparse.Namespace) -> int:
    lb = Leaderboard.from_results_dir(args.results)
    if args.format == "json":
        out = lb.to_json()
    elif args.format == "md":
        out = lb.to_markdown()
    else:
        out = lb.to_table()
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(out + "\n")
        print(f"wrote {args.out}")
    else:
        print(out)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="signalbench",
        description="In-Band Signal Compliance (IBSC) benchmark harness.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_run = sub.add_parser("run", help="run a provider over families and score it")
    p_run.add_argument(
        "--provider", default="mock", choices=["mock", "openai", "gemini"]
    )
    p_run.add_argument(
        "--model", default=None,
        help="model id for real providers (e.g. gpt-4o-mini, gemini-2.5-flash)",
    )
    p_run.add_argument(
        "--env-file", default=None,
        help="path to a KEY=VALUE env file (default ~/.claude/servers/llm-Keys.env)",
    )
    p_run.add_argument(
        "--policy",
        default="oracle",
        choices=["oracle", "always_comply", "always_resist", "random"],
        help="mock provider only",
    )
    p_run.add_argument("--compliance", type=float, default=0.5,
                       help="bias for the 'random' policy in [0,1]")
    p_run.add_argument("--families", default="all",
                       help="'all' or comma list: time,access_deny,memory_label,injection,bot_policy")
    p_run.add_argument("--n", type=int, default=None, help="max items per family")
    p_run.add_argument("--seed", type=int, default=0)
    p_run.add_argument("--system", default=None, help="label for the leaderboard")
    p_run.add_argument("--out", default=None, help="write RunReport JSON here")
    p_run.set_defaults(func=_cmd_run)

    p_lb = sub.add_parser("leaderboard", help="render a leaderboard from results/")
    p_lb.add_argument("--results", default="results/")
    p_lb.add_argument("--format", default="table", choices=["md", "json", "table"])
    p_lb.add_argument("--out", default=None)
    p_lb.set_defaults(func=_cmd_leaderboard)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
