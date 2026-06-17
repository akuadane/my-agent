# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python agentic AI framework for building autonomous agents that use LLMs for decision-making, execute tools, manage permissions, and compose into hierarchical sub-agent networks.

## Environment & Commands

This project uses [Pixi](https://pixi.sh) for environment/dependency management (not pip or poetry).

```bash
pixi install          # Install dependencies (includes editable install of agentlib)
pixi run format       # Format with ruff
pixi run lint         # Lint with ruff
pixi run pytest       # Run tests
```

**Running examples** (requires a running Ollama instance with `gemma4:e2b` or similar):
```bash
pixi run python examples/basic_agent.py    # Basic agent with file/math tools
pixi run python examples/sub_agents.py     # Main agent spawning sub-agents
pixi run python examples/tic_tac_toe.py    # Tic-tac-toe game
```

## Architecture

The package is `agentlib`, installed as an editable package via `pyproject.toml`. Import root: `from agentlib import ...`

### Core Components

**`src/agentlib/core/`** — The engine
- [agent.py](src/agentlib/core/agent.py) — `Agent` class: ties together context, provider, tools, and permission callback; `agent.run()` returns the final string response
- [loop.py](src/agentlib/core/loop.py) — `run_agent()` generator that drives the agentic loop: call provider → extract tool calls → execute → add results to context → repeat until no tool calls remain
- [context.py](src/agentlib/core/context.py) — Conversation history (system prompt + messages)
- [prompts/](src/agentlib/core/prompts/) — `prompts.py` (system prompt constants) and `composer.py` (prompt concatenation)

**`src/agentlib/providers/`** — LLM backends (primary extension point)
- [base.py](src/agentlib/providers/base.py) — `BaseProvider` ABC, `AssistantMessage`, `ToolResultMessage`
- [ollama.py](src/agentlib/providers/ollama.py) — `OllamaProvider`: the only fully implemented provider
- `anthropic.py`, `openai.py`, `local.py` — empty stubs

**`src/agentlib/tools/`** — Tool framework + builtins
- [tool.py](src/agentlib/tools/tool.py) — `Tool` wraps a Python function with name/description/permission level; introspects function signature to build JSON schema; `AgentManagerTool` wraps a sub-agent as a tool
- [executor.py](src/agentlib/tools/executor.py) — `sequential_executor` and `parallel_executor` for running tool calls
- [builtin/basic.py](src/agentlib/tools/builtin/basic.py) — `add_numbers`, `list_directory`, `read_file`

**`src/agentlib/cli/`** — CLI layer
- [policy.py](src/agentlib/cli/policy.py) — `ask_tool_permission_cli()`: prompts the user in the terminal for HIGH permission tools

**`examples/`** — Runnable demos (not shipped in the package)

**`tests/`** — Mirrors the package layout: `tests/core/`, `tests/providers/`, `tests/tools/`, `tests/cli/`

### Data Flow

```
User input
  → Context (conversation history)
  → Provider.generate(messages, tools)  [streams AssistantMessages]
  → Tool calls extracted → executor → ask_tool_permission() → ToolResultMessage
  → Appended to Context → repeat until no tool calls
  → Final response returned as str
```

### Tool Permission Levels

Tools declare a `ToolPermission` (LOW, MEDIUM, HIGH). The `ask_tool_permission` callback (injected at construction time) decides whether to auto-approve or prompt the user. This allows the same agent engine to work in both interactive CLI and headless contexts.

### Sub-Agents

`AgentManagerTool` wraps a child `Agent` as a callable tool. The parent agent can invoke child agents by name; only the child's final string response is returned to the parent, keeping the parent's context clean.

### Provider Abstraction

`BaseProvider` defines the interface; `OllamaProvider` is the only complete implementation. `OpenAIProvider`, `AnthropicProvider`, and `LocalProvider` are empty stubs in `src/agentlib/providers/`.
