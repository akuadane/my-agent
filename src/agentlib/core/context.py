from llmx import Message

from agentlib.providers.base import AssistantMessage, ToolResultMessage


class Context:
    def __init__(self, system_message: str):
        self.messages: list[Message] = []
        self.add_system_message(system_message)

    def add_system_message(self, system_message: str):
        self.messages.append(Message(role="system", content=system_message))

    def add_user_message(self, message: str):
        self.messages.append(Message(role="user", content=message))

    def add_assistant_message(self, message: AssistantMessage):
        self.messages.append(message)

    def add_tool_message(self, message: ToolResultMessage):
        self.messages.append(message)

    def get_messages(self) -> list[Message]:
        return [
            (
                message.to_json()
                if message.role == "assistant" or message.role == "tool"
                else {"role": message.role, "content": message.content}
            )
            for message in self.messages
        ]
