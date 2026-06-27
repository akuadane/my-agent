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

        elif response.content:
            if not showing_content:
                print("\n", flush=True)
                print(Fore.GREEN + f"({name}) Talking: ", end="", flush=True)
                showing_content = True
            print(Fore.GREEN + response.content, end="", flush=True)
            showing_thinking = False

    print(Style.RESET_ALL + "\n")


def speak_agent_work(
    context: Context,
    provider: BaseProvider,
    tools: List[Tool],
    ask_tool_permission_cli: ToolPermission,
):
    import queue
    import re
    import subprocess
    import threading

    speech_queue: queue.Queue = queue.Queue()

    def speaker():
        end = False

        while not end:
            items = [speech_queue.get()]
            if items[0] is None:
                break

            try:
                while True:
                    item = speech_queue.get_nowait()

                    if item is None:
                        end = True
                        break

                    items.append(item)
            except queue.Empty:
                pass

            text = " ".join(items)
            if text.strip():
                subprocess.run(["say", text], check=False)

    thread = threading.Thread(target=speaker, daemon=True)
    thread.start()

    buffer = ""
    for response in run_agent(context, provider, tools, ask_tool_permission_cli):
        if response.content:
            buffer += response.content
            sentences = re.split(r"(?<=[.!?])\s+", buffer)
            if len(sentences) > 1:
                speech_queue.put(" ".join(sentences[:-1]))
                buffer = sentences[-1]

    if buffer.strip():
        speech_queue.put(buffer)

    speech_queue.put(None)
    thread.join()
