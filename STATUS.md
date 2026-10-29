# STATUS

promptv — local-first system-prompt versioner CLI
Built by Asdale Dynamics, LLC

## What was built

A Python CLI (`promptv`) that saves, lists, shows, diffs, deletes, and compares
system-prompt versions across configurable OpenAI-compatible endpoints (default
Ollama). Versions are stored locally as Markdown files with YAML-style frontmatter
(name, version, created, endpoint, model, sha256 digest). No API keys, no secrets,
no network unless you explicitly run `compare` against an endpoint you choose.
Local-first by design.

### Modules
- `promptv/config.py` — config.json loading/saving; default endpoint/model/data dir,
  with env var overrides (`PROMPTV_DEFAULT_ENDPOINT`, `PROMPTV_DEFAULT_MODEL`,
  `PROMPTV_CONFIG_DIR`, `PROMPTV_DATA_DIR`)
- `promptv/store.py` — VersionStore: save, list, get, delete prompt versions as
  Markdown with frontmatter and sha256 content digest
- `promptv/client.py` — OpenAIClient: POST /v1/chat/completions to any compatible
  endpoint using only the standard library (urllib)
- `promptv/diff.py` — unified diff of prompt text and endpoint responses
- `promptv/cli.py` — argparse CLI: init, config, save, list, show, delete, diff, compare

### Commands
| Command | Purpose |
|---------|---------|
| `init` | Create default config and data directories |
| `config [--show] [--endpoint URL] [--model NAME] [--data-dir PATH]` | View/modify configuration |
| `save NAME [--prompt TEXT \| --file PATH] [--endpoint URL] [--model NAME]` | Save a new prompt version |
| `list [NAME]` | List saved versions |
| `show NAME[@vN] [--version N]` | Show a prompt version |
| `delete NAME[@vN] [--version N]` | Delete a saved version |
| `diff A B` | Diff two prompt versions |
| `compare A B [--endpoint URL] [--model MODEL] [--message TEXT]` | Compare two versions via an endpoint |

`--endpoint` and `--model` on `save` and `compare` are optional and fall back to
configured defaults (Ollama by default).

### Packaging
- `pyproject.toml` with `promptv` console script entry point
- Install: `pip install .` (or `pip install -e .` for editable)
- Run: `python -m promptv` or `promptv --help`

### What each saved file looks like
```markdown
---
name: my-bot
version: 2
created: 2026-10-29T14:00:00Z
endpoint: http://localhost:11434/v1
model: llama3
digest: sha256:abc123...
---
You are a friendly, concise assistant.
```

## Tests

41 tests in `tests/`:
- `tests/test_store.py` — save, list, get, delete, frontmatter, digest, invalid names
- `tests/test_client.py` — mock endpoint chat, error handling, bad response shapes
- `tests/test_diff.py` — unified diff for identical/changed/added/removed text
- `tests/test_cli.py` — all CLI commands via a local mock HTTP server, including
  `delete` and `compare` with config defaults

Tests use a local mock HTTP server; no network, no API keys.

### Verification results
- `pip install -e .` — success (builds and installs cleanly)
- `pytest` — 41 passed, 0 failed
- End-to-end smoke test — init, save x2, list, diff, delete v1, list again all work
  correctly; `compare` works with both explicit endpoint/model and config defaults

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

# Show a version
promptv show my-bot@v1

# Diff two versions
promptv diff my-bot@v1 my-bot@v2

# Compare two versions against an endpoint
promptv compare my-bot@v1 my-bot@v2 --endpoint http://localhost:11434/v1 --model llama3

# Compare using configured defaults
promptv compare my-bot@v1 my-bot@v2

# Delete a version
promptv delete my-bot@v1

# Run tests
pytest
```

## Known gaps
- No authentication support (API keys, bearer tokens) — by design; endpoints are
  expected to be local/trusted. `promptv` does not store or manage keys.
- No `--output` flag to write diff/compare results to a file
- No prompt template or variable substitution
- No encryption of stored prompt files (local-first, filesystem permissions only)
- Data and config dirs default to `~/.local/share/promptv` and `~/.config/promptv`
- Only the OpenAI `chat/completions` endpoint shape is supported
- No streaming response support

## License
MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

## About
Asdale Dynamics, LLC (Indiana, formed October 2026), founded by Dylan Asdale — registered
nurse turned AI author. Beginner-friendly AI education, books, and practical local-first
tools. dylanasdale.github.io
