from src.agent_core.prompts.prompts import MAIN_SYSTEM_PROMPT
from src.agent_core.prompts.composer import compose_prompt
from src.agent_core.context.context import Context
from src.agent_core.providers.ollama_provider import OllamaProvider
from src.agent_core.main_loop import run_agent
from src.agent_core.tools.tool import Tool, ToolPermission
from src.agent_tools.tools import add_numbers
from colorama import Fore, Style, init
init(autoreset=True)

def main():
    add_numbers_tool = Tool(function=add_numbers, permission=ToolPermission.LOW)
    tools = [add_numbers_tool]
    system_prompt = compose_prompt(
        [
            MAIN_SYSTEM_PROMPT
        ]
    )
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
        for response in run_agent(context, OllamaProvider(model="gemma4:e2b"), tools):
            if response.thinking:
                print( Fore.YELLOW + "Thinking ... " + Style.RESET_ALL, end="\r")
            else:
                print( Fore.GREEN + response.content + Style.RESET_ALL, end="")

if __name__ == "__main__":
    main()
