# STATUS

promptv — local-first system-prompt versioner CLI
Built by Asdale Dynamics, LLC

## What was built

A Python CLI (`promptv`) that saves, lists, shows, diffs, and compares system-prompt
versions across configurable OpenAI-compatible endpoints (default Ollama). Versions are
stored locally as Markdown files with YAML-style frontmatter (name, version, created,
endpoint, model, sha256 digest). No API keys, no secrets, no network unless you
explicitly run `compare` against an endpoint you choose.

### Modules
- `promptv/config.py` — config.json loading/saving, default endpoint/model/data dir
- `promptv/store.py` — VersionStore: save, list, get, delete prompt versions as Markdown
- `promptv/client.py` — OpenAIClient: POST /v1/chat/completions to any compatible endpoint
- `promptv/diff.py` — unified diff of prompt text and endpoint responses
- `promptv/cli.py` — argparse CLI: init, config, save, list, show, diff, compare

### Commands
- `promptv init` — create config and data directories
- `promptv config [--show] [--endpoint URL] [--model NAME] [--data-dir PATH]`
- `promptv save NAME [--prompt TEXT | --file PATH] [--endpoint URL] [--model NAME]`
- `promptv list [NAME]`
- `promptv show NAME[@vN] [--version N]`
- `promptv diff A B`
- `promptv compare A B --endpoint URL --model MODEL [--message TEXT]`

### Packaging
- `pyproject.toml` with `promptv` console script entry point
- Install: `pip install .` (or `pip install -e .` for editable)
- Run: `python -m promptv` or `promptv --help`

## Tests

37 tests in `tests/`:
- `tests/test_store.py` — save, list, get, delete, frontmatter, digest, invalid names
- `tests/test_client.py` — mock endpoint chat, error handling, bad response shapes
- `tests/test_diff.py` — unified diff for identical/changed/added/removed text
- `tests/test_cli.py` — all CLI commands via a mock HTTP endpoint server

All tests use a local mock HTTP server; no network, no API keys.

### Verification results
- `pip install -e .` — success
- `pytest` — 37 passed, 0 failed
- End-to-end smoke test — init, save x2, list, diff all work correctly

## How to run

```bash
# Install
pip install .

# Initialize
promptv init

# Save a prompt version
promptv save my-bot --prompt "You are a helpful assistant."

# Save another version
promptv save my-bot --prompt "You are a helpful, concise assistant."

# List versions
promptv list my-bot

# Diff two versions
promptv diff my-bot@v1 my-bot@v2

# Compare two versions against an endpoint
promptv compare my-bot@v1 my-bot@v2 --endpoint http://localhost:11434/v1 --model llama3

# Run tests
pytest
```

## Known gaps
- No authentication support (API keys, bearer tokens) — by design; endpoints are expected to be local/trusted
- No `--output` flag to write diff/compare results to a file
- No prompt template or variable substitution
- No encryption of stored prompt files (local-first, filesystem permissions only)
- Data and config dirs default to `~/.local/share/promptv` and `~/.config/promptv`
- Only the OpenAI `chat/completions` endpoint shape is supported

## License
MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

## About
Asdale Dynamics, LLC (Indiana, formed October 2026), founded by Dylan Asdale — registered
nurse turned AI author. Beginner-friendly AI education, books, and practical local-first
tools. dylanasdale.github.io
