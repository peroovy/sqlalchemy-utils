from types import TracebackType
from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction

from .abc import (
    ISavepoint,
    ISavepointManager,
    IUnitOfWork,
    TContext,
    UnitOfWorkHasNotBeenOpenedYet,
    UnitOfWorkIsAlreadyOpened,
)


class AlchemyUnitOfWork(IUnitOfWork[TContext]):
    def __init__(
        self, session_factory: Callable[[], AsyncSession], context_factory: Callable[[AsyncSession], TContext]
    ) -> None:
        self._session_factory = session_factory
        self._context_factory = context_factory

        self._session: AsyncSession | None = None

    async def __aenter__(self) -> TContext:
        if self._session:
            raise UnitOfWorkIsAlreadyOpened

        self._session = await self._session_factory().__aenter__()
        await self._session.begin()

        return self._context_factory(self._session)

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        if not self._session:
            raise UnitOfWorkHasNotBeenOpenedYet

        await self._session.__aexit__(exc_type, exc_value, traceback)

    def begin_savepoint(self) -> ISavepointManager:
        if not self._session:
            raise UnitOfWorkHasNotBeenOpenedYet

        return _AlchemySavepointManager(savepoint=self._session.begin_nested())

    async def commit(self) -> None:
        if not self._session:
            raise UnitOfWorkHasNotBeenOpenedYet

        await self._session.commit()

    async def rollback(self) -> None:
        if not self._session:
            raise UnitOfWorkHasNotBeenOpenedYet

        await self._session.rollback()


class _AlchemySavepointManager(ISavepointManager):
    def __init__(self, savepoint: AsyncSessionTransaction) -> None:
        self._savepoint = savepoint

    async def __aenter__(self) -> ISavepoint:
        await self._savepoint.__aenter__()

        return _AlchemySavepoint(self._savepoint)

    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        await self._savepoint.__aexit__(exc_type, exc_value, traceback)


class _AlchemySavepoint(ISavepoint):
    def __init__(self, savepoint: AsyncSessionTransaction) -> None:
        self._savepoint = savepoint

    async def commit(self) -> None:
        await self._savepoint.commit()

    async def rollback(self) -> None:
        await self._savepoint.rollback()
