from dataclasses import dataclass, field

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Response:
    success: bool
    item: object = field(default_factory=dict)
    errors: list = field(default_factory=list)
    count: int = 0
