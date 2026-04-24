from src.agent_core.tools.parser import get_tool_from_response
from src.agent_core.context.context import Context
from src.agent_core.providers.base import BaseProvider
from src.agent_core.tools.executor import sequential_executor
from src.agent_core.prompts.prompts import TOOL_RESULT_PROMPT_TEMPLATE

class State: 
    def __init__(self, context: Context, provider: BaseProvider):
        self.context = context
        self.provider = provider
        self.continue_running = True


def run_agent(context: Context, provider: BaseProvider) -> str:
    state = State(context, provider)


    while state.continue_running:
        response = state.provider.generate(state.context.get_messages(),None)
        output = response.text[0].content
        print("Output: ", output)
        tools = get_tool_from_response(output)
        
        print("Output: ", output)
        print("Tools: ", tools)

        if tools:
            tool_results = sequential_executor(tools)
            state.context.add_system_message(TOOL_RESULT_PROMPT_TEMPLATE)
            state.context.add_multiple_tool_messages(tool_results)

        else:
            state.context.add_assistant_message(output)
            state.continue_running = False
    
    return state.context.messages
