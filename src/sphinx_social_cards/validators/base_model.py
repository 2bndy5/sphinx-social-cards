from pydantic import BaseModel as PydanticBaseModel


class CustomBaseModel(PydanticBaseModel):
    model_config = dict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )
