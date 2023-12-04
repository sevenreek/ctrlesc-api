from typing import Any, Optional, TYPE_CHECKING
from .base import CamelizingModel, TimerState
from .puzzle import AnyPuzzle, AnyPuzzleConfig, AnyPuzzleState, make_puzzle


class BaseStage(CamelizingModel):
    slug: str


class StageConfig(BaseStage):
    puzzles: list[AnyPuzzleConfig]
    name: str
    description: Optional[str]


class StageState(BaseStage):
    puzzles: list[AnyPuzzleState]


class Stage(StageConfig, StageState):
    puzzles: list[AnyPuzzle]


class BaseRoom(CamelizingModel):
    slug: str


class RoomConfig(BaseRoom):
    name: str
    stages: list[StageConfig]
    image_url: Optional[str]
    base_time: int

    @property
    def max_completion(self):
        return sum(
            (
                puzzle.completion_worth
                for stage in self.stages
                for puzzle in stage.puzzles
            )
        )


class RoomState(BaseRoom):
    active_stage: Optional[int] = None
    state: TimerState = TimerState.READY
    time_elapsed_on_pause: Optional[int] = None
    extra_time: int = 0
    stages: list[StageState]


class Room(RoomConfig, RoomState):
    stages: list[Stage]

    def __init__(self, config: RoomConfig, state: RoomState):
        stages: list[Stage] = []
        for stage_model, stage_state in zip(config.stages, state.stages, strict=True):
            puzzles = []
            for puzzle_model, puzzle_state in zip(
                stage_model.puzzles, stage_state.puzzles, strict=True
            ):
                puzzles.append(make_puzzle(puzzle_model, puzzle_state))
            stages.append(
                Stage(**stage_model.model_dump(exclude={"puzzles"}), puzzles=puzzles)
            )

        base_data = config.model_dump(exclude={"stages"}) | state.model_dump(
            exclude={"stages"}
        )
        super().__init__(**base_data, stages=stages)
