"""This module contains validating dataclasses for the configurations in python"""
from pathlib import Path
from typing import Union, List, Optional, cast, Dict, Set

from pydantic import field_validator, PrivateAttr
from pydantic_extra_types.color import Color
import requests
from sphinx.config import Config
from sphinx.util import isurl
from sphinx.util.logging import getLogger

from .common import CustomBaseModel, PathType
from .layers import Icon, Font
from .layout import Layout
from .contexts import Cards_Layout_Options
from ..colors import auto_get_fg_color, MD_COLORS

LOGGER = getLogger(__name__)
REQUEST_TIMEOUT = (5, 10)


def try_request(url, timeout=REQUEST_TIMEOUT, **kwargs) -> requests.Response:
    response = requests.get(url, timeout=timeout, **kwargs)
    if response.status_code != 200:
        raise RuntimeError(f"requested {url} returned {response.status_code}")
    return response


class Debug(CustomBaseModel):
    """To ease creation of custom layouts, optional debugging glyphs can be `enable`\ d
    in the generated social card images.

    .. social-card:: {"debug": true}
        :dry-run:

    Each layer will have a boundary box drawn with some text to indicate the layer
    number (as ordered in the list of layout `layers <Layout.layers>`) and corresponding
    orientation.

    - The text in the top-left corner indicates the layer number, `x <Offset.x>`
      and `y <Offset.y>`.
    - The text in the bottom-right corner indicates the layer number,
      `width <Size.width>` and `height <Size.height>`.
    """

    #: If set to :python:`True`, then debugging outlines and labels are drawn.
    enable: bool = False
    grid: bool = True
    """If set to :python:`True` (the default) and `enable`\ d, then a grid of dots are
    drawn."""
    grid_step: int = 30
    """If `grid` is enabled, then this `int` specifies the distance (in pixels) between
    each dot in the grid. Defaults to :python:`30`.

    .. social-card:: {"debug": {"enable": true, "grid_step": 15}}
        :dry-run:
    """
    color: Color = Color("grey")
    """The color used to draw the debugging outlines, labels, and grid. The color for
    the debugging text is automatically set based on this color value.

    .. social-card:: {"debug": {"enable": true, "color": "black"}}
        :dry-run:
    """


class Social_Cards(CustomBaseModel):
    """A `dict` of configurations related to generating social media cards.
    Each attribute equates to a supported configuration option.

    Some options use another data class to validate its values, so be mindful of the
    documented attributes' datatype.

    .. literalinclude:: ../tests/conftest.py
        :language: python
        :caption: A minimal/required configuration in conf.py
        :start-after: # -- Options for sphinx_social_cards
        :end-at: }
    """

    site_url: str
    """This required option will be the base URL that social media platforms use to
    fetch the social card's image."""
    description: str = ""
    """This option will be used as the description metadata for all generated
    pages. It can be overridden for individual pages using the :meta-field:`description`
    metadata role."""
    enable: bool = True
    """Set this option to :python:`False` to disable automatic generation of social
    cards for each page. The :rst:dir:`social-card` directive can be used to invoke or
    override social card generation for a specific page."""
    cards_layout: str = "default"
    """The layout file's name used to generate the social cards. If using a custom-made
    layout (not a pre-made layout), then the layout file **must** be a YAML file. If the
    the `cards_layout_dir` is specified, then that path is searched for a matching
    layout before searching the default path of pre-made layouts.

    .. _pre-designed-layouts:

    This extension ships with some pre-made layouts for convenience.

    .. jinja:: layouts

        .. md-tab-set::

        {% for layout in layouts %}
            .. md-tab-item:: {{ layout }}

                .. example:: Full ``{{ layout }}`` layout syntax
                    :collapsible:

                    .. literalinclude::
                        ../src/sphinx_social_cards/layouts/{{ layout }}.yml
                        :language: yaml
                .. social-card:: {"cards_layout": "{{ layout }}"}
                    :dry-run:
                    {% if layout == 'blog' -%}
                    :meta-data:
                        {
                            "read-time": "5 minutes",
                            "avatar": "images/avatar.jpg",
                            "tags": "sphinx, social, cards"
                        }
                    {%- endif %}
        {% endfor %}
    """
    cards_layout_dir: List[PathType] = []
    """The list of paths (absolute or relative to conf.py) where the `cards_layout` is
    located. In the case of similarly named layout files, the order in this list takes
    precedence."""
    cards_layout_options: Cards_Layout_Options = Cards_Layout_Options()
    """A set (`dict`) of options that can be accessed via the ``layout.*`` :ref:`jinja
    context <jinja-ctx>`. See `cards_layout_options <Cards_Layout_Options>` for more
    detail."""
    cards_exclude: Union[List[str], Set[str]] = []
    """This `list` can be used to exclude certain pages from generating social cards.
    Default is an empty `list`. |clude-list|

    .. |clude-list| replace:: Each item **must** be relative to the directory
        containing the conf.py file. :mod:`Glob patterns <glob>` are supported, and file
        suffixes are only required when specifying an individual document source.

    .. code-block:: python
        :caption: exclude all docs in the ``*-generated`` directories and a file
            named ``changelog``

        social_cards = {
            "cards_exclude": [
                "*-generated/*", # (1)!
                "changelog.rst",
            ]
        }
    .. code-annotations::
        1. Use ``**`` to include all subdirectories
    .. note::
        This option does not affect the :rst:dir:`social-card` directive.
    """
    cards_include: Union[List[str], Set[str]] = []
    """This `list` can be used to include certain pages from `cards_exclude` `list`.
    Default is an empty `list`. |clude-list|

    .. code-block:: python
        :caption: include all docs in the ``blog-posts`` folder

        social_cards = {
            "cards_include": [
                "blog-posts/*",
            ]
        }
    """
    image_paths: List[PathType] = []
    """A list of directories that contain images to be used in the creation of social
    cards. By default, the path to the directory containing the conf.py file is
    automatically added to this list. Each entry in this list can be an absolute path or
    a path relative to the conf.py file.

    This extension includes bundled SVG icons with distribution. The path to the
    bundled icons are appended to this list automatically.

    :Bundled Icons:
        .. list-table::
            :header-rows: 1

            * - name
              - Referenced in layouts using
            * - :si-icon:`sphinx_logo` Sphinx logo
              - ``sphinx_logo``
            * - :si-icon:`material/material-design`
                `Material Design <https://materialdesignicons.com/>`_
              - ``material/<icon-name>``
            * - :si-icon:`fontawesome/regular/font-awesome`
                `Font Awesome <https://fontawesome.com/search?m=free>`_
              - ``fontawesome/<brands|regular|solid>/<icon-name>``
            * - :si-icon:`octicons/mark-github-16`
                `Octicons <https://octicons.github.com/>`_
              - ``octicons/<icon-name>``
            * - :si-icon:`simple/simpleicons`
                `Simple Icons <https://simpleicons.org/>`_
              - ``simple/<icon-name>``
    """
    debug: Union[Debug, bool] = Debug()
    """A field to specify layout debugging helpers. See `Debugging Layouts`_ for more
    detail."""
    _parsed_layout: Layout = PrivateAttr(default=Layout())
    path: str = "_static/social_cards"
    """This option specifies where the generated social card images will be written to.
    It's normally not necessary to change this option. Defaults to the documentation's
    output in the subfolder '_static/social_cards'."""
    cache_dir: Union[str, Path] = "social_cards_cache"
    """The directory (relative to the conf.py file) that is used to store cached data
    for generating the social cards. By default, this will create/use a directory named
    :python:`"social_cards_cache"` located adjacent to the conf.py file.

    .. tip::
        :title: Caching Fonts

        This path is also used to cache the downloaded fonts except for the distributed
        cache of Roboto font variants. If this path is checked into a git remote
        (such as repository hosted on GitHub), then the cache of fonts can be shared
        with project collaborators or reused in a Continuous Integration workflow.

        .. code-block:: text
            :caption: .gitignore

            # ignore cached images, but check in cached fonts
            doc/social_cards_cache/**
            !docs/social_cards_cache/fonts/*
    """

    @field_validator("debug")
    def validate_debug(cls, val: Union[bool, Debug]) -> Debug:
        if isinstance(val, bool):
            return Debug(enable=val)
        return val

    def get_fonts(self) -> List[Font]:
        assert self.cards_layout_options.font is not None
        fonts: List[Font] = [self.cards_layout_options.font]
        for layer in self._parsed_layout.layers:
            if layer.typography is not None and layer.typography.font is not None:
                fonts.append(layer.typography.font)
        # LOGGER.info("found %d typography layers with fonts", len(fonts))
        return fonts

    def set_defaults(self, doc_src: str, config: Config):
        # sets the default values for colors, fonts, logo, and paths based on sphinx'
        # runtime configuration
        theme_options = getattr(config, "html_theme_options")
        self._set_default_paths(doc_src)
        self._set_default_colors(theme_options)
        self._set_default_font(theme_options)
        self._set_default_logo(config, theme_options)

    def _set_default_paths(self, doc_src: str):
        for index, possible_dir in enumerate(self.image_paths):
            possible = Path(possible_dir)
            if not possible.is_absolute():
                possible = Path(doc_src, possible)
            if not possible.exists():
                raise FileNotFoundError(f"directory does not exist: {possible}")
            self.image_paths[index] = possible
        cache_dir = Path(self.cache_dir)
        if not cache_dir.is_absolute():
            cache_dir = Path(doc_src, cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir = cache_dir

        excluded: Set[str] = set()
        for pattern in self.cards_exclude:
            for match in Path(doc_src).glob(pattern):
                rel_uri = match.relative_to(doc_src).as_posix()
                excluded.add(rel_uri)
        self.cards_exclude = excluded
        included: Set[str] = set()
        for pattern in self.cards_include:
            for match in Path(doc_src).glob(pattern):
                rel_uri = match.relative_to(doc_src).as_posix()
                included.add(rel_uri)
        self.cards_include = included

    def _set_default_logo(self, config: Config, theme_options: dict):
        theme_icon: Optional[Dict[str, str]] = theme_options.get("icon", None)
        theme_logo: Optional[str] = None
        if theme_icon is not None and "logo" in theme_icon:
            tmp = (
                Path(__file__).parent.parent / ".icons" / (theme_icon["logo"] + ".svg")
            )
            if not tmp.exists():
                raise ValueError(f"Could not find image: {theme_icon['logo']}")
            theme_logo = str(tmp)
        if self.cards_layout_options.logo is None:
            self.cards_layout_options.logo = Icon(
                image=getattr(config, "html_logo", None) or theme_logo
            )
        if self.cards_layout_options.logo.image is not None and isurl(
            self.cards_layout_options.logo.image
        ):
            response = try_request(self.cards_layout_options.logo.image)
            f_name = Path(self.cards_layout_options.logo.image).name
            cache_logo = Path(self.cache_dir, f_name)
            cache_logo.write_bytes(response.content)
            self.cards_layout_options.logo.image = str(cache_logo)

    def _set_default_colors(self, theme_options: dict):
        color = self.cards_layout_options.background_color
        accent = self.cards_layout_options.accent
        if any([color is None, accent is None]):
            # try getting primary color from sphinx-immaterial theme's config
            palette = cast(
                Union[List[Dict[str, str]], Dict[str, str]],
                theme_options.get("palette"),
            )
            if isinstance(palette, list):  # using light/dark mode toggle
                color = color or MD_COLORS.get(palette[0].get("primary", "indigo"))
                accent = accent or MD_COLORS.get(palette[0].get("accent", "indigo"))
            elif isinstance(palette, dict):  # using a single palette
                color = color or MD_COLORS.get(palette.get("primary", "indigo"))
                accent = accent or MD_COLORS.get(palette.get("accent", "indigo"))
            else:  # using a sane default (for other themes)
                color, accent = (color or "indigo", accent or "indigo")
        assert color is not None and accent is not None
        if self.cards_layout_options.background_color is None:
            self.cards_layout_options.background_color = color
        if self.cards_layout_options.accent is None:
            self.cards_layout_options.accent = accent
        if self.cards_layout_options.color is None:
            # compute fallback based on bg color
            self.cards_layout_options.color = auto_get_fg_color(
                self.cards_layout_options.background_color
            )

    def _set_default_font(self, theme_options: dict):
        if self.cards_layout_options.font is not None:
            return
        if (
            "font" in theme_options
            and isinstance(theme_options["font"], dict)
            and "text" in theme_options["font"]
            and isinstance(theme_options["font"]["text"], str)
        ):
            self.cards_layout_options.font = Font(family=theme_options["font"]["text"])
        else:
            self.cards_layout_options.font = Font()
