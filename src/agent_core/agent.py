from src.agent_core.context.context import Context
from src.agent_core.providers.base import BaseProvider
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from src.agent_core.tools.tool import Tool


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
        from src.agent_core.main_loop import run_agent

        for _ in run_agent(
            self.context,
            self.provider,
            self.tools,
            self.ask_tool_permission,
        ):
            pass
        # TODO handle this with more care
        return self.context.get_messages()[-1]["content"]
