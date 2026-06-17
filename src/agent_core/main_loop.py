from src.agent_core.context.context import Context
from src.agent_core.providers.base import BaseProvider
from src.agent_core.tools.executor import sequential_executor
from src.agent_core.providers.base import AssistantMessage
from src.agent_core.tools.tool import Tool
from llmx import TextGenerationConfig

from typing import Callable, Generator


class State:
    def __init__(self, context: Context, provider: BaseProvider, tools: list[Tool]):
        self.context = context
        self.provider = provider
        self.tools = tools
        self.tools_json = [tool.to_json() for tool in tools]
        self.tools_map = {tool.name: tool for tool in tools}
        self.continue_running = True


def run_agent(
    context: Context,
    provider: BaseProvider,
    tools: list[Tool],
    ask_tool_permission: Callable[[str, dict], bool],
    config: TextGenerationConfig = TextGenerationConfig(),
    stream: bool = True,
) -> Generator[AssistantMessage, None, None] | AssistantMessage:
    state = State(context, provider, tools)

    def _run_stream() -> Generator[AssistantMessage, None, None]:
        while state.continue_running:
            tools_called = []
            response = None

            for response in state.provider.generate(
                state.context.get_messages(), config, state.tools_json, stream=True
            ):
                if not response.done:
                    yield response

            for tool_call in response.tool_calls:
                tools_called.append(
                    (
                        state.tools_map[tool_call["function"]["name"]],
                        tool_call["function"]["arguments"],
                    )
                )

            state.context.add_assistant_message(response)

            if tools_called:
                for tool_result in sequential_executor(
                    tools_called, ask_tool_permission
                ):
                    state.context.add_tool_message(tool_result)
                # state.context.add_system_message(TOOL_RESULT_PROMPT_TEMPLATE)

            else:
                state.continue_running = False

    def _run_one() -> AssistantMessage:
        while state.continue_running:
            tools_called = []
            response = None

            response = state.provider.generate(
                state.context.get_messages(), config, state.tools_json, stream=False
            )

            for tool_call in response.tool_calls:
                tools_called.append(
                    (
                        state.tools_map[tool_call["function"]["name"]],
                        tool_call["function"]["arguments"],
                    )
                )

            state.context.add_assistant_message(response)

            if tools_called:
                for tool_result in sequential_executor(
                    tools_called, ask_tool_permission
                ):
                    state.context.add_tool_message(tool_result)
                # state.context.add_system_message(TOOL_RESULT_PROMPT_TEMPLATE)

            else:
                state.continue_running = False

    if stream:
        return _run_stream()

    return _run_one()
