# Turtle

Turtle is a local terminal assistant CLI that can **either explain** terminal concepts or **run commands for you** (with a safety confirmation prompt) using a tool-calling agent backed by Ollama.

---

## Features

- **Two modes**
  - **Explain Mode**: short, terminal-friendly explanations with optional example commands
  - **Action Mode**: proposes terminal commands and executes them **only after y/n confirmation**
- **Tool-calling command execution**
  - Uses a strict `run_terminal` tool schema for structured command requests
- **Safer by design**
  - Commands are shown before execution
  - User must confirm before anything runs
- **Works great for common shell workflows**
  - File/folder operations (create/move/rename/delete)
  - Searching and listing
  - Inspecting files and directories

---

## Tech Stack

- **Python** (CLI + agent)
- **Ollama** (local LLM runtime)
- **Qwen 2.5 3B** (`qwen2.5:3b`) (default model)
- **Rich** (terminal UI panels, styled output)

---

## Getting Started

### 1) Prerequisites

- macOS (or Linux) terminal
- Python 3.x
- Ollama installed and running

Pull the model:

```
ollama pull qwen2.5:3b
```

### 2) Install dependencies

From the repo root:

```
pip install -U pip
pip install ollama rich
```

### 3) Install Turtle as a CLI (recommended: pipx)

This makes the `turtle` command available globally without activating a venv:

```
brew install pipx
pipx ensurepath

cd /path/to/qhacks-cli-agent
pipx install -e .
```

Restart your terminal (or run `exec zsh -l`), then:

```
turtle
```

### 4) Run locally (editable install)

If you prefer running with a local environment:

```
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
turtle
```

---

## Usage

Start Turtle:

```
turtle
```

- Type your request at the prompt.
- If Turtle proposes a command, you’ll be asked to confirm with `y/n` before it executes.
- Type `exit` or `quit` to leave.

---

## Notes

- On macOS, some folders (e.g. **Downloads**, **Desktop**, **Documents**) may require enabling **Terminal / VS Code** in:
  - **System Settings → Privacy & Security → Files and Folders** (or **Full Disk Access**)
  - Otherwise commands like `find` may show `Operation not permitted`.

---

## Project Structure

- `terminal_worker/worker.py` — main CLI agent loop + prompts + command execution
- `terminal_worker/tool_schema.py` — strict tool schema for `run_terminal`
- `pyproject.toml` — packaging + CLI entrypoint (`turtle`)

---

## License

Add your license here (e.g. MIT).