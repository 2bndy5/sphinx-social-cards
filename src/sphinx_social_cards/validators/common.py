import math
from pathlib import Path
from typing import Optional, Dict, Union, Any, cast

from pydantic import (
    BaseModel as PydanticBaseModel,
    field_validator,
    field_serializer,
    Field,
    ConfigDict,
    AfterValidator,
    FieldValidationInfo,
)
from pydantic_extra_types.color import Color
from PySide6.QtGui import QGradient
from typing_extensions import Annotated, Literal


def _validate_path(val: Union[str, Path]) -> str:
    val = Path(val)
    if val.is_absolute() and not val.exists():
        raise FileNotFoundError(f"{str(val)} does not exist")
    # relative paths must be resolved at runtime depending on conf.py location
    return str(val)


PathType = Annotated[Union[str, Path], AfterValidator(_validate_path)]
PositiveFloat = Annotated[float, Field(gt=0)]


class CustomBaseModel(PydanticBaseModel):
    model_config = ConfigDict(
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


class Gradient(CustomBaseModel):
    """A specification that defines a color gradient."""

    colors: Dict[Annotated[float, Field(ge=0.0, le=1.0)], Color] = {}
    """A mapping of colors to their corresponding positions in the gradient.
    Each item in this mapping is composed of :yaml:`key: value` pairs in which:

    - The :yaml:`key:` is a position at which the color will occur in the gradient.
      This `float` *must* be in the range ``0`` to ``1`` inclusively. More detail about
      how these positional values are used is described in |gradient_positions|.
    - The :yaml:`value` is a :ref:`solid color <solid_color>` to use at the specified
      point in the gradient.

    This mapping's color positions does not have to be in any specific order. If using
    a `preset`, then this mapping will override colors in the preset's mapping of
    colors. When neither the `preset` or `colors` is specified, this defaults to
    :yaml:`0.0: black` and :yaml:`1.0: white`.

    .. |rel_root_offset| replace:: relative to the layout's `offset <Offset>` (the
        absolute top-left corner of the card).
    .. |color-pos| replace:: position in the mapping of `colors`.
    """
    preset: Optional[Union[str, int]] = None
    """An optional preset gradient that has a pre-defined mapping of `colors`. Each
    preset is referenced by name (string) or by index (integer). See the :doc:`presets`
    document for a complete list of supported values (with generated examples).
    """

    @field_validator("preset")
    def validate_preset(cls, val: Union[str, int]) -> Union[str, int]:
        supported = [p for p in list(QGradient.Preset) if p.name != "NumPresets"]
        assert isinstance(val, (str, int))
        if isinstance(val, str) and " " in val:
            val = val.title().replace(" ", "")
        if isinstance(val, str) and val not in [g.name for g in supported]:
            raise ValueError(f"{val} is not a valid preset gradient name")
        if isinstance(val, int) and val not in [g.value for g in supported]:
            raise ValueError(f"{val} is not a valid preset gradient index")
        return val

    @field_serializer("colors")
    def serialize_color_list(self, val: Dict[float, Color]) -> Dict[float, str]:
        return {k: v.as_rgb() for k, v in val.items()}


class Conical_Gradient(Gradient):
    """A specification for linear gradients of colors.

    .. failure:: ``spread`` not applicable to conical gradients

        Conceptually, the ``spread`` feature of other gradients can not be applied to
        conical gradients because conical gradients are implemented using the polar
        coordinate system.
    """

    center: Offset
    """The starting position (`offset <Offset>`) |rel_root_offset| This offset
    corresponds to the minimum ``0.0`` |color-pos|"""
    angle: float
    """The angle of the the line from `center` the represents the gradient's start and
    stop limits. This value (in degrees) is clamped to a value greater than or equal to
    0 and less than 360. The angle of origin (``0`` degrees) is located at 3 o'clock and
    increases counter-clockwise. The scale of listed `colors` begins at ``0.0`` on this
    line and continues counter-clockwise until ending at ``1.0`` on this line.

    .. jinja::

        .. md-tab-set::

            {% for angle in [-45, 0, 45, 180] %}

            .. md-tab-item:: :yaml:`angle: {{ angle }}`

                .. social-card::
                    :dry-run:

                    size: { height: 400, width: 400 }
                    layers:
                      - ellipse:
                          conical_gradient:
                            center: { x: 200, y: 200 }
                            angle: {{ angle }}
                            colors:
                              0.0: red
                              0.5: green
                              1.0: blue
            {% endfor %}
    """
    colors: Dict[Annotated[float, Field(ge=0.0, le=1.0)], Color] = {}

    @field_validator("angle")
    def clamp_angle(cls, val: float) -> float:
        while val < 0:
            val += 360
        while val >= 360:
            val -= 360
        return val


class GradientSpread(CustomBaseModel):
    spread: Literal["pad", "reflect", "repeat"] = "pad"
    """This attribute controls the colors' behavior outside the gradient's specified
    area. By default this is set to :yaml:`pad`."""


class Linear_Gradient(Gradient, GradientSpread):
    """A specification for linear gradients of colors."""

    start: Offset
    """The starting position (`offset <Offset>`) |rel_root_offset| This offset
    corresponds to the minimum ``0.0`` |color-pos|"""
    end: Offset
    """The ending position (`offset <Offset>`) |rel_root_offset| This offset
    corresponds to the maximum ``1.0`` |color-pos|"""
    colors: Dict[Annotated[float, Field(ge=0.0, le=1.0)], Color] = {}


class Radial_Gradient(Gradient, GradientSpread):
    """A specification for linear gradients of colors."""

    center: Offset
    """The starting position (`offset <Offset>`) |rel_root_offset| This offset
    corresponds to the minimum ``0.0`` |color-pos|"""
    radius: PositiveFloat
    """The radius represents the ending position as a distance (in pixels) from the
    specified `center` `offset <Offset>`. The resulting circumference corresponds to the
    maximum ``1.0`` |color-pos|

    .. warning::
        This radius *must* be a greater than 0.

    .. jinja::

        .. md-tab-set::

            {% for radius in [50, 100, 200, 250] %}

            .. md-tab-item:: :yaml:`radius: {{ radius }}`

                .. social-card::
                    :dry-run:

                    size: { height: 400, width: 400 }
                    layers:
                      - background:
                          radial_gradient:
                            center: { x: 200, y: 200 }
                            radius: {{ radius }}
                            colors:
                              0.0: red
                              # show the end of the radius by setting color at
                              # maximum position to the background color
                              0.9999: green
                              1.0: blue
            {% endfor %}
    """
    focal_point: Optional[Offset] = None
    """The focal point (`offset <Offset>`) used to give the gradient a perspective.
    By default, the value of `center` is used. If the specified `offset <Offset>` is
    outside the circumference defined via `radius`, then this `offset <Offset>` will
    be moved to the outer-most point on the circle that would be formed by the `radius`
    from the `center`.

    .. jinja::

        .. md-tab-set::

            {% for i in range(2) %}
            {% if not i %}
            {% set point = 'focal_point: { x: 100, y: 100 }' %}
            {% else %}
            {% set point = 'focal_point: null' %}
            {% endif %}

            .. md-tab-item:: :yaml:`{{ point }}`

                .. social-card::
                    :dry-run:

                    size: { height: 400, width: 400 }
                    layers:
                      - background: { color: blue }
                      - ellipse:
                          radial_gradient:
                            center: { x: 200, y: 200 }
                            radius: 200
                            {{ point }}  {% if i -%}
                            # the default (uses center offset){% endif %}
                            colors:
                              0.0: red
                              1.0: green
            {% endfor %}
    """
    focal_radius: Optional[float] = None
    """The radius from the `focal_point` defines the aperture width of the gradient's
    perspective. This is highly relative to the `center`'s `radius`. Furthermore, if the
    `focal_radius` forms a circumference than extends beyond the `center`'s `radius`,
    then the gradient is effectively nullified and treated like a solid color (which
    coincides with the `colors` list maximum position, 1.0).

    .. example:: Using :yaml:`spread: repeat` as a proof

        The following example uses the :yaml:`repeat` `spread` to show the
        `focal_radius` area. Remember that the :yaml:`repeat` `spread` effectively
        repeats the gradient outside the gradient's effected area (using the same order
        of `colors`).

    .. jinja::

        .. md-tab-set::

            {% for radius in [-100, 0, 50, 58] %}

            .. md-tab-item:: :yaml:`focal_radius: {{ radius }}`

                .. social-card::
                    :dry-run:

                    size: { height: 400, width: 400 }
                    layers:
                      - background: { color: blue }
                      - ellipse:
                          radial_gradient:
                            center: { x: 200, y: 200 }
                            radius: 200
                            focal_radius: {{ radius }} {% if radius == 0 -%}
                            # the default value if not specified{% endif %}
                            focal_point: { x: 100, y: 100 }
                            colors:
                              0.0: red
                              1.0: green
                            spread: repeat
            {% endfor %}
    """
    colors: Dict[Annotated[float, Field(ge=0.0, le=1.0)], Color] = {}

    @field_validator("focal_radius")
    def constrain_focal_radius(cls, val: float, info: FieldValidationInfo) -> float:
        # the radius is a required field, so get that value
        assert "radius" in info.data
        radius = cast(float, info.data["radius"])
        err_msg = (
            f"The focal_radius {val} at focal_point (x: %d, y: %d) extends %f pixels "
            + f"beyond the radius {radius} (from center)"
        )
        if "focal_point" in info.data and info.data["focal_point"] is not None:
            point = cast(Offset, info.data["focal_point"])
        else:
            assert "center" in info.data
            point = cast(Offset, info.data["center"])
        dist2focal = math.sqrt(math.pow(point.x, 2) + math.pow(point.y, 2))
        max_dist = dist2focal + max(0, val)
        if max_dist > radius:
            raise ValueError(err_msg % (point.x, point.y, max_dist - radius))
        return val


ColorType = Union[Color, Linear_Gradient, Radial_Gradient, Conical_Gradient]


def serialize_color(color: Optional[ColorType]) -> Optional[Union[str, Dict[str, Any]]]:
    if color is None:
        return None
    assert isinstance(color, (Color, Gradient))
    if isinstance(color, Gradient):
        return color.model_dump()
    return color.as_rgb()
