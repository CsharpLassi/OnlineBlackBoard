import dataclasses
from dataclasses import dataclass


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


@dataclass
class RoomCreatedData(BaseMessageData):
    room: RoomData
    room_url: str


@dataclass
class RoomJoinedData(BaseMessageData):
    user: UserData
    room: RoomData


@dataclass
class RoomUpdateContentData(BaseMessageData):
    room_id: int
    text: str


@dataclass
class RoomPrintData(BaseMessageData):
    text: str
    markdown: str
    creator: UserData = None
