from dataclasses import dataclass
from typing import List

from .base_data_class import BaseDataClass


@dataclass
class UserData(BaseDataClass):
    user_id: str
    username: str


@dataclass
class RoomData(BaseDataClass):
    room_id: str
    room_name: str





@dataclass
class StrokeData(BaseDataClass):
    @dataclass
    class StrokePoints(BaseDataClass):
        x: float
        y: float

    adaptiveStroke: bool
    color: str
    mode: str
    smoothing: float
    weight: int
    points: List[StrokePoints]



