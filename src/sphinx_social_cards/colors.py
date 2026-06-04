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


def auto_get_fg_color(color: str) -> str:
    """Return 'black' or 'white' depending on luminance of the given CSS color string.

    Accepts hex colors and named CSS colors. Certain named colors are be resolved into
    RGB components via MD_COLORS by this function.
    """
    _color = img_gen.SolidColor.from_string(MD_COLORS.get(color, color))
    fg = _color.get_foreground_color()
    is_black = fg.to_tuple()[:3] == (0, 0, 0)
    return "black" if is_black else "white"
