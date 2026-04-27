from src.agent_core.tools.base import Tool, ToolParameter


class AddNumbersTool(Tool):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            Tool.__init__(
                cls._instance,
                "add_numbers",
                "Helps add two huge numbers; returns their exact integer sum.",
                [
                    ToolParameter(
                        name="a",
                        description="First addend (integer, including very large values)",
                        type="integer",
                        required=True,
                    ),
                    ToolParameter(
                        name="b",
                        description="Second addend (integer, including very large values)",
                        type="integer",
                        required=True,
                    ),
                ],
            )
        return cls._instance

    def __init__(self) -> None:
        pass

    def execute(self, a: int, b: int) -> str:
        return str(int(a) + int(b))
