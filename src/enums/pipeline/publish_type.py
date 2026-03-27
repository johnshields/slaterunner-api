from enum import Enum


class PublishType(str, Enum):
    geo = "geo"
    rig = "rig"
    comp = "comp"
    fx = "fx"
    layout = "layout"
    prep = "prep"
    tex = "tex"
