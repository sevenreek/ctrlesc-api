from enum import Enum
from pydantic import Extra, BaseModel, Field
from .base import CamelizingModel
from typing import Any, Optional, TYPE_CHECKING, TypeVar, Generic, Union, Literal
from typing import Annotated
from pydantic.functional_validators import BeforeValidator
from typing_extensions import Annotated


class PuzzleType(str, Enum):
    DigitalState = "digitalState"
    Sequence = "sequence"
    SpeechDetection = "speechDetection"


class BasePuzzleConfig(CamelizingModel):
    slug: str
    name: str
    completion_worth: int
    type: PuzzleType
    complete_override_enabled: bool
    state_map: dict[str, str]
    name_map: Optional[dict[str, str]] = None
    initial_state: Any


class BasePuzzleState(CamelizingModel):
    slug: str
    completed: bool = False
    type: PuzzleType
    state: Any


# Digital State
class DigitalStatePuzzleConfig(BasePuzzleConfig):
    type: Literal[PuzzleType.DigitalState]


class DigitalStatePuzzleState(BasePuzzleState):
    type: Literal[PuzzleType.DigitalState]
    state: dict[str, bool]


class DigitalStatePuzzle(DigitalStatePuzzleConfig, DigitalStatePuzzleState):
    pass


# Sequence
class SequencePuzzleConfig(BasePuzzleConfig):
    type: Literal[PuzzleType.Sequence]
    target_state: list[Any]


class SequencePuzzleState(BasePuzzleState):
    type: Literal[PuzzleType.Sequence]
    state: list[Any]


class SequencePuzzle(SequencePuzzleConfig, SequencePuzzleState):
    pass


# Speech Detection
class SpeechDetectionPuzzleConfig(BasePuzzleConfig):
    type: Literal[PuzzleType.SpeechDetection]
    phrases: list[str]


class SpeechDetectionAttempt(CamelizingModel):
    phrase: str
    confidence: float
    match_level: float


class SpeechDetectionPuzzleStateObject(CamelizingModel):
    current_phrase: int
    last_attempts: list[SpeechDetectionAttempt]


class SpeechDetectionPuzzleState(BasePuzzleState):
    type: Literal[PuzzleType.SpeechDetection]
    state: SpeechDetectionPuzzleStateObject


class SpeechDetectionPuzzle(SpeechDetectionPuzzleConfig, SpeechDetectionPuzzleState):
    pass


CONFIG_CLASS_MAP: dict[str, type[BaseModel]] = {
    PuzzleType.DigitalState.value: DigitalStatePuzzleConfig,
    PuzzleType.Sequence.value: SequencePuzzleConfig,
    PuzzleType.SpeechDetection.value: SpeechDetectionPuzzleConfig,
}

STATE_CLASS_MAP: dict[str, type[BaseModel]] = {
    PuzzleType.DigitalState.value: DigitalStatePuzzleState,
    PuzzleType.Sequence.value: SequencePuzzleState,
    PuzzleType.SpeechDetection.value: SpeechDetectionPuzzleState,
}

PUZZLE_CLASS_MAP: dict[str, type[BaseModel]] = {
    PuzzleType.DigitalState.value: DigitalStatePuzzle,
    PuzzleType.Sequence.value: SequencePuzzle,
    PuzzleType.SpeechDetection.value: SpeechDetectionPuzzle,
}

AnyPuzzleConfig = Annotated[
    Union[
        DigitalStatePuzzleConfig,
        SequencePuzzleConfig,
        SpeechDetectionPuzzleConfig,
    ],
    Field(discriminator="type"),
]

AnyPuzzleState = Annotated[
    Union[
        DigitalStatePuzzleState,
        SequencePuzzleState,
        SpeechDetectionPuzzleState,
    ],
    Field(discriminator="type"),
]


AnyPuzzle = Annotated[
    Union[
        DigitalStatePuzzle,
        SequencePuzzle,
        SpeechDetectionPuzzle,
    ],
    Field(discriminator="type"),
]


def make_puzzle(config: BasePuzzleConfig, state: AnyPuzzleState):
    """Returns an instance of the appropriate puzzle type
    based on the .type property of the provided config.

    Args:
        config (BasePuzzleConfig): A puzzle config class.

    Returns:
        AnyPuzzle: A puzzle.
    """
    class_type = PUZZLE_CLASS_MAP[config.type]
    return class_type.model_validate({**config.model_dump(), **state.model_dump()})


def infer_puzzle_config(data: dict):
    """Returns an instance of the appropriate puzzle config type
    based on the .type property of the provided dict.

    Args:
        data (dict): A dict built from a configuration JSON of a puzzle.

    Returns:
        AnyPuzzleConfig: A puzzle config class.
    """
    class_type = CONFIG_CLASS_MAP[data["type"]]
    return class_type.model_validate(data)


def infer_puzzle_state(data: dict):
    """Returns an instance of the appropriate puzzle state type
    based on the .type property of the provided dict.

    Args:
        data (dict): A dict built from a configuration JSON of a puzzle.

    Returns:
        AnyPuzzleConfig: A puzzle state class.
    """
    class_type = STATE_CLASS_MAP[data["type"]]
    return class_type.model_validate(data)
