from pydantic import BaseModel, Field

from agentkit.tools import ToolRegistry

CORPUS = [
    {
        "path": "adr/001-message-broker.md",
        "text": "Kafka was selected because replay and consumer groups. NATS is a mailbox.",
    },
    {
        "path": "adr/003-idempotency.md",
        "text": "Idempotency-Key unique constraint in Postgres is the source of truth.",
    },
    {
        "path": "adr/008-local-model-runtime.md",
        "text": "Ollama and vLLM speak OpenAI-compat. Local models first. Cloud is an env var.",
    },
    {
        "path": "adr/009-rag-citations.md",
        "text": "RAG retrieves owned docs with citations. Chain state is not in the vector index.",
    },
]


class RetrieveIn(BaseModel):
    query: str = Field(min_length=3, max_length=400)
    k: int = 3


def _score(query: str, text: str) -> int:
    q = set(query.lower().split())
    return sum(1 for t in q if t in text.lower())


def retrieve(query: str, k: int = 3) -> list[dict]:
    ranked = sorted(CORPUS, key=lambda r: _score(query, r["text"]), reverse=True)
    hits = []
    for row in ranked[:k]:
        hits.append({"path": row["path"], "text": row["text"], "score": _score(query, row["text"])})
    return hits


def register_retrieve(registry: ToolRegistry) -> None:
    def _tool(body: RetrieveIn) -> dict:
        return {"hits": retrieve(body.query, body.k)}

    registry.register("retrieve", RetrieveIn, _tool)
