import datetime
from typing import TypeVar, Generic, Dict, Optional, Tuple, List, Callable, Generator
from gevent.thread import allocate_lock

P = TypeVar("P")
T = TypeVar("T")


class MemDb(Generic[P, T]):
    def __init__(self, expired_minutes: int = 120):
        assert expired_minutes > 0, f"'expired_minutes' must be greater than 0"

        self._db_lock = allocate_lock()
        self._db: Dict[P, T] = dict()
        self._expired: Dict[P, datetime] = dict()

        self._expired_minutes = expired_minutes

    def _calc_exp(self) -> datetime.datetime:
        date = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=self._expired_minutes
        )
        return date

    def lock(self):
        self._db_lock.acquire()

    def release(self):
        self._db_lock.release()

    def items(self) -> List[Tuple[P, T]]:
        items = list()
        self.lock()
        for item_id, item in self._db.items():
            items.append((item_id, item))
        self.release()
        return items

    def add(self, key: P, value: T) -> T:
        self.lock()
        self._db[key] = value
        self._expired[key] = self._calc_exp()
        self.release()
        return value

    def find(self, func: Callable[[P, T], bool]) -> Optional[T]:
        for key, item in self.items():
            if func(key, item):
                return item
        return None

    def get(self, key: P, add_item: Optional[T] = None, **kwargs) -> Optional[T]:
        self.lock()
        item = self._db.get(key)
        if item is None and add_item is not None:
            self._db[key] = add_item
            item = add_item
        if item:
            self._expired[key] = self._calc_exp()

        self.release()

        exist_item = item is not None

        item = self._on_get(key, item, **kwargs)

        if not exist_item and item:
            self.add(key, item)

        return item

    def _on_get(self, key: P, item: Optional[T]) -> Optional[T]:
        return item

    def refresh_key(self, key: P):
        self.lock()
        self._expired[key] = self._calc_exp()
        self.release()

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
        self._expired.pop(key)
        self.release()
        return item

    def pop_expired(self) -> Generator[T, None, None]:
        items = self.items()
        for key, item in items:
            self.lock()
            expired_in = self._expired.get(key)
            self.release()

            if datetime.datetime.utcnow() > expired_in:
                self.lock()
                result_time = self._expired.pop(key, None)
                result_item = self._db.pop(key, None)
                self.release()

                if result_item:
                    yield result_item
