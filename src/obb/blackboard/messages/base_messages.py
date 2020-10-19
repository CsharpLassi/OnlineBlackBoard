from dataclasses import dataclass

from .base_data_class import BaseDataClass

from obb.blackboard.components.session_manager import BlackBoardSessionToken


@dataclass
class BaseRequestMessage(BaseDataClass):
    token: str

    def get_session(self) -> BlackBoardSessionToken:
        return BlackBoardSessionToken.decode(self.token)

    session = property(get_session)


@dataclass
class BaseResponseMessage(BaseDataClass):
    pass
