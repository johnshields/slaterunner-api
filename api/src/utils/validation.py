from typing import Optional, Type, TypeVar
from enum import Enum

T = TypeVar("T", bound=Enum)


def normalize_input(value: Optional[str], enum_cls: Type[T]) -> Optional[T]:
    """Normalize input string to match enum value case-insensitively."""
    if value is None:
        return None

    for member in enum_cls:
        if member.value.lower() == value.lower():
            return member

    raise ValueError(f"Invalid Enum value: {value}. Must be one of {[m.value for m in enum_cls]}")

