from src.agent_core.tools.base import Tool
from src.agent_core.prompts.prompts import TOOL_PROMPT_TEMPLATE

def compose_prompt(**prompts: str) -> str:
    return "\n".join(prompts.values()).strip()


def get_tool_prompt(**tools: Tool) -> str:
    tools_block = "\n".join(str(tool) for tool in tools.values()).strip()
    return TOOL_PROMPT_TEMPLATE.format(tools=tools_block)