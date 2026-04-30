from src.agent_core.prompts.prompts import MAIN_SYSTEM_PROMPT
from src.agent_core.prompts.composer import compose_prompt
from src.agent_core.context.context import Context
from src.agent_core.providers.ollama_provider import OllamaProvider
from src.agent_core.main_loop import run_agent
from src.agent_core.tools.tool import Tool, ToolPermission
from src.agent_tools.tools import add_numbers, read_file, list_directory
from colorama import Fore, Style, init

init(autoreset=True)


def main():
    add_numbers_tool = Tool(function=add_numbers, permission=ToolPermission.LOW)
    file_reader_tool = Tool(function=read_file, permission=ToolPermission.LOW)
    list_directory_tool = Tool(function=list_directory, permission=ToolPermission.LOW)

    tools = [add_numbers_tool, file_reader_tool, list_directory_tool]
    system_prompt = compose_prompt([MAIN_SYSTEM_PROMPT])
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
        showing_thinking = False
        for response in run_agent(context, OllamaProvider(model="qwen3.5:4b"), tools):
            if response.thinking:
                print(
                    Fore.YELLOW + "\rThinking ... " + Style.RESET_ALL,
                    end="",
                    flush=True,
                )
                showing_thinking = True
            else:
                if showing_thinking:
                    print("\r\033[K", end="", flush=True)
                    showing_thinking = False
                print(
                    Fore.GREEN + response.content + Style.RESET_ALL, end="", flush=True
                )
        print("\n")


if __name__ == "__main__":
    main()
