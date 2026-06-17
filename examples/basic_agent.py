from colorama import Fore, Style, init

from agentlib.cli.policy import ask_tool_permission_cli
from agentlib.core.context import Context
from agentlib.core.loop import run_agent
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
    ollama_provider = OllamaProvider(model="gemma4:e2b")
    while True:
        user_input = input("> ")
        if (
            user_input.lower() == "exit"
            or user_input.lower() == "quit"
            or user_input.lower() == "q"
        ):
            break
        context.add_user_message(user_input)
        showing_thinking = False
        showing_content = False
        for response in run_agent(context, ollama_provider, tools, ask_tool_permission_cli):
            # Match examples/ttt.py: stream thinking and content separately; both may
            # appear in the same chunk, so use two `if`s, not if/elif.
            if response.thinking:
                if not showing_thinking:
                    print("\n", flush=True)
                    print(Fore.YELLOW + "Agent: Thinking ... ", end="", flush=True)
                    showing_thinking = True
                print(Fore.YELLOW + response.thinking, end="", flush=True)

            if response.content:
                if not showing_content:
                    print("\n", flush=True)
                    print(Fore.GREEN + "Agent: ", end="", flush=True)
                    showing_content = True
                print(Fore.GREEN + response.content, end="", flush=True)
                showing_thinking = False

        print(Style.RESET_ALL + "\n")


if __name__ == "__main__":
    main()
