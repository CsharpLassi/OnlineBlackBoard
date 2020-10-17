from typing import TypeVar, Generic, Dict, Optional, Tuple, List

from gevent.thread import allocate_lock

P = TypeVar('P')
T = TypeVar('T')


class MemDb(Generic[P, T]):
    __g_mem_id: int = 0

    def __init__(self):
        self.__g_mem_id += 1
        self.__mem_id = self.__g_mem_id

        self._db_lock = allocate_lock()
        self._db: Dict[P, T] = dict()

    def lock(self):
        self._db_lock.acquire()

    def release(self):
        self._db_lock.release()

    def items(self) -> List[Tuple[P, T]]:
        self.lock()
        items = list(self._db.items())
        self.release()
        return items

    def add(self, key: P, value: T):
        self.lock()
        self._db[key] = value
        self.release()

    def get(self, key: P, add_item: Optional[T] = None) -> Optional[T]:
        self.lock()
        item = self._db.get(key)
        if item is None and add_item is not None:
            self._db[key] = add_item
            item = add_item
        self.release()

        return item

    def exist(self, key: P) -> bool:
        self.lock()
        result = key in self._db
        self.release()
        return result

    def pop(self, key: P) -> Optional[T]:
        if not self.exist(key):
            return None
        self.lock()
        item = self._db.pop(key)
        self.release()
        return item
