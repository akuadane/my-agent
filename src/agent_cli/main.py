from src.agent_core.tools.add_numbers import AddNumbersTool
from src.agent_tools.files_tool import FilesTool
from src.agent_core.prompts.prompts import MAIN_SYSTEM_PROMPT
from src.agent_core.prompts.composer import get_tool_prompt, compose_prompt
from src.agent_core.context.context import Context
from src.agent_core.providers.ollama_provider import OllamaProvider
from src.agent_core.main_loop import run_agent



def main():
    add_numbers_tool = AddNumbersTool()
    files_tool = FilesTool()
    system_prompt = compose_prompt([MAIN_SYSTEM_PROMPT, 
                                    get_tool_prompt([add_numbers_tool, files_tool]),])
    context = Context(system_prompt)

    while True:
        user_input = input("> ")
        if user_input.lower() == "exit" or user_input.lower() == "quit" or user_input.lower() == "q":
            break
        context.add_user_message(user_input)
        response = run_agent(context, OllamaProvider(model="qwen3.5:4b"))
        # print(response)

if __name__ == "__main__":
    main()