from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agentkit.llm import LLM
from agentkit.models import Run
from agentkit.tools import ToolFail, ToolRegistry, UnknownTool


async def execute_run(
    session: AsyncSession,
    run_id: str,
    llm: LLM,
    tools: ToolRegistry,
    max_attempts: int = 3,
) -> Run:
    run = await session.scalar(select(Run).where(Run.id == run_id))
    if run is None:
        raise KeyError(run_id)
    messages = [{"role": "user", "content": run.input}]
    while True:
        step = llm.next(messages)
        if step["type"] == "final":
            run.output = step["content"]
            run.status = "succeeded"
            await session.flush()
            return run
        if step["type"] != "tool_call":
            run.status = "failed"
            run.last_error = "bad llm step"
            await session.flush()
            return run
        run.attempt += 1
        while True:
            try:
                result = tools.call(step["name"], step["arguments"])
                break
            except UnknownTool as exc:
                run.status = "failed"
                run.last_error = f"unknown tool: {exc}"
                await session.flush()
                return run
            except ToolFail as exc:
                run.last_error = str(exc)
                if run.attempt >= max_attempts:
                    run.status = "dead_letter"
                    await session.flush()
                    return run
                run.attempt += 1
                continue
        messages.append({"role": "tool", "name": step["name"], "content": str(result)})
