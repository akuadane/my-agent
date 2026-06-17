TOOL_BEGIN_TAG = "<tool_request>"
TOOL_END_TAG = "</tool_request>"

MAIN_SYSTEM_PROMPT = """
You are a helpful assistant that can use tools to help the user.
"""

TOOL_PROMPT_TEMPLATE = """
If you need to use a tool, you should display the tool name and the parramters in a json format.

You MUST indicate the beginning and the end of the tool request
with <tool_request> and </tool_request>.

If multiple tools are needed and can be used in the same request,
you MUST mention multiple tools in the same request.

{TOOL_BEGIN_TAG}
{{
  "tools": [
    {{
      "tool": "browser",
      "parameters": {{
        "url": "https://www.google.com",
        "query": "What is the latest news in ethiopia?"
      }}
    }},
    {{
      "tool": "add_numbers",
      "parameters": {{
        "a": 1,
        "b": 2
      }}
    }}
  ]
}}
{TOOL_END_TAG}


You have the following tools available to you:
{tools}
"""

RETRY_TOOL_PROMPT = """
The previous tool request was not successful because {reason}. You MUST retry the tool request.
You should display the tool name and the parramters in a json format.

You MUST indicate the beginning and the end of the tool request
with <tool_request> and </tool_request>.

You can also use multiple tools in the same request.
{TOOL_BEGIN_TAG}
{{
  "tools": [
    {{
      "tool": "browser",
      "parameters": {{
        "url": "https://www.google.com",
        "query": "What is the latest news in ethiopia?"
      }}
    }},
    {{
      "tool": "add_numbers",
      "parameters": {{
        "a": 1,
        "b": 2
      }}
    }}
  ]
}}
{TOOL_END_TAG}
"""

TOOL_RESULT_PROMPT_TEMPLATE = """
The tool results are as follows:
"""
SUB_AGENT_SYSTEM_PROMPT = """
You can launch specialized subagents to complete tasks.
When a task is broad or parallelizable, start one or more subagents.

For each subagent, provide:
- subagent_type: [explore | generalPurpose | shell | ...]
- description: short 3-5 word title
- prompt: detailed, self-contained instructions including:
  - goal
  - exact files/paths to inspect
  - constraints (read-only vs editable)
  - expected output format
  - what to return (findings, diffs, commands run, risks)

Rules:
- Use multiple subagents in parallel when tasks are independent.
- Keep prompts explicit; subagents do not inherit full user context unless included.
- Prefer direct tools for narrow/simple tasks instead of spawning subagents.
"""
