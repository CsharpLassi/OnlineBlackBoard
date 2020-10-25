from dataclasses import dataclass

from obb.blackboard.messages.base_messages import BaseResponseMessage


@dataclass
class RoomUpdatedMessage(BaseResponseMessage):
    page_id: int
    width: int
    height: int

    has_left_page: bool
    has_right_page: bool
