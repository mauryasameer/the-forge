from meerax.llm.base import LLMResponse


def test_total_tokens():
    r = LLMResponse(content="hi", model="test", input_tokens=10, output_tokens=5)
    assert r.total_tokens == 15


def test_content():
    r = LLMResponse(content="hello world", model="m", input_tokens=0, output_tokens=0)
    assert r.content == "hello world"
