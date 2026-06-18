from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Generator

from agentlib.providers.base import ToolResultMessage
from agentlib.tools.tool import BaseTool, InvalidTool, ToolPermission


def sequential_executor(
    tools: list[(BaseTool, dict)], ask_tool_permission: Callable[[str, dict], bool]
) -> Generator[ToolResultMessage, None, None]:
    for tool, kwargs in tools:
        try:
            if isinstance(tool, InvalidTool):
                yield ToolResultMessage(
                    tool_name=tool.name,
                    content=f"Tool {tool.name} doesn't exist in your environment.",
                )
                continue

            if tool.permission == ToolPermission.HIGH:
                if not ask_tool_permission(tool.name, kwargs):
                    yield ToolResultMessage(
                        tool_name=tool.name,
                        content=f"Tool {tool.name} was not allowed to be used by the user.",
                    )
                    continue
            result = tool.execute(**kwargs)
            yield ToolResultMessage(tool_name=tool.name, content=str(result))
        except Exception:
            yield ToolResultMessage(
                tool_name=tool.name, content="Something went wrong while executing this tool"
            )


def parallel_executor(tools: list[(BaseTool, dict)]) -> list[str]:
    if not tools:
        return []

    with ThreadPoolExecutor(max_workers=len(tools)) as executor:
        return list(
            executor.map(lambda tool_call: str(tool_call[0].execute(**tool_call[1])), tools)
        )
