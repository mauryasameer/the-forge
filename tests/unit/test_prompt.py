from forge.llm.prompt import PromptTemplate


def test_render_basic():
    tpl = PromptTemplate("Hello, {name}!")
    assert tpl.render(name="Sameer") == "Hello, Sameer!"


def test_render_multiple_vars():
    tpl = PromptTemplate("Explain {topic} in {n} sentences.")
    assert tpl.render(topic="SMOTE", n=3) == "Explain SMOTE in 3 sentences."


def test_repr_truncates():
    tpl = PromptTemplate("A" * 100)
    assert "..." in repr(tpl)


def test_repr_short():
    tpl = PromptTemplate("Short template")
    assert "..." not in repr(tpl)
