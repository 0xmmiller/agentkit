# AgentKit

Production-shaped **agent backend**, not a 100-line OpenAI wrapper.

0xMiller Labs - personal engineering lab.

What this has that a notebook does not:

- Durable run state (sqlite)
- Typed tool registry (unknown names are rejected)
- Allowlisted sandbox (`python -c` / `echo` via subprocess + timeout)
- In-process queue (Redis-shaped interface)
- Retries with backoff, then `dead_letter`
- `run_id` on every log line (OTel span would wrap `ToolRegistry.call`)

Default LLM is `FakeLLM` - tests never need an API key.

```bash
pip install -e ".[dev]" && pytest -q
uvicorn agentkit.main:app --port 8010
```
