from abc import ABC, abstractmethod
from typing import Callable, TypeVar

from sqlalchemy import Delete, Select, Update, and_, not_, or_


TQuery = TypeVar("TQuery", Select, Update, Delete)


class Specification(ABC):
    @abstractmethod
    def __call__(self, query: TQuery) -> TQuery:
        raise NotImplementedError


class FilterSpecification(Specification, ABC):
    def __and__(self, other: "FilterSpecification") -> "FilterSpecification":
        return CompositeFilterSpecification(and_, self, other)

    def __or__(self, other: "FilterSpecification") -> "FilterSpecification":
        return CompositeFilterSpecification(or_, self, other)

    def __invert__(self) -> "FilterSpecification":
        return CompositeFilterSpecification(not_, self)


class CompositeFilterSpecification(FilterSpecification, ABC):
    def __init__(self, func: Callable, *specifications: FilterSpecification):
        self._specifications = specifications
        self._func = func

    def __call__(self, query: TQuery) -> TQuery:
        specs = (spec(query=Select()).whereclause for spec in self._specifications)
        specs = (spec for spec in specs if spec is not None)

        return query.where(self._func(*specs))


class ForUpdate(Specification):
    def __call__(self, query: TQuery) -> TQuery:
        return query.with_for_update()
