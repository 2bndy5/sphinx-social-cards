import math
from logging import getLogger
import re
from pathlib import Path
from typing import Optional, Tuple, List, Union

from jinja2 import TemplateNotFound, FileSystemLoader, Template
from jinja2.sandbox import SandboxedEnvironment
from pydantic import TypeAdapter
from pydantic_extra_types.color import Color
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import (
    QImage,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QBrush,
    QPen,
    QPolygonF,
    QColor,
    QFont,
    QFontDatabase,
    QFontMetricsF,
    QTextOption,
    QTextLayout,
)
import yaml

from .validators import Social_Cards
from .validators.layers import (
    Typography,
    LayerImage,
    GenericShape,
    Rectangle,
    Ellipse,
    Polygon,
    ColorType,
)
from .validators.common import Gradient
from .validators.layout import Layer, Layout, Offset
from .validators.contexts import JinjaContexts
from .fonts import FontSourceManager, QtAppFontInfo
from .colors import ColorAttr, auto_get_fg_color, get_qt_color, get_qt_gradient
from .images import find_image, resize_image, overlay_color

LOGGER = getLogger(__name__)
_DEFAULT_LAYOUT_DIR = Path(__file__).parent / "layouts"
layout_validator: TypeAdapter[Layout] = TypeAdapter(Layout)


def _insert_wbr(text: str, token: str = " ") -> str:
    """Inserts word break tokens at probable points that delimit words. This is useful
    for long API or brand names."""
    # Split after punctuation
    text = re.sub("([.:_-]+)", f"\\1{token}", text)
    # Split before brackets
    text = re.sub(r"([(\[{/])", f"{token}\\1", text)
    # Split between camel-case words
    text = re.sub(r"([a-z])([A-Z])", f"\\1{token}\\2", text)
    return text


class CardGenerator:
    """A factory for generating social card images"""

    doc_src: str = ""

    def __init__(self, context: JinjaContexts, config: Social_Cards):
        self.context = context.model_dump()
        self.context["math"] = math
        self.config = config
        self.jinja_env = SandboxedEnvironment(
            loader=FileSystemLoader(
                [
                    str(
                        fp
                        if Path(fp).is_absolute()
                        else Path(self.doc_src, fp).resolve()
                    )
                    for fp in config.cards_layout_dir
                ]
                + [str(_DEFAULT_LAYOUT_DIR)]
            ),
        )
        self.jinja_env.block_start_string = "#%"
        self.jinja_env.block_end_string = "%#"
        self.jinja_env.variable_start_string = "'{{"
        self.jinja_env.variable_end_string = "}}'"
        self.jinja_env.comment_start_string = "##"
        self.jinja_env.comment_end_string = "##"
        # self.jinja_env.line_statement_prefix = "#%"
        self.jinja_env.line_comment_prefix = "##"
        self.jinja_env.finalize = lambda output: "null" if output is None else output
        self.jinja_env.filters["yaml"] = (
            lambda x: yaml.safe_dump(x, default_flow_style=True)
            .rstrip("\n...\n")
            .rstrip("\n")
        )

    def parse_layout(self, content: Optional[str] = None):
        template: Template
        if content is not None:
            template = self.jinja_env.from_string(content)
            parsed_yaml = template.render(self.context).strip()
            try:
                self.config._parsed_layout = layout_validator.validate_python(
                    yaml.safe_load(parsed_yaml)
                )
            except Exception as exc:
                LOGGER.error("Failed to parse layout:\n%s", parsed_yaml)
                raise exc
        else:
            for ext in (".yml", ".yaml", ".YML", ".YAML"):
                try:
                    template = self.jinja_env.get_template(
                        self.config.cards_layout + ext
                    )
                    break
                except TemplateNotFound:
                    continue  # we'll raise the error when all extensions were tried
            else:
                raise ValueError(f"Could not find layout: '{self.config.cards_layout}'")
            template_result = template.render(self.context)
            try:
                self.config._parsed_layout = layout_validator.validate_python(
                    yaml.safe_load(template_result)
                )
            except Exception as exc:
                LOGGER.error(
                    "failed to parse %s template:\n%s",
                    self.config.cards_layout,
                    template_result,
                )
                raise exc

    def get_color(
        self, spec: Optional[ColorType], offset: Offset
    ) -> Optional[Union[QColor, QBrush]]:
        if spec:
            if isinstance(spec, (Color, str)):
                return get_qt_color(spec)
            if isinstance(spec, Gradient):
                return QBrush(get_qt_gradient(spec, offset))
        return None

    def load_font(self, typography: Typography) -> QtAppFontInfo:
        typo_font = typography.font or self.config.cards_layout_options.font
        assert typo_font is not None and typo_font.path is not None
        app_font_id = QFontDatabase.addApplicationFont(typo_font.path)
        family = QFontDatabase.applicationFontFamilies(app_font_id)[0]
        style = QFontDatabase.styles(family)[0]
        return QtAppFontInfo(id=app_font_id, family=family, style=style)

    @staticmethod
    def calc_font_size(
        line_amt: int,
        line_height: Union[float, int],
        max_height: Union[float, int],
        font_db_info: QtAppFontInfo,
    ) -> QFont:
        theoretical_height = max_height / line_amt
        space = theoretical_height - (theoretical_height * line_height)
        space = space * max(1, line_amt - 1) / line_amt
        actual_height = theoretical_height - space
        actual_height -= actual_height % 2
        typo_font = QFontDatabase.font(
            font_db_info.family, font_db_info.style, int(max(1, actual_height))
        )
        metrics = QFontMetricsF(typo_font)
        while metrics.height() > theoretical_height - space and actual_height > 2:
            actual_height -= 2
            typo_font = QFontDatabase.font(
                font_db_info.family, font_db_info.style, int(actual_height)
            )
            metrics = QFontMetricsF(typo_font)
        while metrics.height() < theoretical_height - space - 1:
            actual_height += 2
            typo_font = QFontDatabase.font(
                font_db_info.family, font_db_info.style, int(actual_height)
            )
            metrics = QFontMetricsF(typo_font)

        return typo_font

    def make_text_block(
        self,
        typography: Typography,
        layer: Layer,
        canvas: QPainter,
        font_db_info: QtAppFontInfo,
    ) -> Tuple[List[str], QTextLayout, QTextOption]:
        assert layer.size is not None
        font = self.calc_font_size(
            typography.line.amount,
            typography.line.height,
            layer.size.height - typography.border.width,
            font_db_info,
        )
        canvas.setFont(font)
        metrics = QFontMetricsF(canvas.font())

        align = [a.lower() for a in typography.align.split()[:2]]
        anchor_translator = (
            {  # Horizontal flags
                "start": Qt.AlignmentFlag.AlignLeft,
                "center": Qt.AlignmentFlag.AlignHCenter,
                "end": Qt.AlignmentFlag.AlignRight,
            },
            {  # vertical flags
                "top": Qt.AlignmentFlag.AlignTop,
                "center": Qt.AlignmentFlag.AlignVCenter,
                "bottom": Qt.AlignmentFlag.AlignBottom,
            },
        )

        assert len(align) == 2
        font_flags = QTextOption(
            anchor_translator[0][align[0]] | anchor_translator[1][align[1]]
        )
        font_flags.setWrapMode(QTextOption.WrapMode.NoWrap)
        font_flags.setFlags(QTextOption.Flag.ShowLineAndParagraphSeparators)

        display_lines: List[str] = [""]
        line_count = 0
        max_width = layer.size.width - typography.border.width
        for word in re.split(r"([\0\s\n])", _insert_wbr(typography.content, "\0")):
            if word == "\0" or (word == " " and not display_lines[line_count]):
                continue
            elif word == "\n":
                if line_count < typography.line.amount - 1:
                    display_lines.append("")
                    line_count += 1
                    continue
                elif line_count == typography.line.amount - 1 and typography.overflow:
                    typography.line.amount += 1
                    display_lines.clear()
                    return self.make_text_block(typography, layer, canvas, font_db_info)
                else:
                    word = " "  # just discard the token if we can't add another line
            test_str = display_lines[line_count] + word
            rect = metrics.boundingRect(test_str, font_flags)
            if rect.width() - rect.x() < max_width:  # text fits!
                display_lines[line_count] += word
            # text does not fit!
            elif line_count + 1 < typography.line.amount:
                # line capacity filled and more lines available
                display_lines.append(word)
                display_lines[line_count] = display_lines[line_count].strip()
                line_count += 1
            elif typography.overflow:  # no lines left but overflow is allowed
                # shrink font by adding 1 to the max lines and try again
                typography.line.amount += 1
                display_lines.clear()
                return self.make_text_block(typography, layer, canvas, font_db_info)
            else:  # text has overflow but typography.overflow is disabled
                if display_lines[line_count]:
                    truncated = metrics.elidedText(
                        display_lines[line_count] + word,
                        Qt.TextElideMode.ElideRight,
                        layer.size.width,
                    )
                    display_lines[line_count] = truncated
                else:  # append ellipses to the empty line
                    display_lines[line_count] = "…"
                break

        text_layout = QTextLayout(
            "\n".join(display_lines), canvas.font(), canvas.device()
        )
        text_layout.setFlags(font_flags.flags().value)
        return display_lines, text_layout, font_flags

    def render_text(self, layer: Layer, typography: Typography, canvas: QPainter):
        """Renders text into the social card"""
        font_db_info = self.load_font(typography)
        raw_text, text_layout, font_flags = self.make_text_block(
            typography, layer, canvas, font_db_info
        )

        if typography.color:
            color = self.get_color(typography.color, layer.offset)
        else:
            color = self.get_color(self.config.cards_layout_options.color, layer.offset)
        assert color is not None
        if not typography.border.color:
            stroke_color = color
        else:
            stroke_color = self.get_color(typography.border.color, layer.offset)
            assert stroke_color is not None

        metrics = QFontMetricsF(canvas.font())
        assert layer.size is not None
        padding = layer.size.height - (metrics.height() * typography.line.amount)
        padding /= typography.line.amount
        padding *= len(raw_text)
        padding /= max(1, typography.line.amount - 1)

        y_offset = 0
        layer_rect = QRectF(0, 0, layer.size.width, layer.size.height)
        bbox = metrics.boundingRect(
            layer_rect, font_flags.alignment().value, "\n".join(raw_text)
        )
        canvas.setBrush(Qt.GlobalColor.transparent)
        text_layout.beginLayout()
        for text in raw_text:
            if not text:
                y_offset += metrics.height() + min(0, padding)
                continue
            line = text_layout.createLine()
            line.setNumColumns(len(text))
            line_bbox = metrics.boundingRect(bbox, font_flags.alignment().value, text)
            pos = QPointF(
                line_bbox.x() + typography.border.width / 2, y_offset + max(0, bbox.y())
            )
            line.setPosition(pos)
            # canvas.drawRect(pos.x(), pos.y(), line_bbox.width(), line_bbox.height())
            y_offset += metrics.height() + min(0, padding)
            # draw text fill
            canvas.setPen(QPen(color))
            line.draw(canvas, QPointF(0, 0))
            if typography.border.width and stroke_color is not None:  # draw border
                pos.setY(pos.y() + metrics.ascent())
                painter_path = QPainterPath()
                painter_path.setFillRule(Qt.FillRule.WindingFill)
                painter_path.addText(pos, canvas.font(), text)
                path_stroke = QPainterPathStroker()
                path_stroke.setCurveThreshold(0.35)
                path_stroke.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                stroke = path_stroke.createStroke(painter_path)
                polygons = stroke.toSubpathPolygons()
                canvas.setPen(QPen(stroke_color, typography.border.width))
                for poly in polygons:
                    canvas.drawPolygon(poly)
        text_layout.endLayout()
        # text_layout.draw(canvas, QPointF(0, 0))
        QFontDatabase.removeApplicationFont(font_db_info.id)

    def get_image(self, layer: Layer, img_config: LayerImage):
        """Renders an image into the social card"""
        color = self.get_color(img_config.color, layer.offset)
        img_path = find_image(
            img_config.image,
            self.config.image_paths,
            self.doc_src,
            self.config.cache_dir,
        )
        if img_path is None and img_config.image:
            raise FileNotFoundError(f"Image not found: '{img_config.image}'")
        return img_path, color

    def render_icon(self, layer: Layer, img_config: LayerImage, canvas: QPainter):
        """Renders an ``icon`` layer."""
        img_path, color = self.get_image(layer, img_config)
        if img_path is not None:
            assert layer.size is not None
            img = resize_image(img_path, layer.size, img_config.preserve_aspect)
            if color:
                img = overlay_color(img, color, mask=True)
            canvas.drawImage(0, 0, img)

    def render_background(self, layer: Layer, img_config: LayerImage, canvas: QPainter):
        """Renders an ``background`` layer."""
        img_path, color = self.get_image(layer, img_config)
        img = None
        assert layer.size is not None
        if img_path is not None:
            img = resize_image(img_path, layer.size, img_config.preserve_aspect)
        if color is not None:
            if not img:
                img = QImage(
                    layer.size.width,
                    layer.size.height,
                    QImage.Format.Format_ARGB32_Premultiplied,
                )
                img.fill(Qt.GlobalColor.transparent)
            img = overlay_color(img, color, mask=False)
        if img is not None:
            canvas.drawImage(0, 0, img)

    def get_shape_args(
        self, layer: Layer, shape_config: GenericShape
    ) -> Tuple[QBrush, QPen, QRectF]:
        assert layer.size is not None
        rect = QRectF(0, 0, layer.size.width, layer.size.height)

        if shape_config.border.width:
            # border is drawn outside of the shape's bounding rectangle
            width = shape_config.border.width
            rect = QRectF(
                width / 2,
                width / 2,
                layer.size.width - width,
                layer.size.height - width,
            )
            border_color = self.get_color(shape_config.border.color, layer.offset)
            if border_color is None:
                border_color = Qt.GlobalColor.transparent
            pen = QPen(QBrush(border_color), shape_config.border.width)
        else:
            pen = QPen(QColor(Qt.GlobalColor.transparent))

        color = self.get_color(shape_config.color, layer.offset)
        if color is not None:
            brush = QBrush(color)
        else:
            brush = QBrush(QColor(Qt.GlobalColor.transparent))

        return (brush, pen, rect)

    def render_ellipse(self, layer: Layer, shape_config: Ellipse, canvas: QPainter):
        brush, pen, rect = self.get_shape_args(layer, shape_config)
        canvas.setBrush(brush)
        canvas.setPen(pen)
        if shape_config.arc is not None:  # drawing only an arc
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            start = shape_config.arc.start * 16
            if shape_config.arc.start > shape_config.arc.end:
                start = (shape_config.arc.start - 360) * 16
            end = shape_config.arc.end * 16 - start
            if shape_config.border_to_origin:
                pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                canvas.setPen(pen)
                canvas.drawPie(rect, start, end)
            else:
                assert layer.size is not None
                # drawing arc w/o border to origin should be clipped so arc endpoints coincide w/
                # pieslice boundary
                _tmp_canvas = QImage(
                    layer.size.width,
                    layer.size.height,
                    QImage.Format.Format_ARGB32_Premultiplied,
                )
                _tmp_canvas.fill(Qt.GlobalColor.transparent)
                _mask_canvas = _tmp_canvas.copy()
                with QPainter(_mask_canvas) as painter:
                    pen_mask = QPen(pen)
                    pen_mask.setWidth(1)
                    painter.setPen(pen_mask)
                    painter.setBrush(Qt.GlobalColor.white)
                    painter.drawPie(_tmp_canvas.rect(), start, end)
                with QPainter(_tmp_canvas) as painter:
                    painter.setPen(pen)
                    painter.setBrush(brush)
                    painter.drawEllipse(rect)
                    painter.setCompositionMode(
                        QPainter.CompositionMode.CompositionMode_DestinationIn
                    )
                    painter.drawImage(0, 0, _mask_canvas)
                canvas.drawImage(0, 0, _tmp_canvas)
        else:  # drawing a full ellipse
            canvas.drawEllipse(rect)

    def render_polygon(self, layer: Layer, shape_config: Polygon, canvas: QPainter):
        brush, pen, rect = self.get_shape_args(layer, shape_config)
        assert layer.size is not None
        if shape_config.border.width:
            width = shape_config.border.width
            rect = QRectF(
                width, width, layer.size.width - width, layer.size.height - width
            )
            pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        canvas.setPen(pen)
        canvas.setBrush(brush)
        poly = QPolygonF()

        if isinstance(shape_config.sides, list):

            def clamp_offset_to_rect(minimum: float, maximum: float, desired: int):
                if minimum > desired:
                    return minimum
                if desired > maximum:
                    return maximum
                return float(desired)

            for offset in shape_config.sides:
                poly.append(
                    QPointF(
                        clamp_offset_to_rect(rect.x(), rect.width(), offset.x),
                        clamp_offset_to_rect(rect.y(), rect.height(), offset.y),
                    )
                )
        else:
            assert isinstance(shape_config.sides, int)
            center = QPointF(layer.size.width / 2, layer.size.height / 2)
            radius = (min(rect.width() - rect.x(), rect.height() - rect.y()) / 2) - 0.5

            angles = []
            degrees = 360 / shape_config.sides
            # Start with the bottom left polygon vertex
            current_angle = (270 - 0.5 * degrees) + shape_config.rotation
            for _ in range(shape_config.sides):
                angles.append(current_angle)
                current_angle += degrees
                if current_angle > 360:
                    current_angle -= 360

            for angle in angles:
                point = QPointF(radius, 0.0)
                poly.append(
                    QPointF(
                        point.x() * math.cos(math.radians(360 - angle))
                        - point.y() * math.sin(math.radians(360 - angle))
                        + center.x(),
                        point.y() * math.cos(math.radians(360 - angle))
                        + point.x() * math.sin(math.radians(360 - angle))
                        + center.y(),
                    )
                )

        canvas.drawPolygon(poly)

    def render_rectangle(self, layer: Layer, shape_config: Rectangle, canvas: QPainter):
        brush, pen, rect = self.get_shape_args(layer, shape_config)
        canvas.setBrush(brush)
        canvas.setPen(pen)
        if not shape_config.radius:
            canvas.drawRect(rect)
            return

        corners = [False] * 4
        corner_map = {
            "top left": 0,
            "top right": 1,
            "bottom left": 2,
            "bottom right": 3,
        }
        for corner in shape_config.corners:
            corners[corner_map[corner]] = True

        if all(corners):
            canvas.drawRoundedRect(rect, shape_config.radius, shape_config.radius)
            return
        assert layer.size is not None
        _pointed_rect = QImage(
            layer.size.width,
            layer.size.height,
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        _pointed_rect.fill(Qt.GlobalColor.transparent)
        _rounded_rect = _pointed_rect.copy()
        _combined_rect = _pointed_rect.copy()
        with QPainter(_pointed_rect) as painter:
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRect(rect)
        with QPainter(_rounded_rect) as painter:
            painter.setPen(pen)
            painter.setBrush(brush)
            painter.drawRoundedRect(rect, shape_config.radius, shape_config.radius)
        with QPainter(_combined_rect) as painter:
            assert layer.size is not None
            w, h = layer.size.width / 2, layer.size.height / 2
            for i, is_rounded in enumerate(corners):
                clipping_rect = QRectF(w * (i % 2), h * int(i / 2), w, h)
                painter.drawImage(
                    clipping_rect,
                    _rounded_rect if is_rounded else _pointed_rect,
                    clipping_rect,
                )
        canvas.drawImage(0, 0, _combined_rect)

    def render_debugging(
        self,
        layer: Layer,
        index: int,
        canvas: QPainter,
        color: ColorAttr,
    ):
        assert layer.size is not None
        rect = QRectF(
            layer.offset.x,
            layer.offset.y,
            layer.size.width
            - 1 * (layer.size.width == self.config._parsed_layout.size.width),
            layer.size.height
            - 1 * (layer.size.height == self.config._parsed_layout.size.height),
        )
        font_db_info = self.load_font(Typography(content=""))
        canvas.setFont(QFontDatabase.font(font_db_info.family, font_db_info.style, 10))
        canvas.setBrush(Qt.GlobalColor.transparent)
        canvas.setPen(QPen(color.fill, 1))
        canvas.drawRect(rect)
        canvas.setPen(color.text)
        canvas.setBrush(color.fill)

        def draw_label(label: str, alignment: Qt.AlignmentFlag):
            flags = QTextOption(alignment)
            flags.setWrapMode(QTextOption.WrapMode.NoWrap)
            label_dimensions = canvas.boundingRect(rect, label, flags)
            canvas.drawRect(label_dimensions)
            flags.setAlignment(Qt.AlignmentFlag.AlignCenter)
            canvas.drawText(label_dimensions, label, flags)

        draw_label(
            f" {index} - {layer.offset.x},{layer.offset.y} ",
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft,
        )
        draw_label(
            f" {index} - {layer.size.width},{layer.size.height} ",
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight,
        )
        QFontDatabase.removeApplicationFont(font_db_info.id)

    def render_layer(self, layer: Layer) -> QImage:
        if layer.size is None:
            layer.size = self.config._parsed_layout.size
        _tmp_canvas = QImage(
            layer.size.width,
            layer.size.height,
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        _tmp_canvas.fill(Qt.GlobalColor.transparent)
        with QPainter(_tmp_canvas) as _painter:
            if layer.background is not None:
                self.render_background(layer, layer.background, _painter)
            if layer.rectangle is not None:
                self.render_rectangle(layer, layer.rectangle, _painter)
            if layer.ellipse is not None:
                self.render_ellipse(layer, layer.ellipse, _painter)
            if layer.polygon is not None:
                self.render_polygon(layer, layer.polygon, _painter)
            if layer.icon is not None:
                self.render_icon(layer, layer.icon, _painter)
            if layer.typography is not None:
                self.render_text(layer, layer.typography, _painter)
            if layer.mask is not None:
                mask = self.render_layer(layer.mask)
                _masked = QImage(
                    _tmp_canvas.size(),
                    QImage.Format.Format_ARGB32_Premultiplied,
                )
                _masked.fill(Qt.GlobalColor.transparent)
                with QPainter(_masked) as mask_painter:
                    src_rect = _masked.rect()
                    tgt_rect = QRectF(
                        layer.mask.offset.x,
                        layer.mask.offset.y,
                        src_rect.width(),
                        src_rect.height(),
                    )
                    mask_painter.drawImage(tgt_rect, mask, src_rect)
                if layer.mask.invert:
                    _painter.setCompositionMode(
                        QPainter.CompositionMode.CompositionMode_DestinationOut
                    )
                else:
                    _painter.setCompositionMode(
                        QPainter.CompositionMode.CompositionMode_DestinationIn
                    )
                _painter.drawImage(0, 0, _masked)
        return _tmp_canvas

    def render_card(self) -> QImage:
        FontSourceManager.cache_path = Path(self.config.cache_dir, "fonts")
        for font in self.config.get_fonts():
            FontSourceManager.get_font(font)
        _canvas = QImage(
            self.config._parsed_layout.size.width,
            self.config._parsed_layout.size.height,
            QImage.Format.Format_ARGB32_Premultiplied,
        )
        _canvas.fill(Qt.GlobalColor.transparent)
        with QPainter(_canvas) as _painter:
            for layer in self.config._parsed_layout.layers:
                _tmp_canvas = self.render_layer(layer)
                _painter.drawImage(layer.offset.x, layer.offset.y, _tmp_canvas)
            assert not isinstance(self.config.debug, bool)
            if self.config.debug.enable:
                color = self.config.debug.color
                color_attr = ColorAttr(
                    fill=self.get_color(color, Offset(x=0, y=0)),
                    text=self.get_color(auto_get_fg_color(color), Offset(x=0, y=0)),
                )
                _painter.setBrush(color_attr.fill)
                _painter.setPen(QPen(color_attr.fill))
                if self.config.debug.grid:
                    steps = self.config.debug.grid_step
                    points = []
                    for y in range(
                        steps, self.config._parsed_layout.size.height, steps
                    ):
                        for x in range(
                            steps, self.config._parsed_layout.size.width, steps
                        ):
                            points.append(QPointF(x - 1, y))
                            points.append(QPointF(x + 1, y))
                            points.append(QPointF(x, y - 1))
                            points.append(QPointF(x, y + 1))
                    _painter.drawLines(points)
                for i, layer in enumerate(self.config._parsed_layout.layers):
                    self.render_debugging(layer, i, _painter, color_attr)
        return _canvas
