from .base_messages import BaseRequestMessage
from .datas import *


@dataclass
class JoinRequestMessage(BaseRequestMessage):
    pass


@dataclass
class RoomUpdateContentRequestMessage(BaseRequestMessage):
    raw_text: str


@dataclass
class RoomGetContentRequestMessage(BaseRequestMessage):
    page: int = 0


@dataclass
class RoomDrawRequestMessage(BaseRequestMessage):
    stroke: StrokeData


@dataclass
class RoomGetDrawRequestMessage(BaseRequestMessage):
    page: int = 0


@dataclass()
class RoomUpdateSettingsRequestMessage(BaseRequestMessage):
    pass


@dataclass()
class RoomUpdateUserRequestMessage(BaseRequestMessage):
    user_id: str
    allow_draw: bool = None
