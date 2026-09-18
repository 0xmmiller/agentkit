import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class Queue:
    """In-process queue. Swap for Redis later without changing workers."""

    def __init__(self) -> None:
        self._q: asyncio.Queue[str] = asyncio.Queue()

    async def push(self, run_id: str) -> None:
        await self._q.put(run_id)

    async def pop(self) -> str:
        return await self._q.get()


def backoff_s(attempt: int, base: float = 0.05, cap: float = 2.0) -> float:
    return min(cap, base * (2**attempt))
