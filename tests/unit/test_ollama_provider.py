from forge.llm.ollama import OllamaProvider


def test_generate_without_images_sends_plain_content(mocker):
    provider = OllamaProvider()
    provider._ollama = mocker.MagicMock()
    provider._ollama.chat.return_value = {
        "message": {"content": "hi"},
        "prompt_eval_count": 3,
        "eval_count": 2,
    }

    result = provider.generate("hello")

    call_kwargs = provider._ollama.chat.call_args.kwargs
    assert call_kwargs["messages"] == [{"role": "user", "content": "hello"}]
    assert "images" not in call_kwargs["messages"][0]
    assert result.content == "hi"


def test_generate_with_images_attaches_images_key(mocker):
    provider = OllamaProvider(model="llava")
    provider._ollama = mocker.MagicMock()
    provider._ollama.chat.return_value = {
        "message": {"content": "a cat"},
        "prompt_eval_count": 5,
        "eval_count": 4,
    }

    result = provider.generate("what is this", images=[b"fakepng"])

    call_kwargs = provider._ollama.chat.call_args.kwargs
    message = call_kwargs["messages"][0]
    assert message["content"] == "what is this"
    assert isinstance(message["images"][0], str)
    assert result.content == "a cat"
