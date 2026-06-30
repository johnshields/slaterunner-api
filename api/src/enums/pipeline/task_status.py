from enum import Enum


class TaskStatus(str, Enum):
    WIP = "WIP"
    READY = "READY"
    HOLD = "HOLD"
    DONE = "DONE"
