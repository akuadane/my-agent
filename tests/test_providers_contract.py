import pytest
from src.agent_core.context.context import Context
from src.agent_core.prompts.prompts import MAIN_SYSTEM_PROMPT
from src.agent_core.providers.base import AssistantMessage
from src.agent_core.providers.ollama_provider import OllamaProvider 

@pytest.fixture
def cxt():
    context = Context(MAIN_SYSTEM_PROMPT)
    context.add_user_message("Who are you?")
    return context

@pytest.fixture
def ollama():
    return OllamaProvider('gemma4:e2b')

@pytest.mark.integration
def test_ollama_provider_stream_output(cxt,ollama):
    last_message = None
    for res in ollama.generate(cxt.get_messages(),None,[]):
        last_message = res
        assert  isinstance(res, AssistantMessage)
    
    assert last_message is not None
    assert last_message.done is True

# TODO : test with different inputs such as stream True/False after implementation.