import dataclasses
from dataclasses import dataclass


@dataclass
class RoomCreatedData:
    room_id: str
    room_url: str

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)
