from typing import TYPE_CHECKING, Callable

from agentlib.core.context import Context
from agentlib.providers.base import BaseProvider

if TYPE_CHECKING:
    from agentlib.tools.tool import Tool


class Agent:
    def __init__(
        self,
        name: str,
        context: Context,
        provider: BaseProvider,
        tools: list["Tool"],
        ask_tool_permission: Callable[[str, dict], bool],
    ):
        self.name = name
        self.tools = tools
        self.context = context
        self.provider = provider
        self.ask_tool_permission = ask_tool_permission

    def run(self) -> Context:
        from agentlib.core.loop import run_agent

        run_agent(self.context, self.provider, self.tools, self.ask_tool_permission, stream=False)
        # TODO handle this with more care
        return self.context.get_messages()[-1]["content"]
