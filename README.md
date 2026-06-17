# my-agent

A lightweight Python framework for building autonomous AI agents that reason with LLMs, call tools, manage permissions, and compose into hierarchical agent networks.

## Features

- **Streaming agentic loop** — LLM responses stream in real time; tool calls are extracted, executed, and fed back automatically until the task is complete
- **Tool permission system** — tools declare a permission level (`LOW`, `MEDIUM`, `HIGH`); the framework prompts the user before executing sensitive tools
- **Sub-agent composition** — wrap any agent as a tool so a parent agent can delegate sub-tasks to specialized child agents
- **Pluggable providers** — swap the underlying LLM (Ollama implemented; OpenAI and Anthropic stubs ready)

## Prerequisites

- [Pixi](https://pixi.sh) — handles the Python environment and dependencies
- [Ollama](https://ollama.com) running locally with a model pulled (examples default to `gemma4:e2b`)

```bash
ollama pull gemma4:e2b
```

## Setup

```bash
git clone https://github.com/akuadane/my-agent
cd my-agent
pixi install
pixi run setup
```

## Running the examples

**Basic agent** — interactive REPL with file and math tools:
```bash
pixi run python -m src.agent_cli.examples.main
```

**Sub-agent example** — main agent that spawns a child agent for arithmetic:
```bash
pixi run python -m src.agent_cli.examples.sub_agents
```

**Tic-tac-toe** — two LLM agents play each other:
```bash
pixi run python -m src.agent_cli.examples.ttt
```

Type `exit`, `quit`, or `q` to leave the interactive examples.

## Building your own agent

```python
from src.agent_core.agent import Agent
from src.agent_core.context.context import Context
from src.agent_core.providers.ollama_provider import OllamaProvider
from src.agent_core.tools.tool import Tool, ToolPermission

# 1. Wrap your functions as Tools
def my_tool(x: int, y: int) -> int:
    """Adds two numbers."""
    return x + y

tool = Tool(function=my_tool, permission=ToolPermission.LOW)

# 2. Build an agent
agent = Agent(
    name="my-agent",
    context=Context("You are a helpful assistant."),
    provider=OllamaProvider(model="gemma4:e2b"),
    tools=[tool],
    ask_tool_permission=lambda name, args: True,  # auto-approve
)

# 3. Run it — returns the final response string
result = agent.run()
```

### Tool permissions

| Level | Behavior |
|-------|----------|
| `LOW` | Auto-approved |
| `MEDIUM` | Prompts the user |
| `HIGH` | Prompts the user |

Override the `ask_tool_permission` callback to implement custom approval logic (e.g., deny all HIGH-risk tools in automated pipelines).

### Sub-agents

```python
from src.agent_core.tools.tool import AgentManagerTool

sub_agent_tool = AgentManagerTool(
    provider=provider,
    tools=[tool_a, tool_b],
    ask_tool_permission=ask_tool_permission,
)

# Pass sub_agent_tool to a parent agent like any other tool
```

Only the child agent's final response is returned to the parent — the child's internal reasoning and tool calls stay isolated.

## Development

```bash
pixi run format   # ruff format
pixi run lint     # ruff check
pixi run pytest   # run tests
```
