from typing import Any, Optional, TYPE_CHECKING
from models.base import CamelizingModel
from models.rooms.model import (
    RoomModelOverview,
    PuzzleModel,
    StageModel,
    RoomModelDetail,
)
from models.rooms.state import (
    RoomStateOverview,
    RoomStateDetail,
    PuzzleState,
    StageState,
)


class Puzzle(CamelizingModel):
    slug: str
    name: str
    completion_worth: int
    completed: bool = False
    state: Optional[dict[str, Any]] = None
    component: dict[str, Any]


class Stage(StageModel, StageState):
    puzzles: list[Puzzle]


class RoomOverview(RoomModelOverview, RoomStateOverview):
    pass


class RoomDetail(RoomModelDetail, RoomStateDetail):
    def __init__(self, model: RoomModelDetail, state: RoomStateDetail):
        stages = []
        for stage_model, stage_state in zip(model.stages, state.stages, strict=True):
            puzzles = []
            for puzzle_model, puzzle_state in zip(
                stage_model.puzzles, stage_state.puzzles, strict=True
            ):
                puzzles.append(
                    Puzzle(
                        **(
                            puzzle_model.model_dump(exclude={"initial_state"})
                            | puzzle_state.model_dump()
                        )
                    )
                )
            stages.append(
                Stage(**stage_model.model_dump(exclude={"puzzles"}), puzzles=puzzles)
            )

        base_data = model.model_dump(exclude={"stages"}) | state.model_dump(
            exclude={"stages"}
        )
        super().__init__(**base_data, stages=stages)

    stages: list[Stage]
