from src.agent_core.tools.tool import Tool
from src.agent_core.providers.base import ToolResultMessage
from typing import Generator


def sequential_executor(
    tools: list[(Tool, dict)],
) -> Generator[ToolResultMessage, None, None]:

    for tool, kwargs in tools:
        result = tool.execute(**kwargs)
        yield ToolResultMessage(tool_name=tool.name, content=str(result))


# TODO : Implement the parallel executor
def parallel_executor(tools: list[(Tool, dict)]) -> list[str]:
    pass
