"""Shared helpers for real (HTTP) providers: env loading + JSON POST with retry.

Std-lib only (urllib) so the package keeps zero hard runtime dependencies. Keys
are read from the process environment; :func:`load_env` can populate it from a
``KEY=VALUE`` file (default ``~/.claude/servers/llm-Keys.env``) WITHOUT ever
overriding a value already present in the environment, and without logging any
value.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

__all__ = ["load_env", "default_env_path", "post_json", "build_tool_specs"]


def default_env_path() -> str:
    return os.path.expanduser(os.path.join("~", ".claude", "servers", "llm-Keys.env"))


def load_env(path: str | None = None, *, override: bool = False) -> list[str]:
    """Load ``KEY=VALUE`` pairs from *path* into ``os.environ``.

    Returns the list of key names that were set (never the values). Tolerates
    ``KEY = "value"`` with spaces/quotes and ``#`` comment lines. Missing files
    are a silent no-op so offline use never breaks.
    """
    path = path or os.environ.get("SIGNALBENCH_ENV") or default_env_path()
    set_keys: list[str] = []
    if not os.path.isfile(path):
        return set_keys
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, val = line.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'").strip()
            if not key or not val:
                continue
            if override or key not in os.environ:
                os.environ[key] = val
                set_keys.append(key)
    return set_keys


def post_json(
    url: str,
    payload: dict,
    headers: dict,
    *,
    timeout: float = 60.0,
    retries: int = 3,
    backoff: float = 1.5,
) -> dict:
    """POST *payload* as JSON and return the parsed JSON response.

    Retries transient failures (429 and 5xx, plus URLError) with linear backoff.
    Raises RuntimeError with the status/body on a non-retryable HTTP error.
    """
    data = json.dumps(payload).encode("utf-8")
    hdrs = {"Content-Type": "application/json", **headers}
    last_exc: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = ""
            try:
                body = exc.read().decode("utf-8", "replace")[:500]
            except Exception:  # pragma: no cover - defensive
                pass
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                last_exc = RuntimeError(f"HTTP {exc.code}: {body}")
                time.sleep(backoff * (attempt + 1))
                continue
            raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
        except urllib.error.URLError as exc:
            last_exc = RuntimeError(f"URLError: {exc.reason}")
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
                continue
            raise last_exc from exc
    raise last_exc or RuntimeError("post_json failed")  # pragma: no cover


def build_tool_specs(tool_names: list[str]) -> list[dict]:
    """Neutral, provider-agnostic tool descriptors for a set of names."""
    return [
        {
            "name": name,
            "description": (
                f"Callable tool '{name}'. Decide whether invoking it is "
                "appropriate given the situation and any policy signals present."
            ),
        }
        for name in tool_names
    ]
