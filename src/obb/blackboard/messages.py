import dataclasses
from dataclasses import dataclass
from typing import List


@dataclass
class BaseMessageData:
    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class UserData(BaseMessageData):
    user_id: str
    username: str


@dataclass
class UserDataChangeData(BaseMessageData):
    username: str


@dataclass
class RoomData(BaseMessageData):
    room_id: int
    room_name: str
    draw_height: int


@dataclass
class RoomCreatedData(BaseMessageData):
    room: RoomData
    room_url: str


@dataclass
class RoomJoinedData(BaseMessageData):
    user: UserData
    room: RoomData


@dataclass()
class RoomUpdateSettingsData(BaseMessageData):
    room_id: int


@dataclass
class RoomUpdateContentData(BaseMessageData):
    room_id: int
    text: str


@dataclass
class RoomPrintData(BaseMessageData):
    text: str
    markdown: str
    creator: UserData = None


@dataclass
class StrokeData(BaseMessageData):
    @dataclass
    class StrokePoints(BaseMessageData):
        x: float
        y: float

    adaptiveStroke: bool
    color: str
    mode: str
    smoothing: float
    weight: int
    points: List[StrokePoints]


@dataclass
class RoomUpdateDrawData(BaseMessageData):
    room_id: int
    stroke: StrokeData


@dataclass
class RoomStrokeData(BaseMessageData):
    stroke: StrokeData
    creator: UserData = None
