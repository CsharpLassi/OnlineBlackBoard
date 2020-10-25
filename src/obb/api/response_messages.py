from dataclasses import dataclass, field
from typing import List, TypeVar

from .base_message import BaseMessage

T = TypeVar('T')


@dataclass
class BaseResponse(BaseMessage):
    success: bool
    errors: List[str] = field(default=list)
    new_token: str = None


@dataclass
class SingleItemResponse(BaseResponse):
    item: T = None
