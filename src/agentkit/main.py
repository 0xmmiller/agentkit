from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from agentkit.llm import FakeLLM
from agentkit.models import Base, Run
from agentkit.tools import ToolRegistry
from agentkit.worker import execute_run

engine = create_async_engine(
    "sqlite+aiosqlite:///./agentkit.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
app = FastAPI(title="AgentKit")
TOOLS = ToolRegistry()


class RunIn(BaseModel):
    input: str


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/runs")
async def create_run(body: RunIn) -> dict:
    async with SessionLocal() as session:
        run = Run(input=body.input, status="queued")
        session.add(run)
        await session.flush()
        await execute_run(session, run.id, FakeLLM(), TOOLS)
        await session.commit()
        return {"id": run.id, "status": run.status, "output": run.output}
