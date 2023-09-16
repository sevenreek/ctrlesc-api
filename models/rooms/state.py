from ..base import CamelizingModel, TimerState
from typing import Any, Optional, TYPE_CHECKING
from datetime import timedelta, datetime
from pydantic import ConfigDict


class BaseRoomState(CamelizingModel):
    slug: str
    state: TimerState
    extra_time: int
    started_on: Optional[datetime] = None
    paused_on: Optional[datetime] = None
    stopped_on: Optional[datetime] = None


class BaseRoomStateInput(BaseRoomState):
    state: TimerState = TimerState.READY
    extra_time: int = 0


class RoomStateOverviewInput(BaseRoomStateInput):
    stage: Optional[str] = None
    completion: int = 0


class RoomStateOverview(BaseRoomState):
    stage: Optional[str] = None
    completion: int = 0


class PuzzleState(CamelizingModel):
    slug: str
    completed: bool = False
    state: Optional[dict[str, Any]] = None


class StageState(CamelizingModel):
    slug: str
    puzzles: list[PuzzleState]


class RoomStateDetailInput(RoomStateOverviewInput):
    active_stage: Optional[int] = None
    stages: list[StageState]


class RoomStateDetail(RoomStateOverview):
    active_stage: Optional[int] = None
    stages: list[StageState]
