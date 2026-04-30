from src.agent_core.context.context import Context
from src.agent_core.providers.base import BaseProvider
from src.agent_core.tools.executor import sequential_executor
from src.agent_core.providers.base import AssistantMessageStream
from src.agent_core.tools.tool import Tool

from typing import Generator


class State:
    def __init__(self, context: Context, provider: BaseProvider, tools: list[Tool]):
        self.context = context
        self.provider = provider
        self.tools = tools
        self.tools_json = [tool.to_json() for tool in tools]
        self.tools_map = {tool.name: tool for tool in tools}
        self.continue_running = True


def run_agent(
    context: Context, provider: BaseProvider, tools: list[Tool]
) -> Generator[AssistantMessageStream, None, None]:
    state = State(context, provider, tools)

    while state.continue_running:
        tools_called = []
        for response in state.provider.generate(
            state.context.get_messages(), None, state.tools_json
        ):
            if not response.done:
                yield response
            if response.tool_calls and not response.done:
                tools_called.append(
                    (
                        state.tools_map[response.tool_calls[0].name],
                        response.tool_calls[0].arguments,
                    )
                )

        state.context.add_assistant_message(response)

        if tools_called:
            for tool_result in sequential_executor(tools_called):
                state.context.add_tool_message(tool_result)
            # state.context.add_system_message(TOOL_RESULT_PROMPT_TEMPLATE)

        else:
            state.continue_running = False

    return state.context.messages
