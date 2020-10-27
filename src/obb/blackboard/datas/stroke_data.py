from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class StrokeData:
    @dataclass_json(letter_case=LetterCase.CAMEL)
    @dataclass
    class StrokePoints:
        x: float
        y: float

    adaptiveStroke: bool
    color: str
    mode: str
    smoothing: float
    weight: int
    points: List[StrokePoints]
