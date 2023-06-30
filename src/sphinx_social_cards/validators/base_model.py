from pydantic import BaseModel as PydanticBaseModel, Extra


class CustomBaseModel(PydanticBaseModel):
    class Config:
        extra = Extra.forbid
        validate_assignment = True
        anystr_strip_whitespace = True
