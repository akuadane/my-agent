from src.agent_core.tools.base import Tool
from src.agent_core.tools.add_numbers import AddNumbersTool
from src.agent_core.tools.browser import BrowserTool
from src.agent_tools.files_tool import FilesTool


class ToolsFactory:
    @staticmethod
    def get_tool(tool_name: str) -> Tool:
        if tool_name == "browser":
            return BrowserTool()
        if tool_name == "add_numbers":
            return AddNumbersTool()
        if tool_name == "files":
            return FilesTool()
        else:
            raise ValueError(f"Tool {tool_name} not found")
