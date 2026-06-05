import pytest
from unittest.mock import patch

from src.agent_cli.policy import ask_tool_permission_cli


@pytest.mark.parametrize("user_input", ["y", "yes"])
def test_returns_true_on_approval(user_input):
    with patch("builtins.input", return_value=user_input):
        assert ask_tool_permission_cli("my_tool", {"arg": "value"}) is True


@pytest.mark.parametrize("user_input", ["n", "no", "N", "anything"])
def test_returns_false_on_rejection(user_input):
    print(user_input)
    with patch("builtins.input", return_value=user_input):
        assert ask_tool_permission_cli("my_tool", {"arg": "value"}) is False
