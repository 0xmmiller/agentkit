from agentkit.atlas_tools import register_atlas_tools
from agentkit.retrieve import register_retrieve
from agentkit.local import llm_from_env
from agentkit.mcp import McpHost
from agentkit.models import Base, Run
from agentkit.tools import ToolRegistry
from agentkit.worker import execute_run
from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

engine = create_async_engine(
    "sqlite+aiosqlite:///./agentkit.db",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)
app = FastAPI(title="AgentKit")
TOOLS = ToolRegistry()
register_atlas_tools(TOOLS)
register_retrieve(TOOLS)
MCP = McpHost(TOOLS)


class RunIn(BaseModel):
    input: str


class ToolIn(BaseModel):
    arguments: dict = {}


@app.on_event("startup")
async def startup() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/v1/tools")
async def list_tools() -> dict:
    return {"tools": MCP.list_tools()}


@app.post("/v1/tools/{name}")
async def call_tool(name: str, body: ToolIn) -> dict:
    return MCP.call_tool(name, body.arguments)


@app.post("/v1/runs")
async def create_run(body: RunIn) -> dict:
    async with SessionLocal() as session:
        run = Run(input=body.input, status="queued")
        session.add(run)
        await session.flush()
        await execute_run(session, run.id, llm_from_env(), TOOLS)
        await session.commit()
        return {"id": run.id, "status": run.status, "output": run.output}
