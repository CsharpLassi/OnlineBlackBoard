from dataclasses import dataclass

from .base_messages import BaseResponseMessage
from .datas import *


@dataclass
class UserJoinedResponse(BaseResponseMessage):
    user: UserData
    room: RoomData


@dataclass
class UserLeaveResponse(BaseResponseMessage):
    user: UserData
    room: RoomData


@dataclass
class RoomPrintResponse(BaseResponseMessage):
    raw_text: str
    markdown: str
    creator: UserData = None


@dataclass
class RoomDrawResponseMessage(BaseResponseMessage):
    stroke: StrokeData
    creator: UserData = None


@dataclass()
class RoomUpdateSettingsResponseMessage(BaseResponseMessage):
    content_draw_height: int


@dataclass()
class RoomUpdateUserResponseMessage(BaseResponseMessage):
    user: UserData