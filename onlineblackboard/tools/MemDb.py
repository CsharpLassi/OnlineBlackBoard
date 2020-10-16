from typing import TypeVar, Generic, Dict, Optional

P = TypeVar('P')
T = TypeVar('T')


class MemDb(Generic[P, T]):
    def __init__(self):
        self._db: Dict[P, T] = dict()

    def add(self, key: P, value: T):
        self._db[key] = value

    def get(self, key: P) -> Optional[T]:
        return self.get(key)
