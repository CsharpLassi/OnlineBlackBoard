from dataclasses import dataclass

from obb.tools import dataclasses


@dataclass
class BaseMessage:
    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
