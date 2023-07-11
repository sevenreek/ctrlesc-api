from enum import Enum
from .base import CamelizingModel
from typing import Optional, TYPE_CHECKING
from datetime import timedelta, datetime


class RoomState(str, Enum):
    READY = "ready"
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"
    STOPPED = "stopped"


class RoomBase(CamelizingModel):
    id: int
    slug: str


class Room(RoomBase):
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


class RoomDetails(RoomDisplay):
    pass
