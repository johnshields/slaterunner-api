from enum import Enum


class AssetType(str, Enum):
    Vehicle = "Vehicle"
    Creature = "Creature"
    Character = "Character"
    Effect = "Effect"
    Environment = "Environment"
