from src.agent_core.tools.parser import get_tool_from_response
from src.agent_core.context.context import Context
from src.agent_core.providers.base import BaseProvider
from src.agent_core.tools.executor import sequential_executor
from src.agent_core.prompts.prompts import TOOL_RESULT_PROMPT_TEMPLATE
from src.agent_core.providers.base import AssistantMessageStream
from src.agent_core.tools.tool import Tool

from typing import Generator



class State:
    def __init__(self, context: Context, provider: BaseProvider, tools: list[Tool]):
        self.context = context
        self.provider = provider
        self.tools = tools
        self.tools_json = [tool.to_json() for tool in tools]
        self.continue_running = True


def run_agent(context: Context, provider: BaseProvider, tools: list[Tool]) -> Generator[AssistantMessageStream, None, None]:
    state = State(context, provider, tools)

    while state.continue_running:
        for response in state.provider.generate(state.context.get_messages(), None, state.tools_json):
            if not response.done:
                yield response
            # print("Response: ", response)
            if response.tool_calls:
                print("Tool calls: ", response.tool_calls)

        output = response.content
        state.context.add_assistant_message(response)
        tools = get_tool_from_response(output)

        print("Tools: ", tools)

        if tools:
            tool_results = sequential_executor(tools)
            state.context.add_system_message(TOOL_RESULT_PROMPT_TEMPLATE)
            state.context.add_multiple_tool_messages(tool_results)

        else:
            state.continue_running = False

    return state.context.messages
