"""This module contains validating dataclasses for a layout's layers."""
from typing import Optional, Union, List

from typing_extensions import Literal
from pydantic import field_validator, Field
from typing_extensions import Annotated

from .base_model import CustomBaseModel

PositiveInt = Annotated[int, Field(gt=0)]
PositiveFloat = Annotated[float, Field(gt=0)]


class Border(CustomBaseModel):
    #: The border's width in pixels. Defaults to :yaml:`0`.
    width: Annotated[int, Field(ge=0)] = 0
    #: The border's color.
    color: Optional[str] = None


class Ellipse(CustomBaseModel):
    """The ellipse layer attribute renders an ellipse using the layer's size and offset
    to define the outlining bounding box.

    .. md-tab-set::

        .. md-tab-item:: only border

            .. social-card:: { "debug": true }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: "#4051B2" }
                  - ellipse:
                      border:
                        width: 50
                        color: "red"
                    size: { width: 500, height: 300 }
                    offset: { x: 350, y: 165 }

        .. md-tab-item:: only fill

            .. social-card:: { "debug": true }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: "#4051B2" }
                  - ellipse:
                      color: "green"
                    size: { width: 300, height: 500 }
                    offset: { x: 450, y: 65 }

        .. md-tab-item:: border and fill

            .. social-card:: { "debug": true }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: "#4051B2" }
                  - ellipse:
                      border:
                        width: 50
                        color: "red"
                      color: "green"
                    size: { width: 400, height: 400 }
                    offset: { x: 400, y: 115 }
    """

    border: Border = Border()
    """The shape's outlining `border <Border>` specification."""
    color: Optional[str] = None
    """The shape's fill color."""


class Rectangle(Ellipse):
    """Similar to how the `ellipse <Ellipse>` attribute works, This layer
    attribute provides a way of drawing rectangles with rounded corners.

    .. md-tab-set::

        .. md-tab-item:: only border

            .. social-card:: { "debug": true }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: "#4051B2" }
                  - rectangle:
                      radius: 50
                      border:
                        width: 30
                        color: "red"
                    size: { width: 500, height: 300 }
                    offset: { x: 350, y: 165 }

        .. md-tab-item:: only fill

            .. social-card:: { "debug": true }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: "#4051B2" }
                  - rectangle:
                      radius: 50
                      color: "green"
                    size: { width: 300, height: 500 }
                    offset: { x: 450, y: 65 }

        .. md-tab-item:: border and fill

            .. social-card:: { "debug": true }
                :dry-run:
                :hide-conf:

                layers:
                  - background: { color: "#4051B2" }
                  - rectangle:
                      radius: 50
                      border:
                        width: 30
                        color: "red"
                      color: "green"
                    size: { width: 400, height: 400 }
                    offset: { x: 400, y: 115 }
    """

    radius: Optional[Union[int, float]] = 0
    """The radius of the rounded corner in pixels. Defaults to 0 (no rounding).

    .. tip::
        If the `radius` is smaller than the `border.width <Border.width>`, then the
        border's inner `corners` will not be rounded.
    """
    corners: List[Literal["top left", "top right", "bottom right", "bottom left"]] = [
        "top left",
        "top right",
        "bottom right",
        "bottom left",
    ]
    """This YAML list of strings specifies which corners are rounded. By default all
    corners are rounded. The supported values are:

    .. list-table::

        * - :si-icon:`material/arrow-top-left` ``"top left"``
          - :si-icon:`material/arrow-top-right` ``"top right"``
        * - :si-icon:`material/arrow-bottom-left` ``"bottom left"``
          - :si-icon:`material/arrow-bottom-right` ``"bottom right"``
    .. warning::
        The `radius` must always be less than half the rectangle's minimum
        `width <Size.width>` or `height <Size.height>`. Otherwise, ``pillow`` will fail
        to render the rounded arc for the `corners`.
    .. social-card::
        :dry-run:

        layers:
          - background: { color: "#4051B2" }
          - size: { width: 100, height: 400 }
            offset: { x: 225, y: 115 }
            rectangle:
              radius: 49.9  # cannot be 50 because width is 100
              corners: ["top left", "bottom left"]
              color: "red"
          - size: { width: 600, height: 400 }
            offset: { x: 375, y: 115 }
            rectangle:
              radius: 199.9  # cannot be 200 because height is 400
              corners: ["top right", "bottom right"]
              color: "green"
    """


class LayerImage(CustomBaseModel):
    image: Optional[str] = None
    color: Optional[str] = None
    preserve_aspect: Union[bool, Literal["width", "height"]] = True
    """If an image is used that doesn't match the layer's `size <Size>`, then the image
    will be resized accordingly. This option can be used to control which horizontal
    `width <Size.width>` or vertical `height <Size.height>` or both (:yaml:`true`)
    constraints are respected. Set this option to :yaml:`false` to disable resizing the
    image. By default, this option is set to :yaml:`true`.

    If the image has to be resized then it is centered on the layer for which it is
    used.
    """


class Background(LayerImage):
    """When combining these attributes, the `image` is tinted with the `color`.

    .. hint::
        If no alpha transparency is included with the specified `color`, then the
        `color` will block out the `image`.
    .. social-card::
        :dry-run:

        layers:
          - background:
              image: images/rainbow.png
              color: "#000000AB"
    """

    image: Optional[str] = None
    """The path to an image used as the card's background. This path can be absolute or
    relative to one of the paths specified in
    `social_cards.image_paths <Social_Cards.image_paths>`.

    .. failure:: Missing file extensions

        If the image file's name does not include a file extension (eg ``.png``), then
        it is assumed to ba a SVG image (``.svg`` is appended to the filename).

    By default, this image will be resized to fit within the layer's `size <Size>`. See
    `preserve_aspect <Background.preserve_aspect>` for more details on resizing images.

    .. social-card::
        :dry-run:

        layers:
          - background:
              image: images/rainbow.png
    """
    color: Optional[str] = None
    """The color used as the background fill color. This color will overlay the entire
    `Background.image` (if specified). So be sure to add transparency (an alpha
    color value) when using both a background image and color.

    .. seealso:: Supported color options and syntax is determined by
        `pillow's supported color input`_.
    .. social-card::
        :dry-run:

        layers:
          - background:
              color: "#4051b5"
    """


class Icon(LayerImage):
    """When combining these attributes, the `image` is colorized by the specified
    `color`.

    .. hint:: If no `color` is specified, then the `image`\ 's original color is shown.
    .. social-card::
        :dry-run:

        layers:
          - background: { color: "#4051B5" }
          - size: { width: 150, height: 150 }
            offset: { x: 525, y: 240 }
            icon:
              image: sphinx_logo
              color: "white"
    """

    image: Optional[str] = None
    """An image file's path. This path can be absolute or relative to one of the paths
    specified in `social_cards.image_paths <Social_Cards.image_paths>`.

    By default, this image will be resized to fit within the layer's `size <Size>`. See
    `preserve_aspect <Icon.preserve_aspect>` for more details on resizing images.

    .. failure:: Missing file extensions

        If the image file's name does not include a file extension (eg ``.png``), then
        it is assumed to ba a SVG image (``.svg`` is appended to the filename).
    .. note::
        If no :attr:`color` is specified, then the image's original color will be shown.
        For SVG images without hard-coded color information, black will be used.

    .. social-card::
        :dry-run:

        layers:
          - background: { color: "#4051B5" }
          - size: { width: 150, height: 150 }
            offset: { x: 525, y: 240 }
            icon:
              image: sphinx_logo.svg
    """
    color: Optional[str] = None
    """The color used as the fill color. The actual image color is not used when
    specifying this, rather the non-transparent data is used as a mask for this value.

    .. seealso::
        Supported color options and syntax is determined by
        `pillow's supported color input`_.

    .. hint::
        If an alpha transparency is included with the specified `color`, then the
        `image` will become transparent as well.

    .. social-card::
        :dry-run:

        layers:
          - background: { color: "#4051B5" }
          - size: { width: 150, height: 150 }
            offset: { x: 525, y: 240 }
            icon:
              image: sphinx_logo.svg
              color: "#0000003F"
    """


class Line(CustomBaseModel):
    """These properties are used to calculate the font's size based on the layer's
    absolute maximum `size <Size>`."""

    #: The maximum number of lines that can be used in the layer.
    amount: PositiveInt = 1
    height: PositiveFloat = 1
    """The relative height allotted to each line. This has a direct affect on spacing
    between lines because each layer has an absolute maximum `size <Size>`.

    .. |height0.75| replace:: 75% of the appropriately available line
        height. Text will be smaller but the space between lines will be bigger.

    .. |height1| replace:: the full appropriately available line
        height. Text will be large enough to fit within of the appropriately available
        line height.

    .. |height1.25| replace:: 125% of the appropriately available line
        height. Text will be bigger but the space between lines will be smaller (can
        even be negative).

    .. |height2.0| replace:: 200% of the appropriately available line
        height. Text should never exceed the layer size, thus spacing between lines is
        adjusted accordingly.

    .. |height0.5| replace:: 50% of the appropriately available line
        height. Notice the spacing between lines is always equally proportionate to the
        line height.

    .. jinja::

        .. md-tab-set::

        {% for height in [0.75, 1, 1.25, 2.0, 0.5] %}
            .. md-tab-item:: :yaml:`height: {{ height }}`

                :yaml:`{{ height }}` means each line can have |height{{ height }}|

                .. social-card:: {"debug": true}
                    :dry-run:
                    :hide-layout:
                    :hide-conf:

                    layers:
                      - background: {color: "#4051b5"}
                      - offset: { x: 60, y: 150 }
                        size: { width: 832, height: 330 }
                        typography:
                          content: |
                            Typography
                            Glyphs
                            Pictograms
                          line:
                            amount: 3
                            height: {{ height }}
        {% endfor %}
    """


class Font(CustomBaseModel):
    """The specification that describes the font to be used.

    .. seealso:: Please review the :ref:`choosing-a-font` section."""

    family: str = "Roboto"
    """This option specifies which font to use for rendering the social card, which can
    be any font hosted by `Fontsource`_. Default is :python:`"Roboto"` if not using the
    sphinx-immaterial_ theme. However, the sphinx-immaterial theme's :themeconf:`font`
    option is used as a default if that theme is used.

    If the font specified is not a Roboto font and cannot be fetched from Fontsource_,
    then an exception is raised and the docs build is aborted.
    """
    style: str = "normal"
    """The style of the font to be used. Typically, this can be ``italic`` or
    ``normal``, but it depends on the styles available for the chosen `family`.

    .. failure:: There is no inline style parsing.
        :collapsible:

        Due to the way ``pillow`` loads fonts, there's no way to embed syntactic inline
        styles for individual words or phrases in the text content. ``**bold**`` and
        ``*italic*`` will not render as **bold** and *italic*.

        Instead, the layout customization could be used to individually layer stylized
        text.
    """
    weight: PositiveInt = 400
    """The weight of the font used. If this doesn't match the weights available, then
    the first weight defined for the font is used and a warning is emitted. Default is
    :yaml:`400`."""
    subset: Optional[str] = None
    """A subset type used for the font. If not specified, this will use the default
    defined for the font (eg. :python:`"latin"`)."""
    path: Optional[str] = None
    """The path to the TrueType font (``*.ttf``). If this is not specified, then it is
    set in accordance with the a cache corresponding to the `family`, `style`, `weight`,
    and `subset` options. If explicitly specified, then this value overrides the
    `family`, `style`, `weight`, and `subset` options.
    """


class Typography(CustomBaseModel):
    content: str
    """The text to be displayed. This can be a `Jinja syntax`_ that has access to the
    card's `jinja contexts <jinja-ctx>`.

    The text content is pre-processed (after parsed from `Jinja syntax`_) to allow
    comprehensive wrapping of words. This is beneficial for long winded programmatic
    names.

    .. caution::
        Beware that trailing whitespace is stripped from each line.

    .. md-tab-set::

        .. md-tab-item:: Long words

            .. social-card:: {"debug": true}
                :dry-run:
                :hide-conf:
                :hide-layout:
                :meta-data: {
                  "title":
                    "sphinx_social_cards.validators.LayerTypographyDataclass._fg_color"}
                :meta-data-caption: Using an API name as the page title

                layers:
                  - background: { color: '#4051B2' }
                  - size: { width: 920, height: 360 }
                    offset: { x: 60, y: 150 }
                    typography:
                      content: '{{ page.meta.title }}'
                      line: { amount: 4, height: 1.1 }
                      font: { family: Roboto Mono }

        .. md-tab-item:: Preserved line breaks

            .. note:: Line breaks are not supported when using :ref:`metadata-fields`.

            .. social-card:: {"debug": true}
                :dry-run:
                :layout-caption: Using a line break between words
                :hide-conf:

                layers:
                  - background: { color: '#4051B2' }
                  - size: { width: 920, height: 360 }
                    offset: { x: 60, y: 150 }
                    typography:
                      content: |
                        Paragraph 1

                            Line with leading spaces
                      line: { amount: 3 }
    """
    align: Literal[
        "start top",
        "start center",
        "start bottom",
        "center top",
        "center",
        "center center",
        "center bottom",
        "end top",
        "end center",
        "end bottom",
    ] = "start top"
    """The alignment of text used. This is a string in which the space-separated words
    respectively describe the horizontal and vertical alignment.

    .. list-table:: Alignment Options

        - * :si-icon:`material/arrow-top-left` ``start top``
          * :si-icon:`material/arrow-up` ``center top``
          * :si-icon:`material/arrow-top-right` ``end top``
        - * :si-icon:`material/arrow-left` ``start center``
          * :si-icon:`material/circle-small` ``center`` or ``center center``
          * :si-icon:`material/arrow-right` ``end center``
        - * :si-icon:`material/arrow-bottom-left` ``start bottom``
          * :si-icon:`material/arrow-down` ``center bottom``
          * :si-icon:`material/arrow-bottom-right` ``end bottom``
    """
    color: Optional[str] = None
    """The color to be used for the displayed text. If not specified, then this defaults
    to `cards_layout_options.color <Cards_Layout_Options.color>` (in most
    `pre-designed layouts <pre-designed-layouts>`)."""
    line: Line = Line()
    """The `line <Line>` specification which sets the `amount <Line.amount>` of lines
    and the `height <Line.height>` of each line. This is used to calculate the font's
    size."""
    overflow: bool = False
    """Set this option to :yaml:`true` to automatically shrink the font size enough to
    fit within the layer's `size <Size>`. By default (:yaml:`false`), text will be
    truncated when the layer' capacity is reached, and an ellipsis will be added.

    .. jinja::

        .. md-tab-set::

        {% for desc in ["off", "on"] %}
            .. md-tab-item:: :yaml:`overflow: {{ desc }}`

                .. social-card:: {"debug": true }
                    :dry-run:
                    :hide-layout:
                    :hide-conf:

                    layers:
                      - background: {color: "#4051b5"}
                      - offset: { x: 60, y: 150 }
                        size: { width: 832, height: 330 }
                        typography:
                          content: >
                            If we use a very long sentence, then we gleam how the text
                            will be truncated.
                          line:
                            amount: 3
                          {% if desc == 'on' -%}
                          overflow: true
                          {%- endif %}
          {% endfor %}
    """
    font: Optional[Font] = None
    """The specified font to use. If not specified, then this defaults to values in
    `cards_layout_options.font <Cards_Layout_Options.font>`.

    .. seealso:: Please review :ref:`choosing-a-font` section.
    """

    @field_validator("align")
    def _conform_center_align(cls, val: str) -> str:
        if val == "center":
            return "center center"
        return val
