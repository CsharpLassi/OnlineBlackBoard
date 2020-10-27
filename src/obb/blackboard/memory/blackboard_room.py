from dataclasses import dataclass

from dataclasses_json import LetterCase, dataclass_json

from ..models import BlackboardRoom, BlackBoardRoomData


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class MemoryBlackboardRoomData:
    base: BlackBoardRoomData


class MemoryBlackboardRoom:
    def __init__(self, id: str):
        self.id = id
        self.users = set()

    def get_data(self) -> MemoryBlackboardRoomData:
        return MemoryBlackboardRoomData(
            base=self.model.get_data()
        )

    @property
    def model(self) -> BlackboardRoom:
        return BlackboardRoom.get(self.id)
