from pydantic import BaseModel
from humps import camelize


class CamelizingModel(BaseModel):
    class Config:
        alias_generator = camelize
        allow_population_by_field_name = True
