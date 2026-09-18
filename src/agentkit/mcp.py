from typing import Any

from agentkit.tools import ToolRegistry, UnknownTool


class McpHost:
    """MCP-shaped boundary: list tools, call by name. No model in this process."""

    def __init__(self, registry: ToolRegistry) -> None:
        self.registry = registry

    def list_tools(self) -> list[dict[str, Any]]:
        out = []
        for name, model in self.registry._models.items():
            out.append(
                {
                    "name": name,
                    "input_schema": model.model_json_schema(),
                }
            )
        return out

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            return self.registry.call(name, arguments)
        except UnknownTool as exc:
            return {"error": "unknown_tool", "name": str(exc)}
