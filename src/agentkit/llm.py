from typing import Any, Protocol


class LLM(Protocol):
    def next(self, messages: list[dict[str, Any]]) -> dict[str, Any]: ...


class FakeLLM:
    """Deterministic: first turn tool_call, then final text."""

    def __init__(self, tool: str = "echo", arguments: dict | None = None, fail_tool_times: int = 0) -> None:
        self.tool = tool
        self.arguments = arguments or {"text": "ok"}
        self.fail_tool_times = fail_tool_times
        self._turn = 0

    def next(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        self._turn += 1
        if self._turn == 1:
            return {"type": "tool_call", "name": self.tool, "arguments": self.arguments}
        return {"type": "final", "content": "done"}
