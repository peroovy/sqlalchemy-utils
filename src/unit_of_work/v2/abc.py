from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import TracebackType
from typing import Generic, TypeVar


class UnitOfWorkIsAlreadyOpened(Exception):
    pass


class UnitOfWorkHasNotBeenOpenedYet(Exception):
    pass


@dataclass(frozen=True)
class Context(ABC):
    pass


TContext = TypeVar("TContext", bound=Context, covariant=True)


class ISavepoint(ABC):
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        raise NotImplementedError


class ISavepointManager(ABC):
    @abstractmethod
    async def __aenter__(self) -> ISavepoint:
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        raise NotImplementedError


class IUnitOfWork(Generic[TContext], ABC):
    @abstractmethod
    async def commit(self) -> None:
        """
        :raise UnitOfWorkHasNotBeenOpenedYet: юнит ещё не открыт
        """
        raise NotImplementedError

    @abstractmethod
    async def rollback(self) -> None:
        """
        :raise UnitOfWorkHasNotBeenOpenedYet: юнит ещё не открыт
        """
        raise NotImplementedError

    @abstractmethod
    async def __aenter__(self) -> TContext:
        """
        :raise UnitOfWorkIsAlreadyOpened: юнит уже открыт
        """
        raise NotImplementedError

    @abstractmethod
    async def __aexit__(
        self, exc_type: type[BaseException] | None, exc_value: BaseException | None, traceback: TracebackType | None
    ) -> None:
        """
        :raise UnitOfWorkHasNotBeenOpenedYet: юнит ещё не открыт
        """
        raise NotImplementedError

    @abstractmethod
    def begin_savepoint(self) -> ISavepointManager:
        """
        :raise UnitOfWorkHasNotBeenOpenedYet: юнит ещё не открыт
        """
        raise NotImplementedError
