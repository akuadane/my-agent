from .base import BaseProvider
from typing import Any
from llmx import TextGenerationConfig, TextGenerationResponse, Message
import requests

class OllamaProvider(BaseProvider):
    def __init__(self, model: str, base_url: str = "http://localhost:11434"):
        super().__init__(provider_type="ollama", model_name=model)
        self.base_url = base_url
        self.model = model
    
    def generate(
        self,
        messages: list[dict[str, Any]],
        config: TextGenerationConfig,
    ) -> TextGenerationResponse:
        payload = {
            "model": self.model,
            "messages": messages,
            # "config": config.model_dump(),
            "stream": False
        }
        response = requests.post(f"{self.base_url}/api/chat", json=payload)
        data = response.json()
        msg = data.get("message") or {}
        assistant = Message(
            role=str(msg.get("role", "assistant")),
            content=str(msg.get("content") or ""),
        )
        return TextGenerationResponse(
            text=[assistant],
            config=config,
            usage=data.get("eval_count"),
            response=data,
        )