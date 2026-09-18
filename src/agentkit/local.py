from typing import Any

import httpx

from agentkit.llm import LLM


class OpenAICompatLLM:
    """Ollama, vLLM, llama.cpp server, or a vendor. Same wire.

    Default is local: http://127.0.0.1:11434/v1 (Ollama).
    """

    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434/v1",
        model: str = "llama3.1",
        timeout: float = 60.0,
        tools: list[dict[str, Any]] | None = None,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.tools = tools
        self._client = client or httpx.Client(timeout=timeout)

    def next(self, messages: list[dict[str, Any]]) -> dict[str, Any]:
        payload: dict[str, Any] = {"model": self.model, "messages": messages}
        if self.tools:
            payload["tools"] = self.tools
        resp = self._client.post(f"{self.base_url}/chat/completions", json=payload)
        resp.raise_for_status()
        return parse_completion(resp.json())


def parse_completion(body: dict[str, Any]) -> dict[str, Any]:
    msg = body["choices"][0]["message"]
    calls = msg.get("tool_calls") or []
    if calls:
        import json

        fn = calls[0]["function"]
        args = fn.get("arguments") or "{}"
        if isinstance(args, str):
            args = json.loads(args or "{}")
        return {"type": "tool_call", "name": fn["name"], "arguments": args}
    return {"type": "final", "content": msg.get("content") or ""}


def llm_from_env() -> LLM:
    import os

    url = os.getenv("LLM_BASE_URL")
    if not url:
        from agentkit.llm import FakeLLM

        return FakeLLM()
    return OpenAICompatLLM(base_url=url, model=os.getenv("LLM_MODEL", "llama3.1"))
