from forge.llm.openai_provider import OpenAIProvider


def _mock_response(mocker, text, model, prompt_tokens, completion_tokens):
    response = mocker.MagicMock()
    response.choices = [mocker.MagicMock(message=mocker.MagicMock(content=text))]
    response.model = model
    response.usage.prompt_tokens = prompt_tokens
    response.usage.completion_tokens = completion_tokens
    return response


def test_generate_without_images_sends_plain_string_content(monkeypatch, mocker):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    mock_client = mocker.patch("openai.OpenAI").return_value
    mock_client.chat.completions.create.return_value = _mock_response(mocker, "hello", "gpt-4o-mini", 10, 5)

    provider = OpenAIProvider()
    result = provider.generate("hi there")

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["messages"] == [{"role": "user", "content": "hi there"}]
    assert result.content == "hello"
    assert result.input_tokens == 10
    assert result.output_tokens == 5


def test_generate_with_images_sends_image_url_blocks(monkeypatch, mocker):
    monkeypatch.setenv("OPENAI_API_KEY", "fake-key")
    mock_client = mocker.patch("openai.OpenAI").return_value
    mock_client.chat.completions.create.return_value = _mock_response(mocker, "a description", "gpt-4o-mini", 20, 8)

    provider = OpenAIProvider()
    result = provider.generate("describe this", images=[b"fakepngbytes"])

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    content = call_kwargs["messages"][0]["content"]
    assert content[0] == {"type": "text", "text": "describe this"}
    assert content[1]["type"] == "image_url"
    assert content[1]["image_url"]["url"].startswith("data:image/png;base64,")
    assert result.content == "a description"
