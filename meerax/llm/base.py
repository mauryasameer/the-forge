from __future__ import annotations

import base64
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def encode_image(image: bytes) -> str:
    """Base64-encode raw image bytes (PNG) for embedding in a multimodal LLM request."""
    return base64.b64encode(image).decode()


class LLMProvider(ABC):
    """Abstract interface for all LLM backends.

    Concrete implementations live in claude.py, openai_provider.py, ollama.py.
    Swap providers by changing one constructor argument — no service code changes.
    """

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: str | None = None,
        images: list[bytes] | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Single-turn generation from a plain prompt string, optionally with images (raw PNG bytes)."""
        ...

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, Any]],
        system: str | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Multi-turn generation from an OpenAI-style message list."""
        ...
