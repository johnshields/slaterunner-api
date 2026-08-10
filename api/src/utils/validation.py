from enum import Enum
from typing import TypeVar

T = TypeVar("T", bound=Enum)


def normalize_input(value: str | None, enum_cls: type[T]) -> T | None:
    """Normalize input string to match enum value case-insensitively."""
    if value is None:
        return None

    for member in enum_cls:
        if member.value.lower() == value.lower():
            return member

    raise ValueError(f"Invalid Enum value: {value}. Must be one of {[m.value for m in enum_cls]}")

