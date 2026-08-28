# Security

## API keys

Every LLM provider in `meerax.llm` (`ClaudeProvider`, `OpenAIProvider`, `OllamaProvider`) reads
its credential from an environment variable — `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` — or an
explicit `api_key` constructor argument. None of them, or any app built on them, should ever
have a key hardcoded in source, a config file, or a committed `.env`.

- Keys live in the shell environment or a local, gitignored `.env` — never in a file tracked by
  git.
- If a key is ever accidentally committed, treat it as compromised: rotate it at the provider
  immediately (it's cheaper than trying to prove it wasn't accessed), then remove it from git
  history.
- Rotate keys on a normal cadence even without an incident — quarterly is reasonable for a
  single-maintainer ecosystem like this one.
- CI never has these keys: every LLM-dependent test across this ecosystem mocks the provider's
  client rather than making a real API call, so no repo's CI needs a real credential to pass.

## Dependency updates

Dependabot (`.github/dependabot.yml`, present in every repo including scaffolded ones) opens a
PR for outdated pins weekly. Patch/minor bumps to libraries with real (non-mocked) test coverage
can generally be merged once CI is green. Major version bumps to an SDK whose client is mocked in
tests (the LLM providers, most notably) need a manual look before merging — green CI on a mocked
client doesn't prove the real SDK's interface still matches.

## Reporting

This is a personal/organizational ecosystem, not a public open-source project accepting outside
reports. If you find an issue in a repo you have access to, open an issue or reach Sameer Maurya
directly.
