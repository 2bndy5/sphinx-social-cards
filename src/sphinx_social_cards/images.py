import hashlib
import os
import platform
import re
import shutil
import subprocess
from typing import List, Union, Optional, cast, Tuple
from urllib.parse import urlparse, quote

from pathlib import Path
from PIL import Image, ImageSequence
from sphinx.util.logging import getLogger
from typing_extensions import Literal
from .validators import try_request
from .validators.layout import Size

LOGGER = getLogger(__name__)

IMG_PATH_TYPE = Optional[Union[str, Path]]


def get_magick_cmd(program="magick") -> Optional[str]:
    if "MAGICK_HOME" in os.environ:
        magick_home = Path(os.environ["MAGICK_HOME"], program)
        if platform.system().lower() == "windows":
            magick_home = magick_home.with_suffix(".exe")
        assert magick_home.exists()
        return str(magick_home)
    else:
        return shutil.which(program)


def find_image(
    img_name: IMG_PATH_TYPE,
    possible_locations: List[Union[str, Path]],
    doc_src: Union[str, Path],
    cache_dir: Union[str, Path],
) -> Optional[Path]:
    """Find the image file in pre-known possible locations."""
    if not img_name:  # None or ''
        return None
    if "://" in str(img_name):
        file_name = Path(cache_dir, quote(urlparse(str(img_name)).path, safe="."))
        if not file_name.suffix:
            file_name = file_name.with_suffix(".png")
        if not file_name.exists():
            response = try_request(str(img_name))
            file_name.write_bytes(response.content)
        img_name = file_name
    img_name = Path(img_name)
    if not img_name.suffix:
        img_name = img_name.with_suffix(".svg")
    if not img_name.is_absolute():
        rel_path = Path(doc_src, img_name)
        if rel_path.exists():
            return rel_path
    if img_name.exists():
        return img_name
    for loc in possible_locations + [Path(__file__).parent / ".icons"]:
        pos_path = Path(loc, img_name)
        if not pos_path.is_absolute():
            pos_path = Path(doc_src, pos_path)
        if pos_path.exists():
            return pos_path
    return None


_IDENTIFY_INFO = re.compile(r'^"DPI: ([^\s]*) SIZE: ([^x]*)x([^\s]*) UNITS: ([^"]*)"$')


def convert_svg(
    img_path: Path,
    cache: Union[str, Path],
    size: Size,
    imagemagick_version: Tuple[int, int, int],
) -> Path:
    out_name = (
        img_path.name
        + f"_{size.width}x{size.height}_"
        + hashlib.sha256(img_path.read_bytes()).hexdigest()[:16]
        + ".png"
    )
    out_path = Path(cache, out_name)
    if out_path.exists():
        return out_path
    img_in = f"'{str(img_path)}'" if " " in str(img_path) else str(img_path)
    img_out = f"'{str(out_path)}'" if " " in str(out_path) else str(out_path)

    magick_exe = get_magick_cmd("magick" if imagemagick_version >= (7,) else "identify")
    assert isinstance(magick_exe, str)
    magick_cmd = [
        magick_exe,
        "-format",
        '"DPI: %[fx:resolution.x] SIZE: %[fx:w]x%[fx:h] UNITS: %[units]"',
        img_in,
    ]
    if imagemagick_version >= (7,):
        magick_cmd.insert(1, "identify")

    # get size of svg via ImageMagick
    svg_info = subprocess.run(magick_cmd, check=True, capture_output=True)
    m = _IDENTIFY_INFO.match(svg_info.stdout.decode(encoding="utf-8"))
    assert (
        m is not None
    ), "ImageMagick identify output unrecognized:\n" + svg_info.stdout.decode(
        encoding="utf-8"
    )
    assert len(m.groups()) == 4, (
        "ImageMagick identify output is malformed. Captured data: %r" % m.groups()
    )
    dpi, w, h, svg_units = m.groups()
    if not dpi.isdecimal() or not dpi.isdigit():
        raise ValueError(f"Invalid DPI value: {dpi}")
    # NOTE: reported DPI can be 0 if Inkscape is not installed
    svg_dpi = float(dpi) or 96  # assume std DPI of 96 if 0 was reported
    if svg_units == "PixelsPerCentimeter":
        svg_dpi *= 2.54
    if not w.isdecimal() or not w.isdigit() or not h.isdecimal() or not h.isdigit():
        raise ValueError(f"Invalid width/height value(s): (w={w}, h={h})")
    svg_size = Size(width=int(w), height=int(h))  # can also raise ValueError

    # NOTE: Workaround clipping of converted small images when Inkscape is not
    # installed by telling ImageMagick to use an input canvas of enlarged -size
    # with -density applied.
    def _add_48(max_size: Size) -> Size:
        """add 48 to dimensions if any dimension is smaller than 48"""
        if max_size.width < 48 or max_size.height < 48:
            return Size(width=max_size.width + 48, height=max_size.height + 48)
        return max_size

    enlarged = _add_48(svg_size)
    enlarged = enlarged if enlarged > size else size
    new_dpi = svg_dpi
    if svg_size < enlarged:
        # resize SVG <path> elements using density of DPI based on original size
        if svg_size.height < svg_size.width:
            new_dpi = round(svg_dpi * (enlarged.height / svg_size.height))
        else:
            new_dpi = round(svg_dpi * (enlarged.width / svg_size.width))
    # LOGGER.info("new DPI: %s for %r (%s)", new_dpi, enlarged, out_name)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    magick_exe = get_magick_cmd("magick" if imagemagick_version >= (7,) else "convert")
    assert isinstance(magick_exe, str)
    magick_cmd = [
        magick_exe,
        "-background",
        "none",
        "-density",
        str(new_dpi),
        "-size",
        f"{enlarged.width}x{enlarged.height}",
        "-resize",
        f"{size.width}x{size.height}",
        img_in,
        img_out,
    ]
    if imagemagick_version >= (7,):
        magick_cmd.insert(1, "convert")

    subprocess.run(magick_cmd, check=True)
    return out_path


def resize_image(
    img_path: IMG_PATH_TYPE,
    cache: Union[str, Path],
    size: Size,
    aspect: Union[bool, Literal["width", "height"]],
    imagemagick_version: Tuple[int, int, int],
) -> Image.Image:
    """Resize an image according to specified `size`."""
    if img_path is None:
        return None
    img_path = Path(img_path)
    if img_path.suffix.lower() == ".svg":
        img_path = convert_svg(img_path, cache, size, imagemagick_version)
    img = Image.open(img_path)
    if hasattr(img, "n_frames"):
        img = cast(Image.Image, ImageSequence.all_frames(img.copy())[0])
        img = img.convert(mode="RGBA")
    w, h = img.size
    img.convert(mode="RGBA")
    if aspect and (size.width != w or size.height != h):
        if isinstance(aspect, str):
            if aspect == "width":
                ratio = w / size.width
            else:  # aspect == "height"
                ratio = h / size.height
        if isinstance(aspect, bool):
            if w > h:
                ratio = w / size.width
            else:
                ratio = h / size.height
        img = img.resize((int(w / ratio), int(h / ratio)))
        result = Image.new(mode="RGBA", size=(size.width, size.height))
        xy = tuple(int((i - j) / 2) for i, j in zip(result.size, img.size))
        result.paste(img, box=xy)
        return result
    return img


def overlay_color(img: Image.Image, color: str, mask: bool = False) -> Image.Image:
    if mask:
        base = Image.new(mode="RGBA", size=img.size)
        base.paste(color, mask=img)
        return base
    tint = Image.new(mode="RGBA", size=img.size, color=color)
    img.alpha_composite(tint)
    return img
