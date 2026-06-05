# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python agentic AI framework for building autonomous agents that use LLMs for decision-making, execute tools, manage permissions, and compose into hierarchical sub-agent networks.

## Environment & Commands

This project uses [Pixi](https://pixi.sh) for environment/dependency management (not pip or poetry).

```bash
pixi install          # Install dependencies
pixi run format       # Format with ruff
pixi run lint         # Lint with ruff
pixi run pytest       # Run tests (if configured)
```

**Running examples** (requires a running Ollama instance with `gemma4:e2b` or similar):
```bash
pixi run python -m src.agent_cli.examples.main        # Basic agent with file/math tools
pixi run python -m src.agent_cli.examples.sub_agents  # Main agent spawning sub-agents
pixi run python -m src.agent_cli.examples.ttt         # Tic-tac-toe game
```

## Architecture

### Core Components

**`src/agent_core/`** — The engine
- [agent.py](src/agent_core/agent.py) — `Agent` class: ties together context, provider, tools, and permission callback; `agent.run()` returns the final string response
- [main_loop.py](src/agent_core/main_loop.py) — `run_agent()` generator that drives the agentic loop: call provider → extract tool calls → execute → add results to context → repeat until no tool calls remain
- [context/context.py](src/agent_core/context/context.py) — Conversation history (system prompt + messages)
- [providers/base.py](src/agent_core/providers/base.py) — `BaseProvider` ABC, `AssistantMessage`, `ToolResultMessage`; only `OllamaProvider` is fully implemented
- [tools/tool.py](src/agent_core/tools/tool.py) — `Tool` wraps a Python function with name/description/permission level; introspects function signature to build JSON schema; `AgentManagerTool` wraps a sub-agent as a tool
- [tools/executor.py](src/agent_core/tools/executor.py) — `sequential_executor` and `parallel_executor` for running tool calls

**`src/agent_cli/`** — CLI layer
- [policy.py](src/agent_cli/policy.py) — `ask_tool_permission()`: prompts the user in the terminal for HIGH/MEDIUM permission tools

**`src/agent_tools/`** — Concrete tool implementations
- [tools.py](src/agent_tools/tools.py) — `add_numbers`, `list_directory`, `read_file`

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

Tools declare a `PermissionLevel` (LOW, MEDIUM, HIGH). The `ask_tool_permission` callback (injected at construction time) decides whether to auto-approve or prompt the user. This allows the same agent engine to work in both interactive CLI and headless contexts.

### Sub-Agents

`AgentManagerTool` wraps a child `Agent` as a callable tool. The parent agent can invoke child agents by name; only the child's final string response is returned to the parent, keeping the parent's context clean.

### Provider Abstraction

`BaseProvider` defines the interface; `OllamaProvider` is the only complete implementation. `OpenAIProvider`, `AnthropicProvider`, and `LocalProvider` are empty stubs.
