from agentlib.providers.base import ToolResultMessage
from agentlib.tools.executor import sequential_executor
from agentlib.tools.tool import InvalidTool, Tool, ToolPermission


def allow_all(name: str, kwargs: dict) -> bool:
    return True


def deny_all(name: str, kwargs: dict) -> bool:
    return False


def make_tool(fn, permission=ToolPermission.LOW) -> Tool:
    return Tool(function=fn, permission=permission)


def collect(gen) -> list[ToolResultMessage]:
    return list(gen)


# --- Happy path ---


def test_single_low_permission_tool_executes():
    def add(a: int, b: int) -> int:
        return a + b

    tool = make_tool(add, ToolPermission.LOW)
    results = collect(sequential_executor([(tool, {"a": 1, "b": 2})], allow_all))

    assert len(results) == 1
    assert results[0].tool_name == "add"
    assert results[0].content == "3"


def test_multiple_tools_execute_in_order():
    call_log = []

    def first() -> str:
        call_log.append("first")
        return "one"

    def second() -> str:
        call_log.append("second")
        return "two"

    tools = [
        (make_tool(first), {}),
        (make_tool(second), {}),
    ]
    results = collect(sequential_executor(tools, allow_all))

    assert [r.tool_name for r in results] == ["first", "second"]
    assert [r.content for r in results] == ["one", "two"]
    assert call_log == ["first", "second"]


def test_empty_tool_list_yields_nothing():
    results = collect(sequential_executor([], allow_all))
    assert results == []


# --- HIGH permission tools ---


def test_high_permission_tool_allowed():
    def secret() -> str:
        return "sensitive"

    tool = make_tool(secret, ToolPermission.HIGH)
    results = collect(sequential_executor([(tool, {})], allow_all))

    assert len(results) == 1
    assert results[0].content == "sensitive"


def test_high_permission_tool_denied():
    def secret() -> str:
        return "sensitive"

    tool = make_tool(secret, ToolPermission.HIGH)
    results = collect(sequential_executor([(tool, {})], deny_all))

    assert len(results) == 1
    assert results[0].tool_name == "secret"
    assert "not allowed" in results[0].content


def test_mixed_permissions_denied_tool_does_not_block_next():
    def sensitive() -> str:
        return "private"

    def safe() -> str:
        return "public"

    tools = [
        (make_tool(sensitive, ToolPermission.HIGH), {}),
        (make_tool(safe, ToolPermission.LOW), {}),
    ]

    def selective_deny(name: str, kwargs: dict) -> bool:
        return name != "sensitive"

    results = collect(sequential_executor(tools, selective_deny))

    assert len(results) == 2
    assert "not allowed" in results[0].content
    assert results[1].content == "public"


# --- InvalidTool ---


def test_invalid_tool_yields_error_message():
    invalid = InvalidTool(name="ghost_tool")
    results = collect(sequential_executor([(invalid, {})], allow_all))

    assert len(results) == 1
    assert results[0].tool_name == "ghost_tool"
    assert "doesn't exist" in results[0].content


def test_invalid_tool_does_not_block_subsequent_tools():
    def real_fn() -> str:
        return "real result"

    tools = [
        (InvalidTool(name="missing"), {}),
        (make_tool(real_fn), {}),
    ]
    results = collect(sequential_executor(tools, allow_all))

    assert len(results) == 2
    assert "doesn't exist" in results[0].content
    assert results[1].content == "real result"


# --- Exception handling ---


def test_tool_that_raises_yields_error_message():
    def broken() -> str:
        raise RuntimeError("kaboom")

    tool = make_tool(broken)
    results = collect(sequential_executor([(tool, {})], allow_all))

    assert len(results) == 1
    assert results[0].tool_name == "broken"
    assert "went wrong" in results[0].content


def test_exception_in_one_tool_does_not_stop_others():
    def broken() -> str:
        raise ValueError("oops")

    def fine() -> str:
        return "ok"

    tools = [
        (make_tool(broken), {}),
        (make_tool(fine), {}),
    ]
    results = collect(sequential_executor(tools, allow_all))

    assert len(results) == 2
    assert "went wrong" in results[0].content
    assert results[1].content == "ok"


# --- Result types ---


def test_results_are_tool_result_messages():
    def greet(name: str) -> str:
        return f"hello {name}"

    tool = make_tool(greet)
    results = collect(sequential_executor([(tool, {"name": "world"})], allow_all))

    assert isinstance(results[0], ToolResultMessage)
    assert results[0].content == "hello world"


def test_non_string_return_is_coerced_to_string():
    def give_list() -> list:
        return [1, 2, 3]

    tool = make_tool(give_list)
    results = collect(sequential_executor([(tool, {})], allow_all))

    assert results[0].content == "[1, 2, 3]"


# --- Wrong kwargs (bad input to executor) ---


def test_missing_required_kwarg_yields_fallback_error():
    def greet(name: str) -> str:
        return f"hello {name}"

    tool = make_tool(greet)
    # Pass empty kwargs even though `name` is required — triggers TypeError in execute()
    results = collect(sequential_executor([(tool, {})], allow_all))

    assert len(results) == 1
    assert results[0].tool_name == "greet"
    assert "went wrong" in results[0].content


def test_unexpected_kwarg_yields_fallback_error():
    def greet(name: str) -> str:
        return f"hello {name}"

    tool = make_tool(greet)
    # Pass an argument the function doesn't accept — triggers TypeError in execute()
    results = collect(sequential_executor([(tool, {"name": "world", "extra": "oops"})], allow_all))

    assert len(results) == 1
    assert results[0].tool_name == "greet"
    assert "went wrong" in results[0].content


# --- Permission callback receives correct arguments ---


def test_permission_callback_receives_tool_name_and_kwargs():
    received = []

    def capturing_permission(name: str, kwargs: dict) -> bool:
        received.append((name, kwargs))
        return True

    def compute(x: int) -> int:
        return x * 2

    tool = make_tool(compute, ToolPermission.HIGH)
    collect(sequential_executor([(tool, {"x": 5})], capturing_permission))

    assert received == [("compute", {"x": 5})]
