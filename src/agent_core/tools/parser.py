from src.agent_core.tools.tools_factory import ToolsFactory
from src.agent_core.tools.base import Tool
from src.agent_core.prompts.prompts import TOOL_BEGIN_TAG, TOOL_END_TAG
import json

def get_tool_from_response(response: str) -> list[Tool]:
    tools = []
    tool_request_start = response.find(TOOL_BEGIN_TAG)
    tool_request_end = response.find(TOOL_END_TAG)

    # TODO : Throw an error if the tool request is not found
    if tool_request_start == -1 or tool_request_end == -1:
        return []

    tool_request = response[tool_request_start + len(TOOL_BEGIN_TAG):tool_request_end]

    return json_to_tools(json.loads(tool_request))

def json_to_tools(json_str: dict) -> list[Tool]:
    tools = []
    for tool in json_str["tools"]:
        tools.append(ToolsFactory.get_tool(tool["tool"]))
    return tools