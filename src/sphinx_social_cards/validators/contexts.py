"""This module holds the data classes used to populate the jinja contexts."""
from pathlib import Path
from typing import Union, Dict, Optional, Any

from pydantic import BaseModel
from .base_model import CustomBaseModel
from .layers import Icon, Font


class Cards_Layout_Options(BaseModel):
    """There are some options that are used as default values for the layout's
    subsequent layers. These values are set with `cards_layout_options
    <Social_Cards.cards_layout_options>` and are added to the ``layout.*`` :ref:`jinja
    context <jinja-ctx>` (for customizable re-use in `layer <Layer>` attributes).

    .. hint::
        You can also add your own options in this `dict`. Doing so will allow an
        alternative to :ref:`metadata fields <metadata-fields>` in custom layouts
        and ensure they're only used for social card generation.
    """

    background_image: Optional[Union[Path, str]] = None
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
    background_color: Optional[str] = None
    """The fallback value used for a layer's `background.color <Background.color>`
    attribute in most `pre-designed layouts <pre-designed-layouts>`. By default, this
    value is set to the :themeconf:`palette`\ [:themeconf:`primary`] color or
    :yaml:`"#4051B2"` for themes other than sphinx-immaterial_.

    .. social-card::
        {
            "cards_layout_options": {
                "background_color": "#4051B2"
            }
        }
        :dry-run:

        layers:
          - background:
              color: '{{ layout.background_color }}'
    """
    color: Optional[str] = None
    """The color used for the foreground text in most `pre-designed layouts
    <pre-designed-layouts>`. By default, this will be computed as :yaml:`"white"` or
    :yaml:`"black"` based on the `background_color`.

    .. social-card::
        {
            "cards_layout_options": {
                "color": "#4051B2"
            }
        }
        :dry-run:

        size: { width: 600, height: 125 }
        layers:
          - background: { color: black }
          - typography:
              content: '{{ layout.color }}'
              color: '{{ layout.color }}'
              align: center
    """
    accent: Optional[str] = None
    """The color used as a foreground accentuating color. By default, this value is set
    to the :themeconf:`palette`\ [:themeconf:`accent`] color or :yaml:`"#4EC5F1"` for
    themes other than sphinx-immaterial_.

    .. social-card::
        {
            "cards_layout_options": {
                "accent": "#4EC5F1"
            }
        }
        :dry-run:

        layers:
          - background:
              color: '{{ layout.accent }}'
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
              content: '{{ layout.font.family }} {{ layout.font.style }}'
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
                    "image": "tabler/message",
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
              color: '{{ layout.logo.color }}'
    """


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
    #: The :confval:`language` value.
    language: Optional[str] = None
    #: The :confval:`today` value.
    today: Optional[str] = None


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