from abc import ABC, abstractmethod
from typing import Any
from llmx import TextGenerationConfig, TextGenerator, TextGenerationResponse, Message


class BaseProvider(TextGenerator, ABC):
    def count_tokens(self, messages: str) -> int:
        return len(messages.split(" "))

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, Any]],
        config: TextGenerationConfig,
        tools: list[dict[str, Any]],
    ) -> TextGenerationResponse:
        pass


class ToolCall:
    def __init__(self, index: int, name: str, arguments: dict):
        self.index = index
        self.name = name
        self.arguments = arguments

    def to_json(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "index": self.index,
                "name": self.name,
                "arguments": self.arguments,
            },
        }

    def __str__(self) -> str:
        return str(self.to_json())


class AssistantMessageStream(Message):
    def __init__(
        self,
        content: str = "",
        thinking: str = "",
        tool_calls: list[ToolCall] = [],
        done: bool = False,
    ):
        super().__init__(role="assistant", content=content)
        self.content = content
        self.thinking = thinking
        self.done = done
        self.tool_calls = tool_calls

    def __str__(self) -> str:
        return f"AssistantMessageStream(content='{self.content}', thinking='{self.thinking}', tool_calls='{self.tool_calls}', done='{self.done}')"

    def to_json(self) -> dict[str, Any]:
        return {
            "role": "assistant",
            "content": self.content,
            "thinking": self.thinking,
            "tool_calls": [tool_call.to_json() for tool_call in self.tool_calls],
        }


class ToolResultMessage(Message):
    def __init__(self, tool_name: str, content: str):
        super().__init__(
            role="tool",
            tool_calls=[ToolCall(index=0, name=tool_name, arguments={})],
            content=content,
        )
        self.tool_name = tool_name
        self.content = content

    def to_json(self) -> dict[str, Any]:
        return {
            "role": "tool",
            "tool_name": self.tool_name,
            "content": self.content,
        }
