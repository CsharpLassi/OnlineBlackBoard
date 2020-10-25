from dataclasses import dataclass
from typing import TypeVar

from .base_message import BaseMessage

T = TypeVar('T')


@dataclass
class BaseRequest(BaseMessage):
    token: str


@dataclass
class SingleItemRequest(BaseRequest):
    item: T = None
