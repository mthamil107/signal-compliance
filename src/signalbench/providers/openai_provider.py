"""OpenAI Chat Completions provider (std-lib HTTP, function-calling aware).

Reads ``OPENAI_API_KEY`` from the environment (see ``_net.load_env``). Exposes
each item's tool manifest as OpenAI ``tools`` so tool-graded families
(access_deny, bot_policy, ...) are scored on the model's real call decisions.
Response parsing is factored into :func:`parse_openai` so it is unit-testable
offline.
"""

from __future__ import annotations

import json
import os
import time

from ..core import Item, Response
from .base import Provider
from ._net import build_tool_specs, post_json

__all__ = ["OpenAIProvider", "parse_openai"]

_ENDPOINT = "https://api.openai.com/v1/chat/completions"
DEFAULT_MODEL = "gpt-4o-mini"

# Reasoning models accept ``reasoning_effort``; the classic chat models
# (gpt-4o-mini, gpt-4.1, ...) reject it with a 400, so we gate on the id.
_REASONING_PREFIXES = ("gpt-5", "o1", "o3", "o4")


def _is_reasoning_model(model: str) -> bool:
    m = (model or "").strip().lower()
    return m.startswith(_REASONING_PREFIXES)


def _openai_tools(item: Item) -> list[dict]:
    specs = build_tool_specs(item.available_tool_names())
    return [
        {
            "type": "function",
            "function": {
                "name": s["name"],
                "description": s["description"],
                "parameters": {"type": "object", "properties": {}},
            },
        }
        for s in specs
    ]


def parse_openai(data: dict, item_id: str) -> Response:
    """Turn a Chat Completions JSON body into a Response (pure, testable)."""
    try:
        msg = data["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return Response(item_id=item_id, text="", error=f"malformed response: {data}")
    text = msg.get("content") or ""
    tool_calls: list[dict] = []
    for tc in msg.get("tool_calls") or []:
        fn = tc.get("function", {})
        raw_args = fn.get("arguments") or "{}"
        try:
            args = json.loads(raw_args)
        except (json.JSONDecodeError, TypeError):
            args = {"_raw": raw_args}
        tool_calls.append({"name": fn.get("name", ""), "arguments": args})
    return Response(item_id=item_id, text=text, tool_calls=tool_calls, raw=data)


class OpenAIProvider(Provider):
    """OpenAI chat model under test."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        api_key: str | None = None,
        temperature: float = 0.0,
        timeout: float = 60.0,
        reasoning_effort: str | None = None,
        base_url: str = _ENDPOINT,
    ):
        self.model = model
        self.name = f"openai:{model}"
        self._api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.temperature = temperature
        self.timeout = timeout
        self.reasoning_effort = reasoning_effort
        self.base_url = base_url  # any OpenAI-compatible /chat/completions endpoint

    def complete(self, item: Item) -> Response:
        if not self._api_key:
            return Response(item_id=item.item_id, text="", error="OPENAI_API_KEY not set")
        payload: dict = {
            "model": self.model,
            "messages": item.as_messages(),
        }
        # Reasoning models (gpt-5*, o1/o3/o4) reject a non-default temperature
        # (only 1 is allowed), so we omit it for them and send it otherwise.
        if not _is_reasoning_model(self.model):
            payload["temperature"] = self.temperature
        # Only reasoning models (gpt-5*, o1/o3/o4) accept reasoning_effort;
        # sending it to gpt-4o-mini / gpt-4.1 triggers a 400.
        if self.reasoning_effort and _is_reasoning_model(self.model):
            payload["reasoning_effort"] = self.reasoning_effort
        tools = _openai_tools(item)
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        headers = {"Authorization": f"Bearer {self._api_key}"}
        t0 = time.time()
        try:
            data = post_json(self.base_url, payload, headers, timeout=self.timeout)
        except Exception as exc:
            # Some models (e.g. gpt-5.5) reject reasoning_effort + function tools
            # together on /chat/completions. Fall back to the same request
            # without reasoning_effort so tool-graded items still run.
            msg = str(exc)
            if "reasoning_effort" in msg and "tools" in payload and "reasoning_effort" in payload:
                payload.pop("reasoning_effort", None)
                try:
                    data = post_json(self.base_url, payload, headers, timeout=self.timeout)
                except Exception as exc2:
                    return Response(item_id=item.item_id, text="", error=str(exc2))
            else:
                return Response(item_id=item.item_id, text="", error=msg)
        resp = parse_openai(data, item.item_id)
        resp.latency_ms = (time.time() - t0) * 1000.0
        return resp
