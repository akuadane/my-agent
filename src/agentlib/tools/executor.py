from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Generator

from agentlib.providers.base import ToolResultMessage
from agentlib.tools.tool import Tool, ToolPermission


def sequential_executor(
    tools: list[(Tool, dict)], ask_tool_permission: Callable[[str, dict], bool]
) -> Generator[ToolResultMessage, None, None]:
    for tool, kwargs in tools:
        print("Executing tool: ", tool.name)
        if tool.permission == ToolPermission.HIGH:
            if not ask_tool_permission(tool.name, kwargs):
                yield ToolResultMessage(
                    tool_name=tool.name,
                    content=f"Tool {tool.name} was not allowed to be used by the user.",
                )
                continue
        result = tool.execute(**kwargs)
        yield ToolResultMessage(tool_name=tool.name, content=str(result))


def parallel_executor(tools: list[(Tool, dict)]) -> list[str]:
    if not tools:
        return []

    with ThreadPoolExecutor(max_workers=len(tools)) as executor:
        return list(
            executor.map(lambda tool_call: str(tool_call[0].execute(**tool_call[1])), tools)
        )
