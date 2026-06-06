import pytest

from src.agent_core.context.context import Context
from src.agent_core.providers.base import AssistantMessage, ToolResultMessage


@pytest.fixture
def ctx():
    return Context("sys")


def test_system_message_added_on_init():
    ctx = Context("You are a helpful assistant.")
    messages = ctx.get_messages()
    assert messages[0] == {"role": "system", "content": "You are a helpful assistant."}


def test_user_message_appended(ctx):
    ctx.add_user_message("Hello!")
    assert ctx.get_messages()[1] == {"role": "user", "content": "Hello!"}


def test_assistant_message_serialized_via_to_json(ctx):
    ctx.add_assistant_message(AssistantMessage(content="Hi there", done=True))
    messages = ctx.get_messages()
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hi there"


def test_tool_message_serialized_via_to_json(ctx):
    ctx.add_tool_message(ToolResultMessage(tool_name="add_numbers", content="42"))
    messages = ctx.get_messages()
    assert messages[1]["role"] == "tool"
    assert messages[1]["tool_name"] == "add_numbers"
    assert messages[1]["content"] == "42"


def test_message_order_preserved(ctx):
    ctx.add_user_message("question")
    ctx.add_assistant_message(AssistantMessage(content="answer", done=True))
    ctx.add_tool_message(ToolResultMessage(tool_name="t", content="result"))

    roles = [m["role"] for m in ctx.get_messages()]
    assert roles == ["system", "user", "assistant", "tool"]


def test_add_system_message_appends(ctx):
    ctx.add_system_message("second")
    roles = [m["role"] for m in ctx.get_messages()]
    assert roles.count("system") == 2
