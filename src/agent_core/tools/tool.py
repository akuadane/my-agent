from enum import Enum
import inspect
from typing import Callable, Any

from src.agent_cli.policy import ask_tool_permission
from src.agent_core.context.context import Context
from src.agent_core.providers.base import BaseProvider
from src.agent_core.agent import Agent
from src.agent_core.prompts.prompts import MAIN_SYSTEM_PROMPT
from src.agent_core.prompts.composer import compose_prompt


class ToolPermission(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Tool:
    def __init__(self, function: Callable, permission: ToolPermission):
        self.name = function.__name__
        self.function = function
        self.permission = permission

    def execute(self, **kwargs) -> Any:
        return self.function(**kwargs)

    def to_json(self) -> dict:
        signature = inspect.signature(self.function)
        properties = {}
        required = []

        for name, parameter in signature.parameters.items():
            if parameter.kind in (
                inspect.Parameter.VAR_POSITIONAL,
                inspect.Parameter.VAR_KEYWORD,
            ):
                continue

            annotation = parameter.annotation
            json_type = "string"
            if annotation is int:
                json_type = "integer"
            elif annotation is float:
                json_type = "number"
            elif annotation is bool:
                json_type = "boolean"
            elif annotation is dict:
                json_type = "object"
            elif annotation is list:
                json_type = "array"

            properties[name] = {"type": json_type}

            if parameter.default is inspect.Parameter.empty:
                required.append(name)

        description = inspect.getdoc(self.function) or f"Call {self.name}"

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "required": required,
                    "properties": properties,
                },
            },
        }

class AgentManagerTool(Tool):
    def __init__(self, provider: BaseProvider, tools: list[Tool], ask_tool_permission: Callable[[str, dict], bool]):
        self.name = "addition_agent"
        self.provider = provider
        self.tools = tools
        self.permission = ToolPermission.LOW
        self.ask_tool_permission = ask_tool_permission

    def execute(self, prompt: str) -> Any:
        agent = Agent(name="General Agent", context=Context(compose_prompt([MAIN_SYSTEM_PROMPT,prompt])), provider=self.provider, tools=self.tools, ask_tool_permission= self.ask_tool_permission)
        print("In agent execute")
        return agent.run().get_messages()

    def to_json(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": "Creates new agents to accomplish addition tasks.",
                "parameters": {
                    "type": "object",
                    "required": ["prompt"],
                    "properties": {
                        "prompt": {
                            "type": "string",
                            "description": "Expression to be added. It can be an English statement.",
                        }
                    },
                },
            },
        }