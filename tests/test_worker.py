from pydantic import BaseModel
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from agentkit.llm import FakeLLM
from agentkit.models import Base, Run
from agentkit.tools import ToolFail, ToolRegistry
from agentkit.worker import execute_run


async def _setup():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def test_success():
    engine, factory = await _setup()
    async with factory() as session:
        run = Run(input="hi")
        session.add(run)
        await session.flush()
        out = await execute_run(session, run.id, FakeLLM(), ToolRegistry())
        assert out.status == "succeeded"
        assert out.output == "done"
    await engine.dispose()


async def test_retry_then_success():
    engine, factory = await _setup()
    tools = ToolRegistry()
    state = {"n": 0}

    class X(BaseModel):
        pass

    def flaky(_: X):
        state["n"] += 1
        if state["n"] < 3:
            raise ToolFail("boom")
        return {"ok": True}

    tools.register("echo", X, flaky)
    async with factory() as session:
        run = Run(input="hi")
        session.add(run)
        await session.flush()
        out = await execute_run(session, run.id, FakeLLM(arguments={}), tools, max_attempts=5)
        assert out.status == "succeeded"
        assert state["n"] == 3
    await engine.dispose()


async def test_dead_letter():
    engine, factory = await _setup()
    tools = ToolRegistry()

    class X(BaseModel):
        pass

    def always(_: X):
        raise ToolFail("nope")

    tools.register("echo", X, always)
    async with factory() as session:
        run = Run(input="hi")
        session.add(run)
        await session.flush()
        out = await execute_run(session, run.id, FakeLLM(arguments={}), tools, max_attempts=3)
        assert out.status == "dead_letter"
        assert out.attempt == 3
    await engine.dispose()


async def test_unknown_tool():
    engine, factory = await _setup()
    async with factory() as session:
        run = Run(input="hi")
        session.add(run)
        await session.flush()
        out = await execute_run(
            session, run.id, FakeLLM(tool="rm", arguments={}), ToolRegistry()
        )
        assert out.status == "failed"
        assert "unknown tool" in (out.last_error or "")
    await engine.dispose()
