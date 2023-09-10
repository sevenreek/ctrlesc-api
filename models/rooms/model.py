from ..base import CamelizingModel, TimerState
from typing import Any, Optional, TYPE_CHECKING, Generic
from datetime import timedelta, datetime
from .components import ComponentUnion


class BaseRoomModel(CamelizingModel):
    slug: str
    name: str
    image_url: str
    base_time: int


class RoomModelOverview(BaseRoomModel):
    max_completion: int


class BasePuzzleModel(CamelizingModel):
    slug: str
    name: str
    completion_worth: int
    component: ComponentUnion


class InitialPuzzleModel(BasePuzzleModel):
    initial_state: Optional[dict[str, Any]]


class StageModel(CamelizingModel):
    slug: str
    name: str
    description: Optional[str] = None
    puzzles: list[InitialPuzzleModel]


class RoomModelDetail(BaseRoomModel):
    stages: list[StageModel]
