import inspect
from abc import ABC
from copy import deepcopy
from enum import Enum
from typing import Any, Callable

from agentlib.core.agent import Agent


class ToolPermission(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class BaseTool(ABC):
    def __init__(self, name: str):
        self.name = name


class InvalidTool(BaseTool):
    def __init__(self, name: str):
        super().__init__(name=name)
        self.name = name


class Tool(BaseTool):
    def __init__(self, function: Callable, permission: ToolPermission):
        super().__init__(name=function.__name__)
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
    def __init__(self, template: Agent):
        self.template = template
        self.name = template.name
        self.permission = ToolPermission.LOW

    def execute(self, prompt: str) -> str:
        agent = deepcopy(self.template)
        agent.context.add_user_message(prompt)

        return agent.run()

    def to_json(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.template.name,
                "description": self.template.desc,
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
