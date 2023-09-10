from typing import Any, Optional, TYPE_CHECKING
from ..base import CamelizingModel
from ..rooms.model import (
    RoomModelOverview,
    BasePuzzleModel,
    StageModel,
    RoomModelDetail,
    ComponentUnion,
)
from ..rooms.state import (
    RoomStateOverview,
    RoomStateDetail,
    PuzzleState,
    StageState,
)


class Puzzle(BasePuzzleModel, PuzzleState):
    pass


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
