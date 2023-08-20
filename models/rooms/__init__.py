from models.rooms.model import RoomModel, PuzzleModel, StageModel, RoomModelDetail
from models.rooms.state import (
    RoomStateOverview,
    RoomStateDetails,
    PuzzleState,
    StageState,
)


class RoomOverview(RoomModel, RoomStateOverview):
    pass


class RoomDetails(RoomModelDetail, RoomStateDetails):
    pass


class Puzzle(PuzzleModel, PuzzleState):
    pass


class Stage(StageModel, StageState):
    pass
