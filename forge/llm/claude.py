from __future__ import annotations

import os

from forge.llm.base import LLMProvider, LLMResponse


class ClaudeProvider(LLMProvider):
    """Anthropic Claude backend.

    Requires ANTHROPIC_API_KEY env var or explicit api_key argument.
    """

    DEFAULT_MODEL = "claude-sonnet-4-6"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 2048,
    ) -> None:
        try:
            import anthropic
        except ImportError as exc:
            raise ImportError("Install anthropic: pip install anthropic") from exc
        self._client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self._model = model
        self._max_tokens = max_tokens

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        return self.chat([{"role": "user", "content": prompt}], system=system, **kwargs)

    def chat(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        params: dict = {
            "model": kwargs.get("model", self._model),
            "max_tokens": kwargs.get("max_tokens", self._max_tokens),
            "messages": messages,
        }
        if system:
            params["system"] = system
        response = self._client.messages.create(**params)
        return LLMResponse(
            content=response.content[0].text,
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
        )
