from copy import deepcopy
from typing import TYPE_CHECKING, Callable

from agentlib.core.context import Context
from agentlib.providers.base import BaseProvider

if TYPE_CHECKING:
    from agentlib.tools.tool import Tool


class Agent:
    def __init__(
        self,
        name: str,
        desc: str,
        context: Context,
        provider: BaseProvider,
        tools: list["Tool"],
        ask_tool_permission: Callable[[str, dict], bool],
    ):
        self.name = name
        self.tools = tools
        self.context = context
        self.__init_context = deepcopy(context)
        self.provider = provider
        self.ask_tool_permission = ask_tool_permission
        self.desc = desc

    def __deepcopy__(self, memo: dict) -> "Agent":
        return Agent(
            name=self.name,
            desc=self.desc,
            context=deepcopy(self.__init_context, memo),
            provider=self.provider,
            tools=deepcopy(self.tools, memo),
            ask_tool_permission=self.ask_tool_permission,
        )

    def fresh_copy(self) -> "Agent":
        return Agent(
            name=self.name,
            desc=self.desc,
            context=deepcopy(self.__init_context),
            provider=self.provider,
            tools=deepcopy(self.tools),
            ask_tool_permission=self.ask_tool_permission,
        )

    def run(self) -> Context:
        # from agentlib.core.loop import run_agent
        import agentlib.cli.utilis as cli_utils

        # run_agent(self.context, self.provider, self.tools, self.ask_tool_permission, stream=False)
        cli_utils.display_agent_work(
            name="Sub",
            context=self.context,
            provider=self.provider,
            tools=self.tools,
            ask_tool_permission_cli=self.ask_tool_permission,
        )
        # TODO handle this with more care
        return self.context.get_messages()[-1]["content"]
