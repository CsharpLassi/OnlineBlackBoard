from dataclasses import fields
from typing import TypeVar, Type

T = TypeVar('T')


def dataclass_from_dict(cls: Type[T], value_dict: dict) -> T:
    field_types = {f.name: f.type for f in fields(cls)}
    convert_dict = dict()
    for field_name, field_type in field_types.items():
        value = value_dict[field_name]
        if field_type is str:
            convert_dict[field_name] = str(value)
        elif field_type is int:
            convert_dict[field_name] = int(value)
        elif field_type is float:
            convert_dict[field_name] = float(value)
        else:
            convert_dict[field_name] = dataclass_from_dict(field_type, value)

    return cls(**convert_dict)
