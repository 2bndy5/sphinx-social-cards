import hashlib
import os
import platform
import re
import subprocess
from typing import List, Union, Optional, cast
from urllib.parse import urlparse, quote

from pathlib import Path
from PIL import Image, ImageSequence
from sphinx.util.logging import getLogger
from typing_extensions import Literal
from .validators import try_request
from .validators.layout import Size

LOGGER = getLogger(__name__)

IMG_PATH_TYPE = Optional[Union[str, Path]]


def get_magick_cmd() -> str:
    magick_path = "magick"
    if "MAGICK_HOME" in os.environ:
        magick_home = Path(os.environ["MAGICK_HOME"], magick_path)
        if platform.system().lower() == "windows":
            magick_home = magick_home.with_suffix(".exe")
        assert magick_home.exists()
        magick_path = str(magick_home)
    return magick_path


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
            if response.status_code != 200:
                return None
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


_IDENTIFY_INFO = re.compile(r"DPI: (\d+) SIZE: (\d+)x(\d+)")


def convert_svg(img_path: Path, cache: Union[str, Path], size: Size) -> Path:
    out_name = (
        img_path.name
        + f"_{size.width}x{size.height}_"
        + hashlib.sha256(img_path.read_bytes()).hexdigest()[:16]
        + ".png"
    )
    out_path = Path(cache, out_name)
    if out_path.exists():
        return out_path

    magick_path = get_magick_cmd()

    # get size of svg via ImageMagick
    svg_info = subprocess.run(
        [
            magick_path,
            "identify",
            "-format",
            "DPI: %[fx:resolution.x] SIZE: %[fx:w]x%[fx:h]",
            str(img_path),
        ],
        check=True,
        shell=True,
        capture_output=True,
    )
    m = _IDENTIFY_INFO.search(svg_info.stdout.decode(encoding="utf-8"))
    assert m is not None and isinstance(m, re.Match) and len(m.groups()) == 3
    svg_dpi, w, h = [int(x) for x in m.groups()]
    svg_size = Size(width=w, height=h)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    magick_cmd = [magick_path, "-background", "none", str(img_path), str(out_path)]

    if size.width > svg_size.width or size.height > svg_size.height:
        # resize svg using density of DPI based on original size
        if size.height < size.width:
            new_dpi = int(svg_dpi * (size.height / svg_size.height))
        else:
            new_dpi = int(svg_dpi * (size.width / svg_size.width))
        # LOGGER.info("new DPI: %s", new_dpi)
        magick_cmd.insert(1, "-density")
        magick_cmd.insert(2, str(new_dpi))

    subprocess.run(magick_cmd, shell=True, check=True)
    return out_path


def resize_image(
    img_path: IMG_PATH_TYPE,
    cache: Union[str, Path],
    size: Size,
    aspect: Union[bool, Literal["width", "height"]],
) -> Image.Image:
    """Resize an image according to specified `size`."""
    if img_path is None:
        return None
    img_path = Path(img_path)
    if img_path.suffix.lower() == ".svg":
        img_path = convert_svg(img_path, cache, size)
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
