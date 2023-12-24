from contextlib import AsyncExitStack, asynccontextmanager
from typing import AsyncContextManager, AsyncIterator, Callable

from fastapi import FastAPI


Lifespan = Callable[[FastAPI], AsyncIterator[None]]
LifespanContext = Callable[[FastAPI], AsyncContextManager[None]]


class LifespanRegistry:
    def __init__(self) -> None:
        self._lifespans: list[LifespanContext] = []

    def register(self, lifespan: Lifespan) -> None:
        self._lifespans.append(asynccontextmanager(lifespan))

    @asynccontextmanager
    async def __call__(self, app: FastAPI) -> AsyncIterator[None]:
        async with AsyncExitStack() as stack:
            for lifespan in self._lifespans:
                await stack.enter_async_context(lifespan(app))

            yield
