from .base_messages import BaseRequestMessage
from .datas import *


@dataclass
class JoinRequestMessage(BaseRequestMessage):
    pass


@dataclass
class RoomUpdateContentRequestMessage(BaseRequestMessage):
    raw_text: str


@dataclass
class RoomDrawRequestMessage(BaseRequestMessage):
    stroke: StrokeData


@dataclass()
class RoomUpdateSettingsRequestMessage(BaseRequestMessage):
    pass


@dataclass()
class RoomUpdateUserRequestMessage(BaseRequestMessage):
    user_id: str
    allow_draw: bool = None
