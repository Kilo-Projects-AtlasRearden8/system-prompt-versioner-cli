# promptv

Save, diff, and compare system-prompt versions across configurable OpenAI-compatible
endpoints (default Ollama). Stored locally as Markdown, with no API keys required.

**Built by Asdale Dynamics, LLC** — beginner-friendly AI education, books, and practical
local-first tools.

---

## What this does

`promptv` lets you version your system prompts the same way you version code:

- **Save** a prompt as a new version, stamped with endpoint, model, date, and content hash.
- **List** all saved versions for one prompt or every prompt.
- **Show** the text of any saved version.
- **Diff** any two versions side by side.
- **Compare** two versions by sending both to an endpoint and diffing the responses.

Everything lives on your machine. Nothing is sent anywhere unless you explicitly run
`compare` against an endpoint you choose. No secrets, no API keys, no cloud.

---

## Install

```bash
pip install .
```

Or run directly from source:

```bash
python -m promptv --help
```

---

## Quick start

Initialize the config and data directories:

```bash
promptv init
```

Save your first prompt version:

```bash
promptv save my-bot --prompt "You are a friendly assistant."
```

Save another version:

```bash
promptv save my-bot --prompt "You are a friendly, concise assistant."
```

List saved versions:

```bash
promptv list
```

Show the latest version:

```bash
promptv show my-bot
```

Show a specific version:

```bash
promptv show my-bot@v1
```

Diff two versions:

```bash
promptv diff my-bot@v1 my-bot@v2
```

Compare two versions against an endpoint (default Ollama):

```bash
promptv compare my-bot@v1 my-bot@v2 --endpoint http://localhost:11434/v1 --model llama3
```

Read a prompt from a file:

```bash
promptv save my-bot --file my-prompt.txt
```

View or change configuration:

```bash
promptv config --show
promptv config --endpoint http://custom:1234/v1 --model my-model
```

---

## Configuration

`promptv init` creates:

- `~/.config/promptv/config.json` — default endpoint, model, and data directory
- `~/.local/share/promptv/versions/<name>/vNNN.md` — one Markdown file per version

Each saved file has a YAML-style frontmatter block:

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

Override locations with environment variables:

- `PROMPTV_CONFIG_DIR`
- `PROMPTV_DATA_DIR`

---

## Commands

| Command | Purpose |
|---------|---------|
| `init` | Create default config and data directories |
| `config` | View or modify configuration |
| `save NAME` | Save a new prompt version |
| `list [NAME]` | List saved versions |
| `show NAME[@vN]` | Show a prompt version |
| `diff A B` | Diff two prompt versions |
| `compare A B --endpoint URL --model MODEL` | Compare two versions via an endpoint |

Use `promptv <command> --help` for details on any command.

---

## Endpoints

`promptv` works with any OpenAI-compatible chat endpoint, including:

- **Ollama** (default): `http://localhost:11434/v1`
- **vLLM**, **LM Studio**, **Text Generation WebUI**, and similar

The default endpoint comes from `config.json` or `PROMPTV_DEFAULT_ENDPOINT`. No API keys are ever needed.

---

## Tests

```bash
pip install pytest
pytest
```

Tests use a local mock HTTP server, so no network or API key is required.

---

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

---

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC (Indiana, formed October 2026) is founded by Dylan Asdale, a registered
nurse turned AI author. The LLC publishes beginner-friendly AI education, books and guides,
and practical local-first tools. Dylan's book *The Massive AI Manual* and hub site
dylanasdale.github.io explain AI "like a friend would": plain English, step by step, never
condescending.

This tool is one of the LLC's open-source local-LLM utilities, built to be clear, warm,
polished, tested, and local-first.
