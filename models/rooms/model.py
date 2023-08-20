from enum import Enum
from ..base import CamelizingModel, TimerState
from typing import Any, Optional, TYPE_CHECKING
from datetime import timedelta, datetime


class UIComponentType(str, Enum):
    DigitalState = "digitalState"


class RoomModel(CamelizingModel):
    slug: str
    name: str
    image_url: str
    base_time: int = timedelta(hours=1).seconds
    max_completion: int = 100


class PuzzleModel(CamelizingModel):
    slug: str
    name: str
    completion_worth: int
    component: dict[str, Any]
    initial_state: Optional[dict[str, Any]]


class StageModel(CamelizingModel):
    slug: str
    name: str
    description: Optional[str] = None
    puzzles: list[PuzzleModel]


class RoomModelDetail(RoomModel):
    stages: list[StageModel]
