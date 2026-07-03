# Contributing to signalbench / IBSC

Thanks for your interest in **In-Band Signal Compliance (IBSC)** and the
`signalbench` benchmark. This is an early-stage (v0) research scaffold by a solo
independent researcher, and contributions — especially new signal families,
new providers, and real multi-vendor result runs — are very welcome.

## Ground rules

1. **Honesty first.** IBSC is a *position + benchmark-design* project with an
   offline mock provider and a deterministic reference run. Do **not** add
   claims of empirical results the repo has not actually produced. If you
   contribute a real run, label the provider, model, date, seed, and item
   counts, and keep the mock reference run clearly marked as MOCK.
2. **Offline by default.** The core harness, metric, mock provider, and all
   five family task sets MUST run with zero third-party dependencies and no
   network access. Anything requiring an API key or network goes behind an
   optional extra (`[anthropic]`, `[openai]`) and must degrade gracefully.
3. **Deterministic grading.** Grading is family-owned and std-lib only — no LLM
   judge. New checks should be programmatically verifiable (expected-answer
   match, forbidden-token absence, `must_refuse`, required/forbidden tool).
4. **Apache-2.0.** By contributing you agree your contribution is licensed under
   the project's Apache-2.0 license.

## Development setup

```bash
git clone https://github.com/mthamil107/signal-compliance
cd signal-compliance
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Run the offline demo (no API key, no network):

```bash
python scripts/run_microbench.py
```

Run the tests:

```bash
pytest
```

## Adding a new signal family

Each family is a subclass of `signalbench.families.base.SignalFamily` and must:

- set `name` and `signal_kind` class attributes;
- implement `build_items(seed, n)` yielding a mix of **legitimate**,
  **illegitimate**, and **NONE** (no-signal calibration) items, each with a
  `correct_action` and an `expected` grading key;
- implement `grade(item, response)` returning a `Verdict` with the correct
  `VerdictLabel` per the per-item scoring rules in `metric.py`;
- ship a **self-contained** offline task set (it may *optionally* enrich itself
  from a sibling repo if that repo is importable, but must never require it);
- register itself in `signalbench/families/__init__.py`;
- add tests under `tests/` mirroring the module name.

Keep families balanced: a family should emit both an uptake stratum (legitimate)
and, where meaningful, a resistance stratum (illegitimate), plus a matched
NONE probe so calibration (FTR) is measured in-distribution.

## Adding a provider

Subclass `signalbench.providers.base.Provider`, set a unique `name`, and
implement `complete(item) -> Response`, catching errors into `Response.error`.
Network providers belong in an optional extra and must not be imported at
package import time.

## Style

- `ruff` for lint/format, `mypy` for types (`pip install -e ".[dev]"`).
- Prefer small, pure functions; keep `core.py` and `metric.py` I/O-free.
- Commit messages: clear and descriptive; one logical change per PR.

## Reporting issues

Open a GitHub issue with a minimal reproduction. For anything that looks like a
scoring bug, include the item, the response, and the verdict you got vs. the one
you expected.
