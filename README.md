# promptv

Save, diff, and compare system-prompt versions across OpenAI-compatible endpoints
(default Ollama). Stored locally as Markdown. No API keys required.

**Built by Asdale Dynamics, LLC** — beginner-friendly AI education, books, and
practical local-first tools.

---

## What this tool is for

If you work with AI — whether you're writing, coding, or just exploring — you
probably spend time tweaking the "system prompt" that tells an AI how to behave.
It's the behind-the-scenes instruction that shapes the AI's tone, style, and
boundaries.

The trouble is, system prompts are easy to lose track of. You try one version,
then another, then wonder: "Which one worked better?" or "What did I change?"

`promptv` fixes that. It lets you:

- **Save** each version of a system prompt, stamped with the date, endpoint,
  model, and a content hash
- **List** all your saved versions, organized by prompt name
- **Show** the exact text of any saved version
- **Diff** two versions side by side, so you can see exactly what changed
- **Compare** two versions by sending both to an AI endpoint and diffing the
  responses, so you can see which version gets a better answer

Everything stays on your own computer. Nothing is uploaded. No API keys, no
secrets, no cloud accounts. It's local-first by design.

---

## Install

```bash
pip install .
```

Or run directly from source without installing:

```bash
python -m promptv --help
```

Once installed, the `promptv` command is available everywhere.

---

## Quick start, step by step

### 1. Set it up

```bash
promptv init
```

This creates a config file and a folder where your prompt versions will live.
By default:

- Config: `~/.config/promptv/config.json`
- Prompt versions: `~/.local/share/promptv/versions/`

You can change these locations later with environment variables
(`PROMPTV_CONFIG_DIR`, `PROMPTV_DATA_DIR`) or the `config` command.

### 2. Save your first prompt version

```bash
promptv save writing-assistant --prompt "You are a helpful, friendly writing assistant."
```

You'll see something like:

```
Saved writing-assistant v001 to /home/you/.local/share/promptv/versions/writing-assistant/v001.md
```

Each version gets its own Markdown file, numbered `v001`, `v002`, and so on.

### 3. Save a second version

```bash
promptv save writing-assistant --prompt "You are a helpful, friendly, and concise writing assistant."
```

Now you have two versions: `v001` and `v002`.

### 4. List your saved versions

```bash
promptv list writing-assistant
```

```
writing-assistant:
  v001  2026-10-29T10:00:00Z  http://localhost:11434/v1
  v002  2026-10-29T10:05:00Z  http://localhost:11434/v1
```

### 5. See the text of a version

Show the latest:

```bash
promptv show writing-assistant
```

Show a specific version:

```bash
promptv show writing-assistant@v1
```

Or use the shorthand:

```bash
promptv show writing-assistant@v2
```

### 6. See what changed between two versions

```bash
promptv diff writing-assistant@v1 writing-assistant@v2
```

You'll get a unified diff showing exactly what was added or removed.

### 7. Compare two versions against an AI endpoint

Send both versions to an endpoint (like Ollama) and see which one gives a
better answer:

```bash
promptv compare writing-assistant@v1 writing-assistant@v2 \
  --endpoint http://localhost:11434/v1 \
  --model llama3
```

If you've already set a default endpoint and model with `config`, you can leave
off `--endpoint` and `--model`:

```bash
promptv compare writing-assistant@v1 writing-assistant@v2
```

The output shows each version's response, then a diff between the two
responses.

---

## Commands at a glance

| Command | What it does |
|---------|-------------|
| `init` | Create the config folder and data folder |
| `config` | View or change default endpoint, model, and data folder |
| `save NAME` | Save a new version of a prompt |
| `list [NAME]` | List saved versions (all prompts, or one by name) |
| `show NAME[@vN]` | Show the text of a saved version |
| `diff A B` | Show the difference between two prompt versions |
| `compare A B` | Send two versions to an endpoint and compare responses |
| `delete NAME[@vN]` | Delete a saved version |

Use `promptv <command> --help` for details on any command.

---

## Configuration

`promptv init` writes a `config.json` file. Here's an example:

```json
{
  "default_endpoint": "http://localhost:11434/v1",
  "default_model": "llama3",
  "data_dir": "/home/you/.local/share/promptv"
}
```

Change it anytime:

```bash
promptv config --endpoint http://localhost:11434/v1 --model llama3
promptv config --show
```

You can also override folder locations with environment variables:

- `PROMPTV_CONFIG_DIR` — where `config.json` lives
- `PROMPTV_DATA_DIR` — where prompt versions are stored
- `PROMPTV_DEFAULT_ENDPOINT` — default endpoint (e.g. Ollama)
- `PROMPTV_DEFAULT_MODEL` — default model name

---

## What a saved prompt looks like

Each version is a Markdown file with a small header (called frontmatter) and the
prompt text underneath:

```markdown
---
name: writing-assistant
version: 2
created: 2026-10-29T10:05:00Z
endpoint: http://localhost:11434/v1
model: llama3
digest: sha256:a1b2c3d4...
---
You are a helpful, friendly, and concise writing assistant.
```

The `digest` is a sha256 hash of the prompt text, so you can verify a file
hasn't been changed since it was saved.

---

## Endpoints

`promptv` works with any OpenAI-compatible chat endpoint, including:

- **Ollama** (the default): `http://localhost:11434/v1`
- **vLLM**, **LM Studio**, **Text Generation WebUI**, and similar

No API keys are needed for local endpoints. If you use a remote endpoint that
requires authentication, `promptv` does not store or manage keys — it simply
sends the request you ask it to.

---

## Tests

```bash
pip install pytest
pytest
```

All tests run against a local mock server — no network, no API keys needed.

---

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

---

## About Asdale Dynamics, LLC

Asdale Dynamics, LLC (Indiana, formed October 2026) is founded by Dylan Asdale,
a registered nurse turned AI author. The LLC publishes beginner-friendly AI
education, books and guides, and practical local-first tools. Dylan's book
*The Massive AI Manual* and hub site dylanasdale.github.io explain AI "like a
friend would": plain English, step by step, never condescending.

This tool is one of the LLC's open-source local-LLM utilities. It's built to be
clear, warm, polished, tested, and local-first — something you can trust on your
own machine, with nothing phoning home.
