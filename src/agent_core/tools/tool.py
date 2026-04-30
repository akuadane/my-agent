from enum import Enum
import inspect
from typing import Callable, Any

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