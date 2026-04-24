MAIN_SYSTEM = """
You are a helpful assistant that can use tools to help the user.
"""

TOOL_PROMPT_TEMPLATE = """
If you need to use a tool, you should display the tool name and the parramters in a json format.

You MUST indicate the beginning and the end of the tool request with <tool_request> and </tool_request>.

<tool_request>
{{
  "tools": [
    {{
      "tool": "browser",
      "parameters": {{
        "url": "https://www.google.com",
        "query": "What is the latest news in ethiopia?"
      }}
    }}
  ]
}}
</tool_request>

If you need multiple tools, you should display the tools in a list. You are allowed to call a tool more than once.


You have the following tools available to you:
{tools}
"""
