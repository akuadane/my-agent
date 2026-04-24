from src.agent_core.tools.base import Tool
from src.agent_core.tools.browser import BrowserTool

class ToolsFactory:

    @staticmethod
    def get_tool(tool_name: str) -> Tool:
        if tool_name == "browser":
            return BrowserTool()
        else:
            raise ValueError(f"Tool {tool_name} not found")