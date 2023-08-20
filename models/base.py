from pydantic import ConfigDict, BaseModel
from humps import camelize
from enum import Enum


class CamelizingModel(BaseModel):
    model_config = ConfigDict(alias_generator=camelize, populate_by_name=True)


class TimerState(str, Enum):
    READY = "ready"
    ACTIVE = "active"
    PAUSED = "paused"
    FINISHED = "finished"
    STOPPED = "stopped"
