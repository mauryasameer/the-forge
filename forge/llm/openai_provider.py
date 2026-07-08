from __future__ import annotations

import os

from forge.llm.base import LLMProvider, LLMResponse


class OpenAIProvider(LLMProvider):
    """OpenAI backend (GPT-4o, GPT-4o-mini, etc.).

    Requires OPENAI_API_KEY env var or explicit api_key argument.
    """

    DEFAULT_MODEL = "gpt-4o-mini"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 2048,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ImportError("Install openai: pip install openai") from exc
        self._client = OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])
        self._model = model
        self._max_tokens = max_tokens

    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, **kwargs)

    def chat(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        if system and not any(m["role"] == "system" for m in messages):
            messages = [{"role": "system", "content": system}, *messages]
        response = self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            max_tokens=kwargs.get("max_tokens", self._max_tokens),
            messages=messages,
        )
        choice = response.choices[0]
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
        )
