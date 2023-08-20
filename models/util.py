from pydantic import BaseModel
from inspect import Signature


def extract_model_default_fields(model_class: type[BaseModel]):
    return {
        param_name: param.default
        for param_name, param in model_class.__signature__.parameters.items()
        if param.default != Signature.empty
    }
