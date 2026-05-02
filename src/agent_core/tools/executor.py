from src.agent_core.tools.tool import Tool, ToolPermission
from src.agent_core.providers.base import ToolResultMessage
from typing import Callable, Generator


def sequential_executor(
    tools: list[(Tool, dict)], ask_tool_permission: Callable[[str, dict], bool]
) -> Generator[ToolResultMessage, None, None]:

    for tool, kwargs in tools:
        if tool.permission == ToolPermission.HIGH:
            if not ask_tool_permission(tool.name, kwargs):
                yield ToolResultMessage(tool_name=tool.name, content=f"Tool {tool.name} was not allowed to be used by the user.")
                continue 
        result = tool.execute(**kwargs)
        yield ToolResultMessage(tool_name=tool.name, content=str(result))


# TODO : Implement the parallel executor
def parallel_executor(tools: list[(Tool, dict)]) -> list[str]:
    pass
