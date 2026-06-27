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


def _speech_worker(speech_queue):
    """Consume text chunks from the queue and speak them with pyttsx3.

    Runs in its own process so pyttsx3's macOS driver gets a working
    main-thread run loop.
    """
    import queue

    import pyttsx3

    while True:
        items = [speech_queue.get()]
        if items[0] is None:
            break

        try:
            while True:
                item = speech_queue.get_nowait()
                if item is None:
                    speech_queue.put(None)  # re-signal stop after flushing
                    break
                items.append(item)
        except queue.Empty:
            pass

        text = " ".join(items).strip()
        if text:
            pyttsx3.speak(text)


def speak_agent_work(
    context: Context,
    provider: BaseProvider,
    tools: List[Tool],
    ask_tool_permission_cli: ToolPermission,
):
    import multiprocessing
    import re

    speech_queue: multiprocessing.Queue = multiprocessing.Queue()

    # Runs in a separate PROCESS (not a thread) so the engine owns its own
    # main-thread run loop, which pyttsx3's macOS driver requires.
    process = multiprocessing.Process(target=_speech_worker, args=(speech_queue,), daemon=True)
    process.start()

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
    process.join()
