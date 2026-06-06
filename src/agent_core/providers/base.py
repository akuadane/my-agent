from abc import ABC, abstractmethod
from typing import Any, Generator, Literal, overload
from llmx import TextGenerationConfig, TextGenerator, Message


class BaseProvider(TextGenerator, ABC):
    def count_tokens(self, messages: str) -> int:
        return len(messages.split(" "))

    @overload
    def generate(
        self,
        messages: list[dict[str, Any]],
        config: TextGenerationConfig,
        tools: list[dict[str, Any]],
        stream: Literal[True],
    ) -> Generator["AssistantMessage", None, None]: ...

    @overload
    def generate(
        self,
        messages: list[dict[str, Any]],
        config: TextGenerationConfig,
        tools: list[dict[str, Any]],
        stream: Literal[False],
    ) -> "AssistantMessage": ...

    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, Any]],
        config: TextGenerationConfig,
        tools: list[dict[str, Any]],
        stream: bool = True,
    ) -> "Generator[AssistantMessage, None, None] | AssistantMessage":
        pass


class AssistantMessage(Message):
    def __init__(
        self,
        content: str = "",
        thinking: str = "",
        tool_calls: list[dict[str, Any]] = [],
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
            "tool_calls": self.tool_calls,
        }


class ToolResultMessage(Message):
    def __init__(self, tool_name: str, content: str):
        super().__init__(
            role="tool",
            content=content,
        )
        self.tool_name = tool_name

    def to_json(self) -> dict[str, Any]:
        return {
            "role": "tool",
            "tool_name": self.tool_name,
            "content": self.content,
        }
