from enum import Enum
from .base import CamelizingModel
from typing import Any, Optional, TYPE_CHECKING
from datetime import timedelta, datetime


class RoomState(str, Enum):
    READY = "ready"
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"
    STOPPED = "stopped"


class Room(CamelizingModel):
    id: int
    slug: str
    state: RoomState
    base_time: Optional[timedelta] = timedelta(hours=1)
    extra_time: Optional[timedelta] = timedelta(seconds=0)
    started_on: Optional[datetime] = None
    paused_on: Optional[datetime] = None
    stopped_on: Optional[datetime] = None
    completion: int = 0


class RoomDisplay(Room):
    name: str
    image_url: Optional[str]
    max_completion: int = 100
    stage: Optional[str]


class Puzzle(CamelizingModel):
    name: str
    completion_worth: int
    completed: bool
    state: Optional[dict[str, Any]]


class Stage(CamelizingModel):
    name: str
    description: Optional[str]
    puzzles: list[Puzzle]


class RoomDetails(RoomDisplay):
    stages: list[Stage]
    active_stage: int
