from colorama import init

import agentlib.cli.utilis as cli_utils
from agentlib.cli.policy import ask_tool_permission_cli
from agentlib.core.context import Context
from agentlib.core.prompts.composer import compose_prompt
from agentlib.core.prompts.prompts import MAIN_SYSTEM_PROMPT
from agentlib.providers.ollama import OllamaProvider
from agentlib.tools.builtin.basic import add_numbers, list_directory, read_file
from agentlib.tools.tool import Tool, ToolPermission

init(autoreset=True)


def main():
    add_numbers_tool = Tool(function=add_numbers, permission=ToolPermission.HIGH)
    file_reader_tool = Tool(function=read_file, permission=ToolPermission.LOW)
    list_directory_tool = Tool(function=list_directory, permission=ToolPermission.LOW)

    tools = [add_numbers_tool, file_reader_tool, list_directory_tool]
    system_prompt = compose_prompt([MAIN_SYSTEM_PROMPT])
    print(system_prompt)
    context = Context(system_prompt)
    ollama_provider = OllamaProvider(model="qwen3.5:4b")
    while True:
        user_input = input("> ")
        if (
            user_input.lower() == "exit"
            or user_input.lower() == "quit"
            or user_input.lower() == "q"
        ):
            break
        context.add_user_message(user_input)
        cli_utils.speak_agent_work(
            context=context,
            provider=ollama_provider,
            tools=tools,
            ask_tool_permission_cli=ask_tool_permission_cli,
        )


if __name__ == "__main__":
    main()
