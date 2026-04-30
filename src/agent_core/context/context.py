from llmx import Message

from src.agent_core.providers.base import AssistantMessageStream


class Context:
    def __init__(self, system_message: str):
        self.messages = []
        self.add_system_message(system_message)

    def add_system_message(self, system_message: str):
        self.messages.append(Message(role="system", content=system_message))

    def add_user_message(self, message: str):
        self.messages.append(Message(role="user", content=message))

    def add_assistant_message(self, message: AssistantMessageStream):
        self.messages.append(message)

    def add_tool_message(self, message: str):
        self.messages.append(Message(role="tool", content=message))

    def add_multiple_tool_messages(self, messages: list[Message]):
        for message in messages:
            self.add_tool_message(message)

    def get_messages(self) -> list[Message]:
        return [
            (
                {"role": message.role, "content": message.content, "thinking": message.thinking}
                if message.role == "assistant"
                else {"role": message.role, "content": message.content}
            )
            for message in self.messages
        ]
