# AgentKit

Production-shaped **agent backend** for Atlas. Not a notebook wrapper.

0xMiller Labs — personal engineering lab. [ADR-008](https://github.com/0xmmiller/architecture/blob/main/adr/008-local-model-runtime.md).

## What "AI developer" means here

- **Local models first.** Ollama / vLLM / llama.cpp `llama-server` over
  OpenAI-compat `/v1/chat/completions`. Cloud is `LLM_BASE_URL`, not a
  rewrite.
- **Tools are the sandbox.** The model can `get_portfolio` and
  `create_intent` against Atlas. It cannot see Postgres, Kafka, or RPC.
- **MCP-shaped host.** `GET /v1/tools`, `POST /v1/tools/{name}` so another
  runtime can attach without importing this package.
- **Durable runs.** sqlite state, retries, `dead_letter`. CI uses `FakeLLM`.

```bash
# CI / no GPU
pytest -q
uvicorn agentkit.main:app --port 8010

# laptop
ollama pull llama3.1
LLM_BASE_URL=http://127.0.0.1:11434/v1 LLM_MODEL=llama3.1 \
  ATLAS_API_URL=http://localhost:8001 \
  uvicorn agentkit.main:app --port 8010
```
