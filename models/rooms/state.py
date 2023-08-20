from ..base import CamelizingModel, TimerState
from typing import Any, Optional, TYPE_CHECKING
from datetime import timedelta, datetime


class BaseRoomState(CamelizingModel):
    slug: str
    state: TimerState = TimerState.READY
    extra_time: int = timedelta(seconds=0).seconds
    started_on: Optional[datetime] = None
    paused_on: Optional[datetime] = None
    stopped_on: Optional[datetime] = None
    completion: int = 0


class RoomStateOverview(BaseRoomState):
    stage: Optional[str] = None


class PuzzleState(CamelizingModel):
    slug: str
    completed: bool = False
    state: Optional[dict[str, Any]] = None


class StageState(CamelizingModel):
    slug: str
    puzzles: list[PuzzleState]


class RoomStateDetails(RoomStateOverview):
    active_stage: Optional[int] = None
    stages: list[StageState]
