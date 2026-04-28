from src.agent_core.tools.base import Tool
from src.agent_core.prompts.prompts import (
    TOOL_PROMPT_TEMPLATE,
    TOOL_BEGIN_TAG,
    TOOL_END_TAG,
)


def compose_prompt(prompts: list[str]) -> str:
    return "\n".join(prompts).strip()


def get_tool_prompt(tools: list[Tool]) -> str:
    tool_begin_tag = TOOL_BEGIN_TAG.format(TOOL_BEGIN_TAG)
    tool_end_tag = TOOL_END_TAG.format(TOOL_END_TAG)
    tools_block = "\n".join(str(tool) for tool in tools).strip()
    tool_prompt = TOOL_PROMPT_TEMPLATE.format(
        TOOL_BEGIN_TAG=tool_begin_tag, TOOL_END_TAG=tool_end_tag, tools=tools_block
    )

    return tool_prompt
