from typing import Sequence
import img_gen


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


def get_luminance_contrast(rgba: Sequence[float]) -> float:
    """
    Calculate the luminance according to WCAG std (normalized in range [0, 1])
    NOTE: This does not account for transparency of a color.
    See https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
    """
    r, g, b = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgba[:3]]
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def auto_get_fg_color(color: str) -> str:
    """Return 'black' or 'white' depending on luminance of the given CSS color string.

    Accepts hex colors (#rgb or #rrggbb). Named colors should be resolved to hex via
    MD_COLORS before calling this function.
    """
    css_color = img_gen.SolidColor.from_string(color)
    default_color = "".join([hex(c)[2:] for c in css_color.to_tuple()[:3]])
    hex_color = MD_COLORS.get(color, default_color)
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r = int(hex_color[0:2], 16) / 255
    g = int(hex_color[2:4], 16) / 255
    b = int(hex_color[4:6], 16) / 255
    luminance = get_luminance_contrast([r, g, b])
    return "black" if luminance > 0.451 else "white"
