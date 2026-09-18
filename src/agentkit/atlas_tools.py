import os

import httpx
from pydantic import BaseModel, Field

from agentkit.tools import ToolFail, ToolRegistry


class PortfolioIn(BaseModel):
    owner: str = Field(min_length=3, max_length=66)


class IntentIn(BaseModel):
    owner: str = Field(min_length=3, max_length=66)
    idempotency_key: str


def register_atlas_tools(registry: ToolRegistry, base_url: str | None = None, token: str = "lab-key") -> None:
    """Atlas product tools. The model never sees SQL, Kafka, or RPC URLs."""
    api = (base_url or os.getenv("ATLAS_API_URL") or "http://localhost:8001").rstrip("/")
    headers = {"Authorization": f"Bearer {token}"}

    def get_portfolio(body: PortfolioIn) -> dict:
        try:
            r = httpx.get(f"{api}/v1/portfolio/{body.owner}", headers=headers, timeout=5.0)
            r.raise_for_status()
        except httpx.HTTPError as exc:
            raise ToolFail(str(exc)) from exc
        return r.json()

    def create_intent(body: IntentIn) -> dict:
        try:
            r = httpx.post(
                f"{api}/v1/intents",
                headers={**headers, "Idempotency-Key": body.idempotency_key},
                json={"owner": body.owner, "chain_id": 1, "payload": {"source": "agentkit"}},
                timeout=5.0,
            )
            r.raise_for_status()
        except httpx.HTTPError as exc:
            raise ToolFail(str(exc)) from exc
        return r.json()

    registry.register("get_portfolio", PortfolioIn, get_portfolio)
    registry.register("create_intent", IntentIn, create_intent)
