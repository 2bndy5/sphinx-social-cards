from typing import NamedTuple, Union, Sequence, cast, Tuple, List, Optional

from pydantic_extra_types.color import Color
from PySide6.QtGui import (
    QColor,
    QBrush,
    QGradient,
    QRadialGradient,
    QLinearGradient,
    QConicalGradient,
)

from .validators.common import (
    ColorType,
    Gradient,
    Linear_Gradient,
    Radial_Gradient,
    Conical_Gradient,
)
from .validators.layers import Offset


class ColorAttr(NamedTuple):
    #: The color used as the background fill color.
    fill: Union[QColor, QBrush]
    #: The color used for the foreground text.
    text: Union[QColor, QBrush]


#: The default color palette
MD_COLORS = {
    "red": "#ef5552",
    "pink": "#e92063",
    "purple": "#ab47bd",
    "deep-purple": "#7e56c2",
    "indigo": "#4051b5",
    "blue": "#2094f3",
    "light-blue": "#02a6f2",
    "cyan": "#00bdd6",
    "teal": "#009485",
    "green": "#4cae4f",
    "light-green": "#8bc34b",
    "lime": "#cbdc38",
    "yellow": "#ffec3d",
    "amber": "#ffc105",
    "orange": "#ffa724",
    "deep-orange": "#ff6e42",
    "brown": "#795649",
    "grey": "#757575",
    "blue-grey": "#546d78",
    "white": "#fff",
    "black": "#000",
}


def get_qt_color(color: Color) -> QColor:
    return QColor.fromHslF(*color.as_hsl_tuple(alpha=True))


def get_qt_gradient(
    color: Union[Linear_Gradient, Radial_Gradient, Conical_Gradient], offset: Offset
) -> Union[QLinearGradient, QRadialGradient, QConicalGradient]:
    assert isinstance(color, Gradient)
    if isinstance(color, Linear_Gradient):
        grad = QLinearGradient(
            color.start.x - offset.x,
            color.start.y - offset.y,
            color.end.x - offset.x,
            color.end.y - offset.y,
        )
    if isinstance(color, Radial_Gradient):
        grad = QRadialGradient(
            color.center.x - offset.x, color.center.y - offset.y, color.radius
        )
        if color.focal_point is not None:
            grad.setFocalPoint(
                color.focal_point.x - offset.x, color.focal_point.y - offset.y
            )
        if color.focal_radius is not None:
            grad.setFocalRadius(color.focal_radius)
    if isinstance(color, Conical_Gradient):
        grad = QConicalGradient(
            color.center.x - offset.x, color.center.y - offset.y, color.angle
        )
    if color.preset is not None:
        for p_grad in list(QGradient.Preset):
            if isinstance(color.preset, int) and color.preset == p_grad.value:
                grad.setStops(QGradient(p_grad).stops())
                break
            if isinstance(color.preset, str) and color.preset == p_grad.name:
                grad.setStops(QGradient(p_grad).stops())
                break
    if isinstance(color, (Radial_Gradient, Linear_Gradient)):
        grad.setSpread(QGradient.Spread[f"{color.spread.title()}Spread"])
    for pos, c_spec in color.colors.items():
        color = get_qt_color(c_spec)
        grad.setColorAt(pos, color)
    return grad


def get_luminance_contrast(rgba: Sequence[float]) -> float:
    """
    Calculate the luminance according to WCAG std (normalized in range [0, 1])
    NOTE: This does not account for transparency of a color.
    See https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
    """
    r, g, b = [
        c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgba[:3]
    ]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def auto_get_fg_color(color: ColorType) -> Color:
    luminance: Optional[float] = None
    assert isinstance(
        color, (Color, Linear_Gradient, Radial_Gradient, Conical_Gradient)
    ), "color should already be validated"
    if isinstance(color, Color):
        rgb = [c / 255 for c in color.as_rgb_tuple(alpha=False)]
        luminance = get_luminance_contrast(rgb)
    elif isinstance(color, (Linear_Gradient, Radial_Gradient, Conical_Gradient)):
        # Gradient colors can use a preset color list, a user-defined color list, or
        # an empty color list (in which default gradient is black to white).
        # We'll take the average of luminance contrast for each color & hope for the best
        gradient = get_qt_gradient(color, Offset(x=0, y=0))
        total = 0.0
        for _, grad_color in cast(List[Tuple[float, QColor]], gradient.stops()):
            total += get_luminance_contrast(
                [
                    grad_color.redF(),
                    grad_color.greenF(),
                    grad_color.blueF(),
                ]
            )
        luminance = total / len(gradient.stops())
    assert luminance is not None
    # WCAG mandates a contrast of 4.5 to 1. Here 0.451 is our tie-breaker
    return Color("black" if luminance > 0.451 else "white")
