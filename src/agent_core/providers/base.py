from abc import ABC, abstractmethod
from typing import Any
from llmx import TextGenerationConfig, TextGenerator, TextGenerationResponse


class BaseProvider(TextGenerator, ABC):
    def count_tokens(self, messages: str) -> int:
        return len(messages.split(" "))
    
    @abstractmethod
    def generate(
        self,
        messages: list[dict[str, Any]],
        config: TextGenerationConfig,
    ) -> TextGenerationResponse:
        pass