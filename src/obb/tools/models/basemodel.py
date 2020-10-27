from __future__ import annotations

from typing import TypeVar, Type

# noinspection PyTypeChecker
T = TypeVar("T", bound="BaseModel")


class BaseModel:
    @classmethod
    def get(cls: Type[T], id) -> T:
        """
        :rtype: __thisclass__
        """
        return cls.query.get(id)
