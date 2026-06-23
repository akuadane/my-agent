from copy import deepcopy

from agentlib.core.agent import Agent
from agentlib.core.context import Context
from agentlib.providers.base import AssistantMessage, BaseProvider
from agentlib.tools.tool import Tool, ToolPermission


def allow_all(name: str, kwargs: dict) -> bool:
    return True


def make_tool(fn, permission=ToolPermission.LOW) -> Tool:
    return Tool(function=fn, permission=permission)


class MockProvider(BaseProvider):
    """Returns responses from a fixed list, cycling on the last one."""

    def __init__(self, responses: list[AssistantMessage] | None = None):
        self._responses = responses or [AssistantMessage(content="ok", tool_calls=[], done=True)]
        self._call_count = 0

    def generate(self, messages, config, tools, stream=True):
        response = self._responses[min(self._call_count, len(self._responses) - 1)]
        self._call_count += 1
        if stream:
            return iter([response])
        return response


def make_agent(
    name: str = "agent",
    desc: str = "test agent",
    system_prompt: str = "You are helpful.",
    provider: BaseProvider | None = None,
    tools: list[Tool] | None = None,
) -> Agent:
    return Agent(
        name=name,
        desc=desc,
        context=Context(system_prompt),
        provider=provider or MockProvider(),
        tools=tools or [],
        ask_tool_permission=allow_all,
    )


# --- Construction ---


def test_agent_stores_attributes():
    provider = MockProvider()
    context = Context("sys")
    agent = Agent(
        name="my_agent",
        desc="does stuff",
        context=context,
        provider=provider,
        tools=[],
        ask_tool_permission=allow_all,
    )
    assert agent.name == "my_agent"
    assert agent.desc == "does stuff"
    assert agent.context is context
    assert agent.provider is provider
    assert agent.tools == []
    assert agent.ask_tool_permission is allow_all


# --- run() ---


def test_run_returns_final_response():
    provider = MockProvider([AssistantMessage(content="Done!", tool_calls=[], done=True)])
    agent = make_agent(provider=provider)
    agent.context.add_user_message("hello")
    assert agent.run() == "Done!"


def test_run_calls_tool_then_returns_final_response():
    call_log = []

    def greet(name: str) -> str:
        call_log.append(name)
        return f"hi {name}"

    tool = make_tool(greet)
    responses = [
        AssistantMessage(
            content="",
            tool_calls=[{"function": {"name": "greet", "arguments": {"name": "world"}}}],
            done=True,
        ),
        AssistantMessage(content="Done after tool.", tool_calls=[], done=True),
    ]
    agent = make_agent(provider=MockProvider(responses), tools=[tool])
    agent.context.add_user_message("greet someone")

    result = agent.run()

    assert call_log == ["world"]
    assert result == "Done after tool."


# --- __deepcopy__ ---


def test_deepcopy_returns_new_agent():
    agent = make_agent()
    copy = deepcopy(agent)
    assert copy is not agent


def test_deepcopy_preserves_name_and_desc():
    agent = make_agent(name="agent_x", desc="does x")
    copy = deepcopy(agent)
    assert copy.name == "agent_x"
    assert copy.desc == "does x"


def test_deepcopy_context_is_independent():
    agent = make_agent(system_prompt="sys")
    copy = deepcopy(agent)

    agent.context.add_user_message("only in original")

    contents = [m.get("content") for m in copy.context.get_messages()]
    assert "only in original" not in contents


def test_deepcopy_starts_from_initial_context():
    agent = make_agent(system_prompt="sys")
    agent.context.add_user_message("accumulated message")

    copy = deepcopy(agent)

    contents = [m.get("content") for m in copy.context.get_messages()]
    assert "accumulated message" not in contents


def test_deepcopy_shares_provider_and_callback():
    agent = make_agent()
    copy = deepcopy(agent)
    assert copy.provider is agent.provider
    assert copy.ask_tool_permission is agent.ask_tool_permission


# --- fresh_copy() ---


def test_fresh_copy_returns_new_agent():
    agent = make_agent()
    fresh = agent.fresh_copy()
    assert fresh is not agent


def test_fresh_copy_preserves_name_and_desc():
    agent = make_agent(name="agent_y", desc="does y")
    fresh = agent.fresh_copy()
    assert fresh.name == "agent_y"
    assert fresh.desc == "does y"


def test_fresh_copy_resets_conversation_history():
    agent = make_agent(system_prompt="sys")
    agent.context.add_user_message("hello")
    agent.context.add_user_message("world")

    fresh = agent.fresh_copy()
    messages = fresh.context.get_messages()

    assert len(messages) == 1
    assert messages[0]["role"] == "system"


def test_fresh_copy_preserves_system_prompt():
    agent = make_agent(system_prompt="You are a pirate.")
    agent.context.add_user_message("talk to me")

    fresh = agent.fresh_copy()
    messages = fresh.context.get_messages()

    assert messages[0]["content"] == "You are a pirate."


def test_fresh_copy_preserves_multiple_system_prompts():
    context = Context("First prompt.")
    context.add_system_message("Second prompt.")
    agent = Agent(
        name="multi_sys",
        desc="test",
        context=context,
        provider=MockProvider(),
        tools=[],
        ask_tool_permission=allow_all,
    )
    agent.context.add_user_message("hello")

    fresh = agent.fresh_copy()
    messages = fresh.context.get_messages()

    assert [m["role"] for m in messages] == ["system", "system"]
    assert [m["content"] for m in messages] == ["First prompt.", "Second prompt."]


def test_fresh_copy_context_is_independent_from_original():
    agent = make_agent()
    fresh = agent.fresh_copy()

    fresh.context.add_user_message("only in fresh")

    contents = [m.get("content") for m in agent.context.get_messages()]
    assert "only in fresh" not in contents


def test_fresh_copy_shares_provider_and_callback():
    agent = make_agent()
    fresh = agent.fresh_copy()
    assert fresh.provider is agent.provider
    assert fresh.ask_tool_permission is agent.ask_tool_permission
