from agentkit.local import parse_completion
from agentkit.mcp import McpHost
from agentkit.tools import ToolRegistry


def test_parse_tool_call():
    body = {
        "choices": [
            {
                "message": {
                    "tool_calls": [
                        {"function": {"name": "get_portfolio", "arguments": '{"owner":"0xabc"}'}}
                    ]
                }
            }
        ]
    }
    step = parse_completion(body)
    assert step["type"] == "tool_call"
    assert step["name"] == "get_portfolio"
    assert step["arguments"]["owner"] == "0xabc"


def test_parse_final():
    body = {"choices": [{"message": {"content": "hello"}}]}
    assert parse_completion(body) == {"type": "final", "content": "hello"}


def test_mcp_lists_and_rejects_unknown():
    host = McpHost(ToolRegistry())
    names = {t["name"] for t in host.list_tools()}
    assert "echo" in names
    assert host.call_tool("rm", {})["error"] == "unknown_tool"
