from typing import Generic, Iterable, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.base import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.specifications import FilterSpecification, Specification, TQuery


TModel = TypeVar("TModel", bound=Base)


class Repository(Generic[TModel]):
    model: type[TModel]

    def __init__(self, session: AsyncSession, model: type[TModel]):
        self.session = session
        self.model = model

    def save(self, obj: TModel) -> None:
        self.session.add(obj)

    async def delete(self, obj: TModel) -> None:
        await self.session.delete(obj)

    async def update(self, *specifications: Specification, **values) -> None:
        query = self._apply_specification(update(self.model), specifications)

        await self.session.execute(query.values(values).execution_options(synchronize_session=False))

    async def delete_many(self, *specifications: FilterSpecification) -> None:
        await self.session.execute(self._apply_specification(delete(self.model), specifications))

    async def refresh(self, obj: TModel) -> None:
        await self.session.refresh(obj)

    async def all(self) -> list[TModel]:
        query = select(self.model)

        return list(await self.session.scalars(query))

    async def find_first(self, *specifications: Specification) -> TModel | None:
        query = self._apply_specification(select(self.model).limit(1), specifications)

        return await self.session.scalar(query)

    async def get_one(self, *specifications: Specification) -> TModel:
        obj = await self.find_first(*specifications)

        if obj is None:
            raise NotFoundObjectException

        return obj

    async def find(self, *specifications: Specification) -> list[TModel]:
        query = self._apply_specification(select(self.model), specifications)

        return list(await self.session.scalars(query))

    async def exists(self, *specifications: Specification) -> bool:
        return bool(await self.find_first(*specifications))

    @staticmethod
    def _apply_specification(init_query: TQuery, specifications: Iterable[Specification]) -> TQuery:
        query = init_query

        for spec in specifications:
            query = spec(query)

        return query


class NotFoundObjectException(Exception):
    pass
