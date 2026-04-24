TOOL_BEGIN_TAG = "<tool_request>"
TOOL_END_TAG = "</tool_request>"

MAIN_SYSTEM_PROMPT = """
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

RETRY_TOOL_PROMPT = """
The previous tool request was not successful because {reason}. You MUST retry the tool request.
You should display the tool name and the parramters in a json format.

You MUST indicate the beginning and the end of the tool request with <tool_request> and </tool_request>.

{TOOL_BEGIN_TAG}
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
{TOOL_END_TAG}
"""

TOOL_RESULT_PROMPT_TEMPLATE = """
The tool results are as follows:
"""