from enum import Enum
from typing import Set


class ExtendEnum(Enum):
    @classmethod
    def list(cls) -> Set["str"]:
        return set(map(lambda c: c.value, cls))
