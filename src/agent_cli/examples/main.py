from src.agent_core.prompts.prompts import MAIN_SYSTEM_PROMPT
from src.agent_core.prompts.composer import compose_prompt
from src.agent_core.context.context import Context
from src.agent_core.providers.ollama_provider import OllamaProvider
from src.agent_core.main_loop import run_agent
from src.agent_core.tools.tool import Tool, ToolPermission
from src.agent_tools.tools import add_numbers, read_file, list_directory
from colorama import Fore, Style, init
from src.agent_cli.policy import ask_tool_permission

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
        for response in run_agent(context, ollama_provider, tools, ask_tool_permission):
            # Match examples/ttt.py: stream thinking and content separately; both may
            # appear in the same chunk, so use two `if`s, not if/elif.
            if response.thinking:
                if not showing_thinking:
                    print('\n', flush=True)
                    print(Fore.YELLOW + "Agent: Thinking ... ", end="", flush=True)
                    showing_thinking = True
                print(Fore.YELLOW + response.thinking, end="", flush=True)

            if response.content:
                if not showing_content:
                    print('\n', flush=True)
                    print(Fore.GREEN + "Agent: ", end="", flush=True)
                    showing_content = True
                print(Fore.GREEN + response.content, end="", flush=True)
                showing_thinking = False

        print(Style.RESET_ALL + "\n")


if __name__ == "__main__":
    main()
