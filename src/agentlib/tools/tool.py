import inspect
from abc import ABC
from enum import Enum
from typing import Any, Callable

from agentlib.core.agent import Agent
from agentlib.core.context import Context
from agentlib.core.prompts.composer import compose_prompt
from agentlib.core.prompts.prompts import MAIN_SYSTEM_PROMPT
from agentlib.providers.base import BaseProvider


class ToolPermission(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BaseTool(ABC):
    def __init__(self, name: str, function: Callable, permission: ToolPermission):
        self.name = name
        self.function = function
        self.permission = permission


class InvalidTool(BaseTool):
    def __init__(self, name: str):
        super().__init__(name=name, function=None, permission=None)
        self.name = name


class Tool(BaseTool):
    def __init__(self, function: Callable, permission: ToolPermission):
        super().__init__(name=function.__name__, function=function, permission=permission)

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
    def __init__(
        self,
        provider: BaseProvider,
        tools: list[Tool],
        ask_tool_permission: Callable[[str, dict], bool],
    ):
        self.name = "addition_agent"
        self.provider = provider
        self.tools = tools
        self.permission = ToolPermission.LOW
        self.ask_tool_permission = ask_tool_permission

    def execute(self, prompt: str) -> str:
        agent = Agent(
            name="General Agent",
            context=Context(compose_prompt([MAIN_SYSTEM_PROMPT, prompt])),
            provider=self.provider,
            tools=self.tools,
            ask_tool_permission=self.ask_tool_permission,
        )
        print("In agent execute")
        return agent.run()

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
                            "description": (
                                "Expression to be added. It can be an English statement."
                            ),
                        }
                    },
                },
            },
        }
