from typing import List

from colorama import Fore, Style

from agentlib.core.context import Context
from agentlib.core.loop import run_agent
from agentlib.providers.base import BaseProvider
from agentlib.tools.tool import Tool, ToolPermission


def display_agent_work(
    name: str,
    context: Context,
    provider: BaseProvider,
    tools: List[Tool],
    ask_tool_permission_cli: ToolPermission,
):
    showing_thinking = False
    showing_content = False
    for response in run_agent(context, provider, tools, ask_tool_permission_cli):
        if response.thinking:
            if not showing_thinking:
                print("\n", flush=True)
                print(Fore.YELLOW + f"({name}) Thinking: ", end="", flush=True)
                showing_thinking = True
            print(Fore.YELLOW + response.thinking, end="", flush=True)

        if response.content:
            if not showing_content:
                print("\n", flush=True)
                print(Fore.GREEN + f"({name}) Talking: ", end="", flush=True)
                showing_content = True
            print(Fore.GREEN + response.content, end="", flush=True)
            showing_thinking = False

    print(Style.RESET_ALL + "\n")
