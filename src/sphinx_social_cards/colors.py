from colorsys import rgb_to_hsv
from typing import NamedTuple

from PIL import ImageColor


class ColorAttr(NamedTuple):
    #: The color used as the background fill color.
    fill: str
    #: The color used for the foreground text.
    text: str


def auto_get_fg_color(color: str) -> str:
    """Takes a ``pillow`` compatible BG `color` and returns a legible FG color."""
    hsv = list(rgb_to_hsv(*[c / 255 for c in ImageColor.getrgb(color)][:3]))
    hsv[1] = 0
    # round the invert of brightness (round up to white for grey though)
    hsv[2] = round(1 - (hsv[2] - 0.01 if hsv[2] == 0.5 else hsv[2]))
    return (
        f"hsv({int(hsv[0] * 360)},"
        + ",".join([f"{int(c * 100)}%" for c in hsv[1:]])
        + ")"
    )


#: The default color palette
MD_COLORS = {
    "red": ColorAttr(fill="#ef5552", text="#fff"),
    "pink": ColorAttr(fill="#e92063", text="#fff"),
    "purple": ColorAttr(fill="#ab47bd", text="#fff"),
    "deep-purple": ColorAttr(fill="#7e56c2", text="#fff"),
    "indigo": ColorAttr(fill="#4051b5", text="#fff"),
    "blue": ColorAttr(fill="#2094f3", text="#fff"),
    "light-blue": ColorAttr(fill="#02a6f2", text="#fff"),
    "cyan": ColorAttr(fill="#00bdd6", text="#fff"),
    "teal": ColorAttr(fill="#009485", text="#fff"),
    "green": ColorAttr(fill="#4cae4f", text="#fff"),
    "light-green": ColorAttr(fill="#8bc34b", text="#fff"),
    "lime": ColorAttr(fill="#cbdc38", text="#000"),
    "yellow": ColorAttr(fill="#ffec3d", text="#000"),
    "amber": ColorAttr(fill="#ffc105", text="#000"),
    "orange": ColorAttr(fill="#ffa724", text="#000"),
    "deep-orange": ColorAttr(fill="#ff6e42", text="#fff"),
    "brown": ColorAttr(fill="#795649", text="#fff"),
    "grey": ColorAttr(fill="#757575", text="#fff"),
    "blue-grey": ColorAttr(fill="#546d78", text="#fff"),
    "white": ColorAttr(fill="#fff", text="#000"),
    "black": ColorAttr(fill="#000", text="#fff"),
}
