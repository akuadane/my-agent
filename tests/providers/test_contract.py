import pytest

from agentlib.core.context import Context
from agentlib.core.prompts.prompts import MAIN_SYSTEM_PROMPT
from agentlib.providers.base import AssistantMessage
from agentlib.providers.ollama import OllamaProvider


@pytest.fixture
def cxt():
    context = Context(MAIN_SYSTEM_PROMPT)
    context.add_user_message("Who are you?")
    return context


@pytest.fixture
def ollama():
    return OllamaProvider("gemma4:e2b")


@pytest.mark.integration
def test_ollama_provider_stream_output(cxt, ollama):
    last_message = None
    for res in ollama.generate(cxt.get_messages(), None, []):
        last_message = res
        assert isinstance(res, AssistantMessage)

    assert last_message is not None
    assert last_message.done is True


@pytest.mark.integration
def test_ollama_provider_nonstream_output(cxt, ollama):
    res = ollama.generate(cxt.get_messages(), None, [], stream=False)

    assert isinstance(res, AssistantMessage)
    assert res is not None
    assert res.done is True
