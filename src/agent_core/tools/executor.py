from src.agent_core.tools.tool import Tool


def sequential_executor(tools: list[(Tool, dict)]) -> list[str]:
    results = []
    for tool, kwargs in tools:
        result = tool.execute(**kwargs)
        results.append(result)
    return results


# TODO : Implement the parallel executor
def parallel_executor(tools: list[(Tool, dict)]) -> list[str]:
    pass
