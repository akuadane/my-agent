import json
from pathlib import Path

from src.agent_core.tools.executor import sequential_executor
from src.agent_core.tools.add_numbers import AddNumbersTool
from src.agent_core.tools.parser import get_tool_from_response
from src.agent_core.tools.tools_factory import ToolsFactory

import pytest


@pytest.mark.parametrize(
    "tool_calls,expected",
    [
        ([(AddNumbersTool(), {"a": 1, "b": 2})], ["3"]),
        (
            [
                (AddNumbersTool(), {"a": 1, "b": 2}),
                (AddNumbersTool(), {"a": -3, "b": 4}),
                (AddNumbersTool(), {"a": 5, "b": -6}),
            ],
            ["3", "1", "-1"],
        ),
        ([],[])
    ],
)
def test_sequential_executor(tool_calls, expected):
    assert sequential_executor(tool_calls) == expected


def test_get_tool_from_response():
    fixture_path = Path(__file__).parent / "fixtures" / "tool_call_valid.json"
    tool_call_valid = json.loads(fixture_path.read_text(encoding="utf-8"))

    expected = [
        (
            ToolsFactory.get_tool(tool_data["tool"]),
            tool_data["parameters"],
        )
        for tool_data in tool_call_valid["output"]
    ]

    assert get_tool_from_response(tool_call_valid["input"]) == expected
