import subprocess
from collections.abc import Callable
from typing import Any

from pydantic import BaseModel, Field


class EchoIn(BaseModel):
    text: str = Field(max_length=200)


class EchoOut(BaseModel):
    text: str


class UnknownTool(Exception):
    pass


class ToolFail(Exception):
    pass


def _echo(payload: EchoIn) -> EchoOut:
    proc = subprocess.run(
        ["echo", payload.text],
        capture_output=True,
        text=True,
        timeout=2,
        check=False,
    )
    if proc.returncode != 0:
        raise ToolFail(proc.stderr)
    return EchoOut(text=proc.stdout.rstrip("\n"))


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, Callable[[BaseModel], Any]] = {"echo": _echo}
        self._models: dict[str, type[BaseModel]] = {"echo": EchoIn}

    def call(self, name: str, arguments: dict) -> dict:
        # OTel: start a span named tool.{name} here, attribute run_id.
        if name not in self._tools:
            raise UnknownTool(name)
        model = self._models[name]
        parsed = model.model_validate(arguments)
        result = self._tools[name](parsed)
        if isinstance(result, BaseModel):
            return result.model_dump()
        return dict(result)

    def register(self, name: str, model: type[BaseModel], fn: Callable[[BaseModel], Any]) -> None:
        self._tools[name] = fn
        self._models[name] = model
