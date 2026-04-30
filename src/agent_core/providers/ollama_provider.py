from .base import BaseProvider
from typing import Any
from llmx import TextGenerationConfig
import requests
from typing import Generator
from src.agent_core.providers.base import AssistantMessageStream, ToolCall
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
    ) -> Generator[AssistantMessageStream, None, None]:
        payload = {
            "model": self.model,
            "messages": messages,
            # "config": config.model_dump(),
            "stream": True,
            "tools": tools,
        }
        assistant_content = ""
        thinking_content = ""
        final_tool_calls = []
        prev_chunk = b""
        for chunk in requests.post(f"{self.base_url}/api/chat", json=payload, stream=True):
            try: 
                data = json.loads(prev_chunk + chunk)
                prev_chunk = b""
                message = data.get("message", {})
                assistant_content += message.get("content", "")
                thinking_content += message.get("thinking", "")
              
                tool_calls = []
                for tool_call in message.get("tool_calls", []):
                    func = data.get("function", {})
                    tool_calls.append(ToolCall(index=func.get('index'), name=func.get("name"), arguments=tool_call.get("arguments")))
                
                final_tool_calls.extend(tool_calls)
                yield AssistantMessageStream(content=message.get("content", ""), 
                    thinking=message.get("thinking", ""), tool_calls=tool_calls, done=data.get("done", False))
            except json.JSONDecodeError:
                prev_chunk += chunk
                continue
            
           
       
        yield AssistantMessageStream(content=assistant_content, thinking=thinking_content, done=True)
        
