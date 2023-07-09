from pydantic import BaseModel as PydanticBaseModel


class CustomBaseModel(PydanticBaseModel):
    model_config = dict(
        extra="forbid",
        validate_assignment=True,
        str_strip_whitespace=True,
    )


# this class is defined here to avoid a circular import
class Offset(CustomBaseModel):
    """An attribute to describe a layer's positional offset."""

    x: int = 0
    """The offset on the X axis (relative to the top-left corner of the card). Defaults
    to 0."""
    y: int = 0
    """The offset on the Y axis (relative to the top-left corner of the card). Defaults
    to 0."""
