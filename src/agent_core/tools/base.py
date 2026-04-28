from abc import ABC, abstractmethod
from typing import Any


class ToolParameter(ABC):
    def __init__(self, name: str, description: str, type: str, required: bool):
        self.name = name
        self.description = description
        self.type = type
        self.required = required

    def __str__(self) -> str:
        required = str(self.required).lower()
        return (
            f"\tname: {self.name}\n"
            f"\tdescription: {self.description}\n"
            f"\ttype: {self.type}\n"
            f"\trequired: {required}\n"
        )


class Tool(ABC):
    def __init__(self, name: str, description: str, parameters: list[ToolParameter]):
        self.name = name
        self.description = description
        self.parameters = parameters

    def __str__(self) -> str:
        parameters = "\n".join(
            str(parameter).replace("\n", "\n    ") for parameter in self.parameters
        )
        return (
            f"- tool name: {self.name}\n"
            f"  tool description: {self.description}\n"
            f"  parameters:\n"
            f"  {parameters}"
        )

    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass
