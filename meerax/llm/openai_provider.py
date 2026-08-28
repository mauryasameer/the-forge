from __future__ import annotations

import os
from typing import Any

from meerax.llm.base import LLMProvider, LLMResponse, encode_image


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

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        images: list[bytes] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        messages: list[dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        if images:
            content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
            content.extend(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(img)}"}}
                for img in images
            )
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": prompt})
        return self.chat(messages, **kwargs)

    def chat(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        if system and not any(m["role"] == "system" for m in messages):
            messages = [{"role": "system", "content": system}, *messages]
        response = self._client.chat.completions.create(
            model=kwargs.get("model", self._model),
            max_tokens=kwargs.get("max_tokens", self._max_tokens),
            messages=messages,  # type: ignore[arg-type]
        )
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
        )
