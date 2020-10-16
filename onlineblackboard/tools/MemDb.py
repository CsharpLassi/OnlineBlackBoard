from typing import TypeVar, Generic, Dict, Optional, ItemsView

P = TypeVar('P')
T = TypeVar('T')


class MemDb(Generic[P, T]):
    def __init__(self):
        self._db: Dict[P, T] = dict()

    def items(self) -> ItemsView[P, T]:
        return self._db.items()

    def add(self, key: P, value: T):
        self._db[key] = value

    def get(self, key: P) -> Optional[T]:
        return self._db.get(key)

    def exist(self, key: P) -> bool:
        return key in self._db

    def pop(self, key: P) -> Optional[T]:
        return self._db.pop(key)
