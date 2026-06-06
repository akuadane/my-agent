from .base import BaseProvider
from typing import Any, Generator
from llmx import TextGenerationConfig
import requests
from src.agent_core.providers.base import AssistantMessage
import json


class OllamaProvider(BaseProvider):
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        super().__init__(provider_type="ollama", model_name=model)
        self.base_url = base_url
        self.model = model

    def generate(
        self,
        messages: list[dict[str, Any]],
        config: TextGenerationConfig,
        tools: list[dict[str, Any]],
        stream: bool = True,
    ) -> Generator[AssistantMessage, None, None] | AssistantMessage:
        payload = {
            "model": self.model,
            "messages": messages,
            "options": {k: v for k, v in config if v is not None} if config else {},
            "stream": stream,
            "tools": tools,
        }
        if stream:
            return self._generate_stream(payload)
        else:
            return self._generate_one(payload)

    def _generate_stream(
        self, payload: dict
    ) -> Generator[AssistantMessage, None, None]:
        assistant_content = ""
        thinking_content = ""
        final_tool_calls = []
        prev_chunk = b""
        for chunk in requests.post(
            f"{self.base_url}/api/chat", json=payload, stream=True
        ):
            try:
                data = json.loads(prev_chunk + chunk)
                prev_chunk = b""
                message = data.get("message", {})
                assistant_content += message.get("content", "")
                thinking_content += message.get("thinking", "")
                function_call = message.get("tool_calls", None)
                tool_call = []
                if function_call:
                    function_data = function_call[0].get("function", {})
                    tool_call = [
                        {
                            "type": "function",
                            "function": {
                                "index": function_call[0].get("index", 0),
                                "name": function_data.get("name", ""),
                                "arguments": function_data.get("arguments", {}),
                            },
                        }
                    ]
                    final_tool_calls.extend(tool_call)
                yield AssistantMessage(
                    content=message.get("content", ""),
                    thinking=message.get("thinking", ""),
                    tool_calls=tool_call,
                    done=data.get("done", False),
                )
            except json.JSONDecodeError:
                prev_chunk += chunk
                continue

        yield AssistantMessage(
            content=assistant_content,
            thinking=thinking_content,
            tool_calls=final_tool_calls,
            done=True,
        )

    def _generate_one(self, payload: dict) -> AssistantMessage:
        data = requests.post(f"{self.base_url}/api/chat", json=payload).json()
        message = data.get("message", {})
        tool_calls = []
        function_call = message.get("tool_calls", None)
        if function_call:
            function_data = function_call[0].get("function", {})
            tool_calls = [
                {
                    "type": "function",
                    "function": {
                        "index": function_call[0].get("index", 0),
                        "name": function_data.get("name", ""),
                        "arguments": function_data.get("arguments", {}),
                    },
                }
            ]
        return AssistantMessage(
            content=message.get("content", ""),
            thinking=message.get("thinking", ""),
            tool_calls=tool_calls,
            done=True,
        )
