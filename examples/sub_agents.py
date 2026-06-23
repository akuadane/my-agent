from colorama import init

import agentlib.cli.utilis as cli_utils
from agentlib.cli.policy import ask_tool_permission_cli
from agentlib.core.agent import Agent
from agentlib.core.context import Context
from agentlib.core.prompts.composer import compose_prompt
from agentlib.core.prompts.prompts import MAIN_SYSTEM_PROMPT, SUB_AGENT_AVAILABILITY_SYSTEM_PROMPT
from agentlib.providers.ollama import OllamaProvider
from agentlib.tools.builtin.basic import add_numbers, list_directory, read_file
from agentlib.tools.tool import AgentManagerTool, Tool, ToolPermission

init(autoreset=True)


def main():
    add_numbers_tool = Tool(function=add_numbers, permission=ToolPermission.HIGH)
    file_reader_tool = Tool(function=read_file, permission=ToolPermission.LOW)
    list_directory_tool = Tool(function=list_directory, permission=ToolPermission.LOW)

    base_tools = [file_reader_tool, list_directory_tool]
    ollama_provider = OllamaProvider(model="gemma4:e2b")
    sub_agent_tool = AgentManagerTool(
        Agent(
            name="Addition Calculator",
            desc="""This agent has addition tools. 
                    Use it when you want to subdivide a task or calculate addition.""",
            context=Context(MAIN_SYSTEM_PROMPT),
            provider=ollama_provider,
            tools=[*base_tools, add_numbers_tool],
            ask_tool_permission=ask_tool_permission_cli,
        )
    )

    tools = [*base_tools, sub_agent_tool]
    system_prompt = compose_prompt([MAIN_SYSTEM_PROMPT, SUB_AGENT_AVAILABILITY_SYSTEM_PROMPT])
    print(system_prompt)
    context = Context(system_prompt)

    while True:
        user_input = input("> ")
        if (
            user_input.lower() == "exit"
            or user_input.lower() == "quit"
            or user_input.lower() == "q"
        ):
            break
        context.add_user_message(user_input)

        cli_utils.display_agent_work(
            name="Main",
            context=context,
            provider=ollama_provider,
            tools=tools,
            ask_tool_permission_cli=ask_tool_permission_cli,
        )


if __name__ == "__main__":
    main()
