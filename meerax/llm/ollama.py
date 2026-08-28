from __future__ import annotations

from typing import Any

from meerax.llm.base import LLMProvider, LLMResponse, encode_image


class OllamaProvider(LLMProvider):
    """Local Ollama backend. No API key required — needs Ollama running on localhost."""

    DEFAULT_MODEL = "llama3.2"

    def __init__(self, model: str = DEFAULT_MODEL, host: str = "http://localhost:11434") -> None:
        try:
            import ollama as _ollama
            self._ollama = _ollama
        except ImportError as exc:
            raise ImportError("Install ollama: pip install ollama") from exc
        self._model = model
        self._host = host

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
        user_message: dict[str, Any] = {"role": "user", "content": prompt}
        if images:
            user_message["images"] = [encode_image(img) for img in images]
        messages.append(user_message)
        return self.chat(messages, **kwargs)

    def chat(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        if system and not any(m["role"] == "system" for m in messages):
            messages = [{"role": "system", "content": system}, *messages]
        response = self._ollama.chat(
            model=kwargs.get("model", self._model),
            messages=messages,
        )
        msg = response["message"]
        return LLMResponse(
            content=msg["content"],
            model=self._model,
            input_tokens=response.get("prompt_eval_count", 0),
            output_tokens=response.get("eval_count", 0),
        )
