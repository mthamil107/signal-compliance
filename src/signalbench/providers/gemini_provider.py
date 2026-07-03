"""Google Gemini (generativelanguage API) provider, std-lib HTTP.

Reads ``GEMINI_API_KEY`` (or ``GOOGLE_API_KEY``). Standard AI Studio keys
(``AIza...``) authenticate via the ``?key=`` query param; anything else is
treated as an OAuth bearer token and sent in the ``Authorization`` header, so
both credential styles work. Item tool manifests are exposed as Gemini
``function_declarations``. Parsing is factored into :func:`parse_gemini` for
offline unit tests.
"""

from __future__ import annotations

import os
import time

from ..core import Item, Response
from .base import Provider
from ._net import build_tool_specs, post_json

__all__ = ["GeminiProvider", "parse_gemini"]

_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-2.5-flash"


def _gemini_tools(item: Item) -> list[dict]:
    specs = build_tool_specs(item.available_tool_names())
    if not specs:
        return []
    decls = [
        {
            "name": s["name"],
            "description": s["description"],
            "parameters": {"type": "object", "properties": {}},
        }
        for s in specs
    ]
    return [{"function_declarations": decls}]


def parse_gemini(data: dict, item_id: str) -> Response:
    """Turn a generateContent JSON body into a Response (pure, testable)."""
    if isinstance(data, dict) and data.get("error"):
        err = data["error"]
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        return Response(item_id=item_id, text="", error=f"gemini error: {msg}")
    try:
        parts = data["candidates"][0]["content"]["parts"]
    except (KeyError, IndexError, TypeError):
        return Response(item_id=item_id, text="", error=f"malformed response: {data}")
    text_parts: list[str] = []
    tool_calls: list[dict] = []
    for part in parts:
        if "text" in part and part["text"]:
            text_parts.append(part["text"])
        fc = part.get("functionCall")
        if fc:
            tool_calls.append(
                {"name": fc.get("name", ""), "arguments": fc.get("args", {}) or {}}
            )
    return Response(
        item_id=item_id,
        text="".join(text_parts),
        tool_calls=tool_calls,
        raw=data,
    )


class GeminiProvider(Provider):
    """Gemini chat model under test."""

    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        *,
        api_key: str | None = None,
        temperature: float = 0.0,
        timeout: float = 60.0,
        thinking_budget: int | None = None,
    ):
        self.model = model
        self.name = f"gemini:{model}"
        self._api_key = (
            api_key
            or os.environ.get("GEMINI_API_KEY")
            or os.environ.get("GOOGLE_API_KEY")
        )
        self.temperature = temperature
        self.timeout = timeout
        self.thinking_budget = thinking_budget

    def _url_and_headers(self) -> tuple[str, dict]:
        """Pick auth style. Google API keys (``AIza...``, newer ``AQ.*``, etc.)
        go in the ``?key=`` query param; only OAuth2 access tokens (``ya29.*``)
        or an explicit ``GEMINI_AUTH=bearer`` use the Authorization header."""
        url = f"{_BASE}/{self.model}:generateContent"
        key = self._api_key or ""
        use_bearer = key.startswith("ya29.") or (
            os.environ.get("GEMINI_AUTH", "").lower() == "bearer"
        )
        if use_bearer:
            return url, {"Authorization": f"Bearer {key}"}
        return f"{url}?key={key}", {}

    def complete(self, item: Item) -> Response:
        if not self._api_key:
            return Response(item_id=item.item_id, text="", error="GEMINI_API_KEY not set")
        messages = item.as_messages()
        system = next((m["content"] for m in messages if m["role"] == "system"), "")
        user = next((m["content"] for m in messages if m["role"] == "user"), "")
        payload: dict = {
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": self.temperature},
        }
        # 2.5 models expose a thinking budget; a low value bounds cost. Only
        # send it for gemini-2.5-* (note: 2.5-pro may clamp to a minimum).
        if self.thinking_budget is not None and "gemini-2.5" in (self.model or ""):
            payload["generationConfig"]["thinkingConfig"] = {
                "thinkingBudget": int(self.thinking_budget)
            }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}
        tools = _gemini_tools(item)
        if tools:
            payload["tools"] = tools
        url, headers = self._url_and_headers()
        t0 = time.time()
        try:
            data = post_json(url, payload, headers, timeout=self.timeout)
        except Exception as exc:
            return Response(item_id=item.item_id, text="", error=str(exc))
        resp = parse_gemini(data, item.item_id)
        resp.latency_ms = (time.time() - t0) * 1000.0
        return resp
