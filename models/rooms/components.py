from enum import Enum
from pydantic import Extra, BaseModel
from ..base import CamelizingModel
from typing import Any, Optional, TYPE_CHECKING, TypeVar, Generic, Union, Literal
from typing import Annotated
from pydantic.functional_validators import BeforeValidator


class UIComponentType(str, Enum):
    DigitalState = "digitalState"
    Sequence = "sequence"
    SpeechDetection = "speechDetection"


class BaseComponent(CamelizingModel):
    type: UIComponentType
    complete_override_enabled: bool
    state_map: dict[str, str]
    name_map: Optional[dict[str, str]] = None


ComponentT = TypeVar("ComponentT", bound=BaseComponent)


class DigitalStateComponent(BaseComponent):
    type: Literal[UIComponentType.DigitalState]


class SequenceComponent(BaseComponent):
    length: int
    type: Literal[UIComponentType.Sequence]


class SpeechDetectionComponent(BaseComponent):
    type: Literal[UIComponentType.SpeechDetection]
    words: list[str]


CLASS_MAP: dict[str, type[BaseModel]] = {
    UIComponentType.DigitalState.value: DigitalStateComponent,
    UIComponentType.Sequence.value: SequenceComponent,
    UIComponentType.SpeechDetection.value: SpeechDetectionComponent,
}


def infer_component_type(data: dict):
    class_type = CLASS_MAP[data["type"]]
    return class_type.model_validate(data)


ComponentUnion = Union[
    DigitalStateComponent,
    SequenceComponent,
    SpeechDetectionComponent,
]

# TypeInferringComponent = Annotated[
#    ComponentUnion,
#    BeforeValidator(infer_component_type),
# ]
