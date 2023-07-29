from logging import getLogger
from pathlib import Path
from typing import List, Union, Optional, cast, Tuple
from urllib.parse import urlparse, quote

from PySide6.QtGui import QImage, QImageReader, QPainter, QBrush
from PySide6.QtCore import Qt, QSize, QRect
from PySide6.QtGui import QColor
from PySide6.QtSvg import QSvgRenderer
from typing_extensions import Literal
from .validators import try_request
from .validators.layout import Size

LOGGER = getLogger(__name__)

IMG_PATH_TYPE = Optional[Union[str, Path]]


def find_image(
    img_name: IMG_PATH_TYPE,
    possible_locations: List[Union[str, Path]],
    doc_src: Union[str, Path],
    cache_dir: Union[str, Path],
) -> Optional[Path]:
    """Find the image file in pre-known possible locations."""
    if not img_name:
        return None
    if "://" in str(img_name):
        url = str(img_name).strip()
        file_name = Path(cache_dir, quote(urlparse(url).path, safe="."))
        if not file_name.suffix:
            file_name = file_name.with_suffix(".png")
        if not file_name.exists():
            response = try_request(url)
            file_name.write_bytes(response.content)
        img_name = file_name
    if isinstance(img_name, str):
        img_name.strip()
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


def render_svg(img_path: IMG_PATH_TYPE, size: Size) -> QImage:
    svg = QSvgRenderer(str(img_path))
    svg_size = svg.defaultSize()
    svg.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
    tgt_size = QSize(size.width, size.height)
    if any([size.width != svg_size.width(), size.height != svg_size.height()]):
        if svg_size.width() < svg_size.height():
            svg_size = QSize(
                svg_size.width() * size.height / svg_size.height(), size.height
            )
        else:  # svg_size.height() <= svg_size.width():
            svg_size = QSize(
                size.width, svg_size.height() * size.width / svg_size.width()
            )
    else:
        svg_size = tgt_size
    img = QImage(svg_size, QImage.Format.Format_ARGB32_Premultiplied)
    img.fill(Qt.GlobalColor.transparent)  # creates a color table
    with QPainter(img) as painter:
        svg.render(painter)
    if not all([svg_size.width() == size.width, svg_size.height() == size.height]):
        padding = QImage(tgt_size, QImage.Format.Format_ARGB32_Premultiplied)
        padding.fill(Qt.GlobalColor.transparent)
        with QPainter(padding) as painter:
            painter.drawImage(
                QRect(
                    (tgt_size.width() - svg_size.width()) / 2,
                    (tgt_size.height() - svg_size.height()) / 2,
                    svg_size.width(),
                    svg_size.height(),
                ),
                img,
                QRect(0, 0, svg_size.width(), svg_size.height()),
            )
        return padding
    return img


def resize_image(
    img_path: IMG_PATH_TYPE,
    size: Size,
    aspect: Union[bool, Literal["width", "height"]],
) -> QImage:
    """Resize an image according to specified `size`."""
    if img_path is None:
        return None
    img_path = Path(img_path)
    if img_path.suffix.lower() in (".svg", ""):
        img = render_svg(img_path.with_suffix(".svg"), size)
    else:
        img = QImage(img_path)
    if img.isNull():
        supported_formats = [
            fmt.toStdString() for fmt in QImageReader.supportedImageFormats()
        ]
        raise RuntimeError(
            f"{str(img_path)} is not of a supported format {supported_formats}"
        )
    w, h = cast(Tuple[int, int], img.size().toTuple())
    if aspect and (size.width != w or size.height != h):
        if isinstance(aspect, str):
            if aspect == "width":
                img_copy = img.scaledToWidth(
                    size.width, mode=Qt.TransformationMode.SmoothTransformation
                )
            else:
                assert aspect == "height"
                img_copy = img.scaledToHeight(
                    size.height, mode=Qt.TransformationMode.SmoothTransformation
                )
        else:
            assert aspect is True
            if h > w:
                img_copy = img.scaledToHeight(
                    size.height, mode=Qt.TransformationMode.SmoothTransformation
                )
            else:
                img_copy = img.scaledToWidth(
                    size.width, mode=Qt.TransformationMode.SmoothTransformation
                )
        if w != h:
            _tmp_canvas = QImage(
                size.width, size.height, QImage.Format.Format_ARGB32_Premultiplied
            )
            _tmp_canvas.fill(Qt.GlobalColor.transparent)
            with QPainter(_tmp_canvas) as painter:
                rect = QRect(0, 0, img_copy.width(), img_copy.height())
                if w < h:
                    offset = QRect(
                        (size.width - img_copy.width()) / 2,
                        0,
                        img_copy.width(),
                        img_copy.height(),
                    )
                else:
                    offset = QRect(
                        0,
                        (size.height - img_copy.height()) / 2,
                        img_copy.width(),
                        img_copy.height(),
                    )
                painter.drawImage(offset, img_copy, rect)
            return _tmp_canvas
        return img_copy
    return img.copy(img.rect())


def overlay_color(
    img: QImage, color: Union[QColor, QBrush], mask: bool = False
) -> QImage:
    if mask:
        paint_bucket = QImage(img.size(), QImage.Format.Format_ARGB32_Premultiplied)
        paint_bucket.fill(
            color if isinstance(color, QColor) else Qt.GlobalColor.transparent
        )
        with QPainter(paint_bucket) as painter:
            painter.setPen(Qt.GlobalColor.transparent)
            if isinstance(color, QBrush):
                painter.setBrush(color)
                painter.drawRect(img.rect())
            painter.setCompositionMode(
                QPainter.CompositionMode.CompositionMode_DestinationIn
            )
            painter.drawImage(0, 0, img)
        return paint_bucket
    with QPainter(img) as painter:
        painter.setPen(Qt.GlobalColor.transparent)
        if isinstance(color, QBrush):
            painter.setBrush(color)
            painter.drawRect(img.rect())
        else:
            assert isinstance(color, QColor)
            painter.fillRect(img.rect(), color)
    return img
