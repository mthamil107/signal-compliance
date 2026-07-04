"""ClaudeCodeProvider: drive the local ``claude`` CLI in print mode.

Uses a Claude Code *subscription* (no API credit) by shelling out to
``claude -p ... --output-format json``. IMPORTANT: this evaluates **Claude Code
as a deployed agent** — the model runs under Claude Code's own system prompt, and
tools are disabled so it answers in text. It is therefore NOT a bare-model row and
must be reported separately from the API-model leaderboard. Because signalbench's
own tools are not exposed, tool-graded items (``required_tool`` / ``forbidden_tool``
with no ``forbidden_tokens``) are approximate; secret-leak, refusal, and
uptake items grade cleanly from the text.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time

from ..core import Item, Response
from .base import Provider

__all__ = ["ClaudeCodeProvider"]

def _resolve_claude() -> str:
    """Find a directly-executable claude binary (not the .cmd/.bat shim).

    subprocess cannot run a Windows `.cmd` shim without a shell, so prefer the
    native `claude.exe` the shim points to (npm layout), falling back to whatever
    is on PATH.
    """
    exe = shutil.which("claude.exe")
    if exe:
        return exe
    shim = shutil.which("claude")
    if shim:
        import os
        cand = os.path.join(
            os.path.dirname(shim), "node_modules", "@anthropic-ai",
            "claude-code", "bin", "claude.exe",
        )
        if os.path.isfile(cand):
            return cand
        return shim
    return "claude"


_CLAUDE = _resolve_claude()

# Deny every built-in Claude Code tool so it answers in text only.
_DISABLED_TOOLS = (
    "Bash Edit Write Read Glob Grep WebFetch WebSearch Task NotebookEdit "
    "TodoWrite MultiEdit"
)


class ClaudeCodeProvider(Provider):
    """A system-under-test backed by the Claude Code CLI (subscription)."""

    def __init__(self, model: str = "claude-haiku-4-5-20251001", timeout: float = 180.0):
        self.model = model
        self.name = f"claude-code:{model}"
        self.timeout = timeout

    def complete(self, item: Item) -> Response:
        cmd = [
            _CLAUDE, "-p", item.to_prompt(),
            "--model", self.model,
            "--disallowedTools", _DISABLED_TOOLS,
            "--output-format", "json",
        ]
        t0 = time.time()
        try:
            proc = subprocess.run(
                cmd, capture_output=True, text=True,
                timeout=self.timeout, encoding="utf-8",
            )
        except subprocess.TimeoutExpired:
            return Response(item_id=item.item_id, text="", error="claude-code timeout")
        except FileNotFoundError:
            return Response(item_id=item.item_id, text="", error="claude CLI not found on PATH")
        if proc.returncode != 0:
            return Response(
                item_id=item.item_id, text="",
                error=f"claude-code exit {proc.returncode}: {(proc.stderr or '')[:200]}",
            )
        try:
            data = json.loads(proc.stdout)
        except (json.JSONDecodeError, TypeError) as exc:
            return Response(
                item_id=item.item_id, text="",
                error=f"claude-code parse error: {exc}; out={proc.stdout[:200]}",
            )
        if data.get("is_error"):
            return Response(
                item_id=item.item_id, text="",
                error=f"claude-code: {str(data.get('result',''))[:200]}",
            )
        return Response(
            item_id=item.item_id,
            text=data.get("result") or "",
            tool_calls=[],
            raw={"cost_usd": data.get("total_cost_usd"), "model": self.model},
            latency_ms=(time.time() - t0) * 1000.0,
        )
