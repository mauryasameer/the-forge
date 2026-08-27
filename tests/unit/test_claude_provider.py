from meerax.llm.claude import ClaudeProvider


def _mock_response(mocker, text, model, input_tokens, output_tokens):
    response = mocker.MagicMock()
    response.content = [mocker.MagicMock(text=text)]
    response.model = model
    response.usage.input_tokens = input_tokens
    response.usage.output_tokens = output_tokens
    return response


def test_generate_without_images_sends_plain_string_content(monkeypatch, mocker):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    mock_client = mocker.patch("anthropic.Anthropic").return_value
    mock_client.messages.create.return_value = _mock_response(mocker, "hello", "claude-sonnet-4-6", 10, 5)

    provider = ClaudeProvider()
    result = provider.generate("hi there")

    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["messages"] == [{"role": "user", "content": "hi there"}]
    assert result.content == "hello"
    assert result.input_tokens == 10
    assert result.output_tokens == 5


def test_generate_with_images_sends_content_blocks(monkeypatch, mocker):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key")
    mock_client = mocker.patch("anthropic.Anthropic").return_value
    mock_client.messages.create.return_value = _mock_response(mocker, "a description", "claude-sonnet-4-6", 20, 8)

    provider = ClaudeProvider()
    result = provider.generate("describe this", images=[b"fakepngbytes"])

    call_kwargs = mock_client.messages.create.call_args.kwargs
    content = call_kwargs["messages"][0]["content"]
    assert content[0]["type"] == "image"
    assert content[0]["source"]["type"] == "base64"
    assert content[0]["source"]["media_type"] == "image/png"
    assert content[1] == {"type": "text", "text": "describe this"}
    assert result.content == "a description"
