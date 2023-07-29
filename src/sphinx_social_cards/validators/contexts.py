"""This module holds the data classes used to populate the jinja contexts."""
from importlib import import_module
import platform
import time
from typing import Dict, Optional, Any, cast

from pydantic import BaseModel, field_validator, Field, ConfigDict, field_serializer
from sphinx.search import languages, SearchLanguage
from typing_extensions import Annotated
from .common import CustomBaseModel, ColorType, PathType, serialize_color
from .layers import Icon, Font

time_fmt = "%B %#d %Y" if platform.system().lower() == "windows" else "%B %-d %Y"
today_default = time.strftime(time_fmt, time.localtime())


class Cards_Layout_Options(BaseModel):
    """There are some options that are used as default values for the layout's
    subsequent layers. These values are set with `cards_layout_options
    <Social_Cards.cards_layout_options>` and are added to the ``layout.*`` :ref:`jinja
    context <jinja-ctx>` (for customizable re-use in `layer <Layer>` attributes).

    .. seealso::
        This section heavily relies on knowledge about :ref:`using_jinja`
    """

    model_config = ConfigDict(
        validate_assignment=True, extra="allow", str_strip_whitespace=True
    )

    background_image: Optional[PathType] = None
    """The fallback value used for a layer's `background.image <Background.image>`
    attribute. Default is :python:`None`. This image will not be shown if the
    `background_color` has no alpha channel (transparency) value.

    .. social-card::
        {
            "cards_layout_options": {
                "background_image": "images/rainbow.png"
            }
        }
        :dry-run:

        layers:
          - background:
              image: '{{ layout.background_image }}'
    """
    background_color: Optional[ColorType] = None
    """The fallback value used for a layer's `background.color <Background.color>`
    attribute in most `pre-designed layouts <pre-designed-layouts>`. By default, this
    value is set to the :themeconf:`palette`\ [:themeconf:`primary`] color or
    :yaml:`"#4051B2"` for themes other than sphinx-immaterial_.

    .. social-card::
        {
            "cards_layout_options": {
                "background_color": "rgb(90, 32, 166)"
            }
        }
        :dry-run:

        layers:
          - background:
              color: '{{ layout.background_color | yaml }}'
    """
    color: Optional[ColorType] = None
    """The color used for the foreground text in most `pre-designed layouts
    <pre-designed-layouts>`. By default, this will be computed as :yaml:`"white"` or
    :yaml:`"black"` based on the `background_color`.

    .. social-card::
        {
            "cards_layout_options": {
                "color": "#0FF1CE"
            }
        }
        :dry-run:

        size: { width: 600, height: 125 }
        layers:
          - background: { color: black }
          - typography:
              content: "'{{ layout.color }}'"
              color: '{{ layout.color | yaml }}'
              align: center
              line: { amount: 2 }
    """
    accent: Optional[ColorType] = None
    """The color used as a foreground accentuating color. By default, this value is set
    to the :themeconf:`palette`\ [:themeconf:`accent`] color or :yaml:`"#4051B2"` for
    themes other than sphinx-immaterial_.

    .. social-card::
        {
            "cards_layout_options": {
                "accent": "hsl(35.7, 100%, 65.1%)"
            }
        }
        :dry-run:

        layers:
          - background:
              color: '{{ layout.accent| yaml }}'
    """
    font: Optional[Font] = None
    """The `font <Font>` specification to be used.

    .. seealso:: Please review :ref:`choosing-a-font` section.

    .. social-card::
        {
            "cards_layout_options": {
                "font": {
                    "family": "Roboto",
                    "style": "italic"
                }
            }
        }
        :dry-run:

        size: { width: 600, height: 125 }
        layers:
          - background: { color: black }
          - typography:
              content: '{{ layout.font.family }}' '{{ layout.font.style }}'
              line: { amount: 2 }
              align: center
    """
    logo: Optional[Icon] = None
    """The icon used for branding of the site. By default, this will be the
    :confval:`html_logo` (or the sphinx-immaterial_ theme's
    :themeconf:`icon`\ [:themeconf:`logo`]).

    In most :ref:`pre-designed layouts <pre-designed-layouts>`, the image's `color
    <Icon.color>` is used as is. This behavior can be changed by setting this option.

    Most :ref:`pre-designed layouts <pre-designed-layouts>` use the :meta-field:`icon`
    metadata field to overridden the `image <Icon.image>` value per page.

    .. social-card::
        {
            "cards_layout_options": {
                "logo": {
                    "image": "images/message.png",
                    "color": "#4051B2"
                }
            }
        }
        :dry-run:

        size: { width: 250, height: 250 }
        layers:
          - background: { color: black }
          - icon:
              image: '{{ layout.logo.image }}'
              color: '{{ layout.logo.color | yaml }}'
    """

    @field_serializer("background_color")
    def serialize_bg_color(self, color: Optional[ColorType], _info):
        return serialize_color(color)

    @field_serializer("color")
    def serialize_fg_color(self, color: Optional[ColorType], _info):
        return serialize_color(color)

    @field_serializer("accent")
    def serialize_accent_color(self, color: Optional[ColorType], _info):
        return serialize_color(color)


class Config(BaseModel):
    """A `dict` whose items expose some configuration options in conf.py. The following
    items are included in this context:"""

    theme: Dict[str, Any] = {}
    """A `dict` whose items correspond to the :confval:`html_theme_options`. This
    `dict` is very dependent on the choice of sphinx theme and what it defines in its
    ``theme.conf`` file."""
    #: The `social_cards.description <Social_Cards.description>` value.
    site_description: Optional[str] = None
    site_url: str
    """The `social_cards.site_url <Social_Cards.site_url>` value. This value has the
    transport protocol (``https://``) automatically removed for convenience."""
    #: The :confval:`project` value which is used as the site's title.
    docstitle: Optional[str] = None
    #: The :confval:`author` value.
    author: Optional[str] = None
    #: The full language name that corresponds to the :confval:`language` value
    language: Annotated[Optional[str], Field(validate_default=True)] = None
    today: Optional[str] = today_default
    """The :confval:`today` value. Defaults to current date using
    :python:`"\<month> \<day> \<year>"` format."""

    @field_validator("today")
    def revert_today_default(cls, val: Optional[str]):
        if not val:
            return today_default
        return val

    @field_validator("language")
    def _get_lang_name(cls, val: Optional[str]) -> Optional[str]:
        if val is None:
            val = "en"
        lang_class = languages.get(val)
        if lang_class is None:
            return val
        if isinstance(lang_class, type(SearchLanguage)):
            return lang_class.language_name
        assert isinstance(lang_class, str)
        module, attr = lang_class.rsplit(".", 1)
        return cast(SearchLanguage, getattr(import_module(module), attr)).language_name


class Page(CustomBaseModel):
    """A `dict` whose items include the following:"""

    meta: Dict[str, str] = {}
    """A `dict` whose items correspond to the page's :ref:`Metadata <metadata-fields>`
    (or :du-tree:`meta element(s) <meta>` created via the :du-dir:`meta directive
    <metadata>`)."""
    #: The value of the title of the page for which the card is generated.
    title: Optional[str] = None
    canonical_url: str = ""
    """A URL of the current page relative to the `site_url <Social_Cards.site_url>`
    value."""
    #: A `bool` value that indicates if the current page is the root of the site.
    is_homepage: bool = False


class JinjaContexts(BaseModel):
    #: A `dict` whose items correspond to the `cards_layout_options`.
    layout: Cards_Layout_Options = Cards_Layout_Options()
    config: Config = Config(site_url="")
    page: Page = Page()
    plugin: Dict[str, Any] = {}
    """A `dict` whose items correspond to :doc:`compatible plugins
    <../plugins/index>`\ ' contexts."""
