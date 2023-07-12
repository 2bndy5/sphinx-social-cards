import re
from pathlib import Path
from typing import Optional, Tuple, List, Union, Dict, Any, cast
from jinja2 import TemplateNotFound, FileSystemLoader, Template
from jinja2.sandbox import SandboxedEnvironment
import yaml
from yaml.composer import ComposerError

from PIL import (
    Image,
    ImageFont,
    ImageDraw,
    ImageColor,
    ImageChops,
    _version as pil_version,
)
import pydantic
from sphinx.util.logging import getLogger
from .validators import Social_Cards, _validate_color
from .validators.layers import (
    Typography,
    LayerImage,
    GenericShape,
    Rectangle,
    Ellipse,
    Polygon,
)
from .validators.layout import Layer, Layout
from .validators.contexts import JinjaContexts
from .fonts import FontSourceManager
from .colors import ColorAttr, MD_COLORS, auto_get_fg_color
from .images import find_image, resize_image, overlay_color

LOGGER = getLogger(__name__)
_DEFAULT_LAYOUT_DIR = Path(__file__).parent / "layouts"
PIL_VER = tuple([int(x) for x in pil_version.__version__.split(".")[:3]])


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
    imagemagick_version: Tuple[int, int, int] = (0, 0, 0)

    def __init__(self, context: JinjaContexts, config: Social_Cards):
        self.context = context
        self.config = config
        self._canvas: Image.Image = Image.new(mode="RGBA", size=(10, 10))
        self._jinja_env = SandboxedEnvironment(
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

    def parse_layout(self, content: Optional[str] = None):
        template: Template
        if content is not None:
            template = self._jinja_env.from_string(content)
            self.config._parsed_layout = pydantic.TypeAdapter(Layout).validate_python(
                yaml.safe_load(template.render(self.context).strip())
            )
        else:
            for ext in (".yml", ".yaml", ".YML", ".YAML"):
                try:
                    template = self._jinja_env.get_template(
                        self.config.cards_layout + ext
                    )
                    break
                except TemplateNotFound:
                    continue  # we'll raise the error when all extensions were tried
            else:
                raise ValueError(f"Could not find layout: '{self.config.cards_layout}'")
            template_result = template.render(self.context)
            try:
                self.config._parsed_layout = pydantic.TypeAdapter(
                    Layout
                ).validate_python(yaml.safe_load(template_result))
            except ComposerError as exc:
                LOGGER.error("failed to parse template:\n%s", template_result)
                raise exc

    def get_color(self, spec: Optional[str]) -> Optional[str]:
        color, is_pil_color = _validate_color(spec)
        if not is_pil_color and color:
            raise ValueError(f"Invalid color specified: '{color}'")
        if color in MD_COLORS:
            return MD_COLORS[color].fill
        if not color:
            return None
        return color

    def load_font(self, typography: Typography, font_size) -> ImageFont.FreeTypeFont:
        typo_font = typography.font or self.config.cards_layout_options.font
        assert typo_font is not None and typo_font.path is not None
        return ImageFont.truetype(typo_font.path, font_size)

    @staticmethod
    def calc_font_size(
        line_amt: int,
        line_height: Union[float, int],
        max_height: int,
        font: Union[str, Path],
    ) -> Tuple[Union[float, int], int]:
        theoretical_height = max_height / line_amt
        space = theoretical_height - (theoretical_height * line_height)
        space = space * max(1, line_amt - 1) / line_amt
        actual_height = theoretical_height - space
        typo_font = ImageFont.truetype(font=str(font), size=int(max(1, actual_height)))
        metrics = typo_font.getmetrics()
        while sum(metrics) > theoretical_height - space and actual_height > 2:
            actual_height -= 2
            typo_font = ImageFont.truetype(font=str(font), size=int(actual_height))
            metrics = typo_font.getmetrics()
        while sum(metrics) < theoretical_height - space - 1:
            actual_height += 1
            typo_font = ImageFont.truetype(font=str(font), size=int(actual_height))
            metrics = typo_font.getmetrics()

        space = (max_height - (sum(metrics) * line_amt)) / max(1, line_amt - 1)
        size = int(actual_height)
        del typo_font
        return space, size

    def make_text_block(
        self, typography: Typography, layer: Layer, canvas: Image.Image
    ) -> Tuple[List[List[str]], int, Union[int, float]]:
        assert layer.size is not None
        typo_font = typography.font or self.config.cards_layout_options.font
        assert typo_font is not None and typo_font.path is not None
        spacing, font_size = self.calc_font_size(
            typography.line.amount,
            typography.line.height,
            layer.size.height,
            typo_font.path,
        )
        font = self.load_font(typography, font_size)

        display_text: List[List[str]] = [[]]
        brush = ImageDraw.Draw(canvas)
        line_count = 0
        offset = (0, 0)
        for word in re.split(r"([\0\s\n])", _insert_wbr(typography.content, "\0")):
            if word == "\0":
                continue
            elif word == "\n":
                if line_count < typography.line.amount - 1:
                    display_text.append([])
                    line_count += 1
                    continue
                elif line_count == typography.line.amount - 1 and typography.overflow:
                    typography.line.amount += 1
                    return self.make_text_block(typography, layer, canvas)
                else:
                    word = " "  # just discard the token if we can't add another line
            test_str = "".join(display_text[line_count] + [word])
            x, y, w, h = brush.textbbox(offset, test_str, font=font, spacing=spacing)
            if w - x < layer.size.width:  # text fits!
                display_text[line_count].append(word)
            # text does not fit!
            elif line_count + 1 < typography.line.amount:
                # line capacity filled and more lines available
                display_text.append([word])
                line_count += 1
            elif typography.overflow:  # no lines left but overflow is allowed
                # shrink font by adding 1 to the max lines and try again
                typography.line.amount += 1
                return self.make_text_block(typography, layer, canvas)
            else:  # text has overflow but typography.overflow is disabled
                if display_text[line_count]:
                    # backtrack 1 char at a time till we can fit the '...'
                    this_line = "".join(display_text[line_count]).rstrip()
                    x, y, w, h = brush.textbbox(
                        offset, this_line + "...", font=font, spacing=spacing
                    )
                    while w - x > layer.size.width and this_line:
                        x, y, w, h = brush.textbbox(
                            offset,
                            this_line[:-1].rstrip() + "...",
                            font=font,
                            spacing=spacing,
                        )
                        this_line = this_line[:-1].rstrip()
                    display_text[line_count] = re.split(r"(\s)", this_line + "...")
                else:  # append ellipses to the empty line
                    display_text[line_count].append("...")
                break
        return display_text, font_size, spacing

    def render_text(self, layer: Layer, typography: Typography, canvas: Image.Image):
        """Renders text into the social card"""
        assert layer.size is not None
        text_block, font_size, spacing = self.make_text_block(typography, layer, canvas)
        font = self.load_font(typography, font_size)
        full_text = "\n".join(["".join(r).rstrip() for r in text_block]).rstrip()
        brush = ImageDraw.Draw(canvas)
        x, y, w, h = brush.textbbox(
            (0, 0),
            full_text,
            font,
            spacing=spacing,
            stroke_width=typography.border.width,
        )

        color = self.config.cards_layout_options.color
        if typography.color:
            color = self.get_color(typography.color)
        if not typography.border.color:
            stroke_color = color
        else:
            stroke_color = self.get_color(typography.border.color)

        align = [a.lower() for a in typography.align.split()[:2]]
        anchor_translator = dict(start="l", center="m", end="r", top="a", bottom="d")

        def get_anchor_offset(anchor: str, length: int):
            anchor = anchor.lower()
            if anchor in ("end", "bottom"):
                return length
            if anchor == "center":
                return int(length / 2)
            return 0  # if anchor in ("start", "top")

        padding = (
            (layer.size.height - (h - y) - (y if align[1] != "top" else 0))
            / typography.line.amount
            * len(text_block)
            / max(1, typography.line.amount - 1)
        )
        brush.text(
            (
                get_anchor_offset(align[0], layer.size.width),
                get_anchor_offset(align[1], layer.size.height)
                - (y if align[1] == "top" else 0),
            ),
            full_text,
            font=font,
            fill=color,
            spacing=spacing + padding,
            anchor="".join([anchor_translator[a] for a in align]),
            stroke_width=typography.border.width,
            stroke_fill=stroke_color,
        )
        return canvas

    def get_image(self, layer: Layer, img_config: LayerImage):
        """Renders an image into the social card"""
        img_path: Optional[Path] = None
        color: Optional[str] = None
        if img_config.image is not None:
            img_path = find_image(
                img_config.image.strip(),
                self.config.image_paths,
                self.doc_src,
                self.config.cache_dir,
            )
            if img_path is None and img_config.image:
                raise FileNotFoundError(f"Image not found: '{img_config.image}'")
        if img_config.color:
            color = self.get_color(img_config.color)
        return img_path, color

    def render_icon(self, layer: Layer, img_config: LayerImage, canvas: Image.Image):
        """Renders an ``icon`` layer."""
        img_path, color = self.get_image(layer, img_config)
        if img_path is not None:
            assert layer.size is not None
            img = resize_image(
                img_path,
                self.config.cache_dir,
                layer.size,
                img_config.preserve_aspect,
                self.imagemagick_version,
            )
            if color is not None:
                img = overlay_color(img, color, mask=True)
            canvas.alpha_composite(img)

    def render_background(
        self, layer: Layer, img_config: LayerImage, canvas: Image.Image
    ):
        """Renders an ``background`` layer."""
        img_path, color = self.get_image(layer, img_config)
        img = None
        assert layer.size is not None
        if img_path is not None:
            img = resize_image(
                img_path,
                self.config.cache_dir,
                layer.size,
                img_config.preserve_aspect,
                self.imagemagick_version,
            )
        if color is not None:
            if not img:
                img = Image.new(mode="RGBA", size=(layer.size.width, layer.size.height))
            img = overlay_color(img, color, mask=False)
        if img is not None:
            canvas.alpha_composite(img)

    def get_shape_args(
        self, layer: Layer, shape_config: GenericShape
    ) -> Dict[str, Any]:
        assert layer.size is not None
        size = (layer.size.width - 1, layer.size.height - 1)
        border_color: Optional[str] = self.get_color(shape_config.border.color)
        color: Optional[str] = self.get_color(shape_config.color)
        return {
            "xy": [(0, 0), size],
            "fill": color,
            "outline": border_color,
            "width": shape_config.border.width,
        }

    def render_ellipse(self, layer: Layer, shape_config: Ellipse, canvas: Image.Image):
        args = self.get_shape_args(layer, shape_config)
        brush = ImageDraw.Draw(canvas)
        if shape_config.arc is not None:  # drawing only an arc
            args["start"] = shape_config.arc.start
            args["end"] = shape_config.arc.end
            if shape_config.border_to_origin:
                brush.pieslice(**args)
            else:
                assert "outline" in args
                outline_color = args.pop("outline")
                # the angle of the endpoints for the arc needs clipping
                # so lets create a temp canvas as a mask the default behavior and
                # paste the result into the the current canvas
                tmp = Image.new("RGBA", size=canvas.size)
                mask = tmp.copy()
                brush = ImageDraw.Draw(tmp)
                brush_mask = ImageDraw.Draw(mask)
                brush.pieslice(**args)
                args["fill"] = "white"
                brush_mask.pieslice(**args)
                args["fill"] = outline_color
                brush.arc(**args)
                canvas.paste(tmp, mask=mask)
        else:  # drawing a full ellipse
            brush.ellipse(**args)

    def render_polygon(self, layer: Layer, shape_config: Polygon, canvas: Image.Image):
        args = self.get_shape_args(layer, shape_config)
        args.pop("xy", None)  # we don't use the same size/offset for this
        brush = ImageDraw.Draw(canvas)
        if isinstance(shape_config.sides, list):
            xy: List[Tuple[int, int]] = [
                (offset.x, offset.y) for offset in shape_config.sides
            ]
            brush.polygon(xy=xy, **args)
        else:
            assert isinstance(shape_config.sides, int)
            assert layer.size is not None
            center = (layer.size.width / 2, layer.size.height / 2)
            radius = (min(layer.size.width, layer.size.height) / 2) - 0.5
            brush.regular_polygon(
                bounding_circle=(center, radius),
                n_sides=shape_config.sides,
                rotation=shape_config.rotation,
                **args,
            )

    def render_rectangle(
        self, layer: Layer, shape_config: Rectangle, canvas: Image.Image
    ):
        args = self.get_shape_args(layer, shape_config)
        brush = ImageDraw.Draw(canvas)
        corners = [False] * 4
        corner_map = {
            "top left": 0,
            "top right": 1,
            "bottom right": 2,
            "bottom left": 3,
        }
        for corner in shape_config.corners:
            corners[corner_map[corner]] = True
        xy = cast(List[Tuple[int, int]], args.get("xy"))
        set_radius = shape_config.radius or 1
        max_radius = min(xy[1][0], xy[1][1]) // 2
        args["radius"] = min(  # type: ignore[type-var]
            *[int(r - (r % 2)) for r in (max_radius, set_radius)]
        )
        brush.rounded_rectangle(**args, corners=tuple(corners))

    def render_debugging(self, layer: Layer, index: int, color: ColorAttr):
        offset = (layer.offset.x, layer.offset.y)
        assert layer.size is not None
        area = [layer.size.width + offset[0], layer.size.height + offset[1]]
        if area[0] >= self.config._parsed_layout.size.width:
            area[0] = self.config._parsed_layout.size.width - 1
        if area[1] >= self.config._parsed_layout.size.height:
            area[1] = self.config._parsed_layout.size.height - 1
        size = tuple(area)
        font = ImageFont.truetype(
            str(Path(__file__).parent / ".fonts" / "Roboto normal (latin 400).ttf"), 10
        )
        brush = ImageDraw.Draw(self._canvas)
        brush.rectangle((offset, size), outline=ImageColor.getrgb(color.fill))

        def draw_label(
            label: str,
            _offset: Tuple[int, int],
            _size: Optional[Tuple[int, int]] = None,
        ):
            anchor = "rd" if _size is not None else "la"
            label_dimensions = brush.textbbox(
                _size or _offset, label, font=font, anchor=anchor
            )
            label_backdrop = tuple(
                [
                    x + (2 * ((i % 2) * (-1 if i == 1 else 1)))
                    for i, x in enumerate(label_dimensions)
                ]
            )
            brush.rectangle(label_backdrop, fill=ImageColor.getrgb(color.fill))
            brush.text(
                _size or _offset,
                label,
                fill=ImageColor.getrgb(color.text),
                font=font,
                anchor=anchor,
            )

        draw_label(f" {index} - {layer.offset.x},{layer.offset.y} ", offset)
        draw_label(
            f" {index} - {layer.size.width},{layer.size.height} ",
            offset,
            cast(Tuple[int, int], size),
        )

    def render_layer(self, layer: Layer):
        if layer.size is None:
            layer.size = self.config._parsed_layout.size
        _tmp_canvas = Image.new(mode="RGBA", size=(layer.size.width, layer.size.height))
        if layer.background is not None:
            self.render_background(layer, layer.background, _tmp_canvas)
        if layer.ellipse is not None:
            self.render_ellipse(layer, layer.ellipse, _tmp_canvas)
        if layer.polygon is not None:
            self.render_polygon(layer, layer.polygon, _tmp_canvas)
        if layer.rectangle is not None:
            self.render_rectangle(layer, layer.rectangle, _tmp_canvas)
        if layer.icon is not None:
            self.render_icon(layer, layer.icon, _tmp_canvas)
        if layer.typography is not None:
            _tmp_canvas = self.render_text(layer, layer.typography, _tmp_canvas)
        return _tmp_canvas

    def render_card(self) -> Image.Image:
        FontSourceManager.cache_path = Path(self.config.cache_dir, "fonts")
        for font in self.config.get_fonts():
            FontSourceManager.get_font(font)
        card_size = (
            self.config._parsed_layout.size.width,
            self.config._parsed_layout.size.height,
        )
        self._canvas: Image.Image = Image.new(  # type: ignore[no-redef]
            mode="RGBA", size=card_size
        )
        for layer in self.config._parsed_layout.layers:
            _tmp_canvas = self.render_layer(layer)
            masked = None
            if layer.mask is not None:
                mask = self.render_layer(layer.mask)
                if (
                    mask.size[0] > _tmp_canvas.size[0]
                    or mask.size[1] > _tmp_canvas.size[1]
                ):
                    mask = mask.crop((0, 0) + _tmp_canvas.size)
                else:
                    padding = Image.new(mode="RGBA", size=_tmp_canvas.size)
                    padding.paste(mask, (layer.mask.offset.x, layer.mask.offset.y))
                    mask = padding
                if layer.mask.invert:
                    mask.putalpha(ImageChops.invert(mask.getchannel("A")))
                masked = Image.new(mode="RGBA", size=_tmp_canvas.size)
                masked.paste(_tmp_canvas, mask=mask)
            self._canvas.alpha_composite(
                masked or _tmp_canvas, (layer.offset.x, layer.offset.y)
            )
        assert not isinstance(self.config.debug, bool)
        if self.config.debug.enable:
            if self.config.debug.color in MD_COLORS:
                color = MD_COLORS[self.config.debug.color]
            else:
                color = ColorAttr(
                    fill=self.config.debug.color,
                    text=auto_get_fg_color(self.config.debug.color),
                )
            if self.config.debug.grid:
                brush = ImageDraw.Draw(self._canvas)
                steps = self.config.debug.grid_step
                for y in range(steps, self.config._parsed_layout.size.height, steps):
                    for x in range(steps, self.config._parsed_layout.size.width, steps):
                        brush.ellipse(
                            [x - 1, y - 1, x + 1, y + 1],
                            fill=ImageColor.getrgb(color.fill),
                        )
            for i, layer in enumerate(self.config._parsed_layout.layers):
                self.render_debugging(layer, i, color)
        return self._canvas
