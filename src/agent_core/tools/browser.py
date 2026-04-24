from src.agent_core.tools.base import Tool, ToolParameter


class BrowserTool(Tool):
    def __init__(self):
        super().__init__(
            name="browser",
            description="Use this tool to browse the web",
            parameters=[
                ToolParameter(
                    name="url",
                    description="The URL to browse",
                    type="string",
                    required=True,
                ),
                ToolParameter(
                    name="query",
                    description="The query to search the web",
                    type="string",
                    required=True,
                ),
            ],
        )

    def execute(self, url: str, query: str) -> str:
        return f"Browsing the web for {query} at {url}"
