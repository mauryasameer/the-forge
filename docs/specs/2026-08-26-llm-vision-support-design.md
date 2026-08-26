# forge.llm vision (multimodal) support

## Problem

`forge.llm.LLMProvider.generate()` is text-only — it cannot send an image to the model. This
blocks `PixelDrift` (a CycleGAN retrofit currently being brainstormed) from generating
translation-quality commentary that actually looks at sample image grids, and blocks any future
project wanting multimodal generation (captioning, visual QA, etc).

## Goals

- `generate()` accepts an optional `images` parameter across all three providers (Claude,
  OpenAI, Ollama), each encoding into its own wire format internally.
- Provider-agnostic input: raw image bytes (PNG), not a provider-specific type — mirrors
  `forge.vision.gridplot`'s numpy-based approach (mechanism-agnostic at the interface boundary).
- Fully backward compatible: `images` defaults to `None`, every existing call site (all of
  `forge`'s own tests, `TrendWhisperer`'s narrative service) behaves identically.

## Non-goals

- Non-PNG image formats. Every producer in this ecosystem (matplotlib `savefig`, forge.report's
  own `_fig_to_b64`) already emits PNG — no need to support JPEG/WEBP/etc until something
  actually needs it.
- Multi-turn multimodal `chat()`. `chat()`'s message-list API already lets a caller construct
  provider-specific multimodal messages by hand if truly needed; this spec only extends the
  common-case single-turn `generate()` path, which is what every current and anticipated caller
  (TrendWhisperer's narrative service, PixelDrift's forthcoming one) actually uses.
- Local/offline vision models beyond what Ollama already supports via its existing `model`
  constructor arg (e.g. `OllamaProvider(model="llava")`) — no new provider needed.

## Design

**`forge/llm/base.py`:**
- `LLMProvider.generate()`'s abstract signature gains `images: list[bytes] | None = None`.
- New helper: `encode_image(image: bytes) -> str` — `base64.b64encode(image).decode()`. Single
  source of truth, reused by all three providers instead of each reimplementing base64 encoding.

**`forge/llm/claude.py` (`ClaudeProvider.generate`):** when `images` is provided, builds Claude's
multimodal content-block format:
```python
content = [
    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": encode_image(img)}}
    for img in images
] + [{"type": "text", "text": prompt}]
```
and calls `self.chat([{"role": "user", "content": content}], system=system, **kwargs)` instead of
the current plain-string path.

**`forge/llm/openai_provider.py` (`OpenAIProvider.generate`):** builds OpenAI's `image_url`
data-URI format:
```python
content = [{"type": "text", "text": prompt}] + [
    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{encode_image(img)}"}}
    for img in images
]
```
same `chat()` delegation pattern.

**`forge/llm/ollama.py` (`OllamaProvider.generate`):** Ollama's chat API takes images as a
sibling `images` key (list of base64 strings) on the message dict, not embedded in `content`:
```python
message = {"role": "user", "content": prompt}
if images:
    message["images"] = [encode_image(img) for img in images]
```

All three: when `images` is `None` or empty, behavior is byte-for-byte identical to today (plain
string content, no new keys).

## Testing

None of the three providers (`ClaudeProvider`, `OpenAIProvider`, `OllamaProvider`) have any unit
tests today — only `LLMResponse` itself (`tests/unit/test_llm_base.py`) is tested, presumably
because the providers wrap real paid/networked SDK clients. This is the first time any of them
gets tested, establishing the convention rather than matching an existing one:

- `pytest-mock` (already a `dev` extra dependency) patches each SDK's client class
  (`mocker.patch("anthropic.Anthropic")`, `mocker.patch("openai.OpenAI")`, and the internal
  `ollama` module reference inside `OllamaProvider`) so no real network call happens.
- `monkeypatch.setenv("ANTHROPIC_API_KEY", "fake")` / `OPENAI_API_KEY` set before construction,
  since both constructors do `os.environ["...KEY"]` (raises `KeyError`, not `.get()`, if unset).
- Each mocked client returns a fake response object shaped like the real SDK's response (e.g.
  Claude: `.content[0].text`, `.model`, `.usage.input_tokens/.output_tokens`; OpenAI:
  `.choices[0].message.content`, `.model`, `.usage.prompt_tokens/.completion_tokens`).
- New test per provider: `generate(prompt, images=[b"<png bytes>"])` — assert the mocked
  client's create/chat call received the provider-correct image block shape (the exact dict/list
  structure this design section specifies).
- Second test per provider: `generate(prompt)` with no `images` — assert the call shape is
  identical to what it would have been before this change (plain string/dict content, no image
  keys) — the regression guard for backward compatibility.
- `OllamaProvider` test mocks `self._ollama.chat` (the lazily-imported `ollama` module
  reference stored on the instance) rather than patching a module-level import.

## Versioning

MINOR bump: `0.4.0` → `0.5.0` (additive, backward compatible, no existing caller's behavior
changes).
