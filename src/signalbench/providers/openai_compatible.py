"""Providers for OpenAI-compatible endpoints: open-source and self-hosted models.

Most model runtimes now expose an OpenAI ``/chat/completions`` API, so a single
base-URL swap covers a huge range of open models:

- **Ollama** (local / fully offline): ``http://localhost:11434/v1/chat/completions``
  — no API key, runs open weights on your machine. `OllamaProvider`.
- **Hugging Face Inference router** (hosted open models, no GPU needed):
  ``https://router.huggingface.co/v1/chat/completions`` with ``HF_TOKEN``. `HFProvider`.
- **OpenRouter** (one key, many paid + open models):
  ``https://openrouter.ai/api/v1/chat/completions`` with ``OPENROUTER_API_KEY``. `OpenRouterProvider`.
- Anything else OpenAI-compatible (vLLM, Together, Fireworks, Groq, DeepSeek): `OpenAICompatibleProvider(base_url=..., key_env=...)`.

Reasoning-effort gating and temperature handling are inherited from OpenAIProvider;
open models are not matched as reasoning models, so a plain temperature is sent and
no reasoning_effort is attached.
"""

from __future__ import annotations

import os

from .openai_provider import OpenAIProvider

__all__ = [
    "OpenAICompatibleProvider",
    "OllamaProvider",
    "HFProvider",
    "OpenRouterProvider",
]


class OpenAICompatibleProvider(OpenAIProvider):
    """Any OpenAI-compatible chat endpoint."""

    def __init__(
        self,
        model: str,
        *,
        base_url: str,
        api_key: str | None = None,
        key_env: str | None = None,
        label: str = "open",
        **kw,
    ):
        key = api_key or (os.environ.get(key_env) if key_env else None) or "no-key"
        super().__init__(model=model, api_key=key, base_url=base_url, **kw)
        self.name = f"{label}:{model}"


class OllamaProvider(OpenAICompatibleProvider):
    """Local, fully-offline open models via Ollama (no API key)."""

    def __init__(self, model: str, *, host: str = "http://localhost:11434", **kw):
        super().__init__(
            model,
            base_url=f"{host.rstrip('/')}/v1/chat/completions",
            api_key="ollama",  # Ollama ignores the value but the header must exist
            label="ollama",
            **kw,
        )


class HFProvider(OpenAICompatibleProvider):
    """Hosted open models via the Hugging Face Inference router (needs HF_TOKEN)."""

    def __init__(self, model: str, **kw):
        super().__init__(
            model,
            base_url="https://router.huggingface.co/v1/chat/completions",
            key_env="HF_TOKEN",
            label="hf",
            **kw,
        )


class OpenRouterProvider(OpenAICompatibleProvider):
    """Many paid + open models via OpenRouter (needs OPENROUTER_API_KEY)."""

    def __init__(self, model: str, **kw):
        super().__init__(
            model,
            base_url="https://openrouter.ai/api/v1/chat/completions",
            key_env="OPENROUTER_API_KEY",
            label="openrouter",
            **kw,
        )
