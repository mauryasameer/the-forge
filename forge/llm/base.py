from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class LLMProvider(ABC):
    """Abstract interface for all LLM backends.

    Concrete implementations live in claude.py, openai_provider.py, ollama.py.
    Swap providers by changing one constructor argument — no service code changes.
    """

    @abstractmethod
    def generate(self, prompt: str, system: str | None = None, **kwargs) -> LLMResponse:
        """Single-turn generation from a plain prompt string."""
        ...

    @abstractmethod
    def chat(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        **kwargs,
    ) -> LLMResponse:
        """Multi-turn generation from an OpenAI-style message list."""
        ...
