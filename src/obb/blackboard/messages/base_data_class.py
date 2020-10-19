import dataclasses
from dataclasses import dataclass


@dataclass
class BaseDataClass:
    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
