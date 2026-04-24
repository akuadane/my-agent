from src.agent_core.tools.base import Tool, ToolParameter


class BrowserTool(Tool):
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            Tool.__init__(
            cls._instance,
            "browser",
            "Use this tool to browse the web",
            [
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
        return cls._instance

    def __init__(self) -> None:
        # Tool is initialized in __new__; Python still calls __init__ after __new__,
        # so this overrides Tool.__init__ to avoid a second call with no args.
        pass

    def execute(self, url: str, query: str) -> str:
        return f"Browsing the web for {query} at {url}"
