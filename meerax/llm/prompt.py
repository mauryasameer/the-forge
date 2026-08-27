from __future__ import annotations


class PromptTemplate:
    """Lightweight string template for LLM prompts.

    Usage::

        tpl = PromptTemplate("Explain {topic} in {n} sentences.")
        prompt = tpl.render(topic="SMOTE", n=3)
    """

    def __init__(self, template: str) -> None:
        self._template = template

    def render(self, **kwargs: object) -> str:
        return self._template.format(**kwargs)

    def __repr__(self) -> str:
        preview = self._template[:60].replace("\n", " ")
        return f"PromptTemplate('{preview}{'...' if len(self._template) > 60 else ''}')"
