"""
``sphinx_social_cards.plugins``
    This module holds the information that plugins need to interface with the
    sphinx_social_cards extension. Currently, this module holds the following:
"""
import logging
from pathlib import Path
from typing import Dict, Any, Union
from sphinx.application import Sphinx
from ..validators import Social_Cards

LOGGER = logging.getLogger("sphinx_social_cards.plugins")

SPHINX_SOCIAL_CARDS_PLUGINS_ENV_KEY = "sphinx_social_cards_plugins"
"""The Sphinx builder environment key that points to the `plugin <JinjaContexts.plugin>`
    `jinja contexts <jinja-ctx>`."""

SPHINX_SOCIAL_CARDS_CONFIG_KEY = "sphinx_social_cards"
"""The Sphinx config validated object from conf.py. This key always points to a
`Social_Cards` object."""


def add_jinja_context(app: Sphinx, jinja_ctx: Dict[str, Any]):
    """Adds a `dict` to the builder environment key for `plugin <JinjaContexts.plugin>`
    `jinja contexts <jinja-ctx>`."""
    plugins_env = getattr(app.env, SPHINX_SOCIAL_CARDS_PLUGINS_ENV_KEY, {})
    plugins_env.update(jinja_ctx)
    LOGGER.info("Adding social-card jinja context: %r", jinja_ctx)
    setattr(app.env, SPHINX_SOCIAL_CARDS_PLUGINS_ENV_KEY, plugins_env)


def add_layouts_dir(app: Sphinx, layouts_dir: Union[str, Path]):
    """Adds a `str` or :py:class:`~pathlib.Path` of new layouts to the
    `cards_layout_dir` `list`."""
    layouts_dir = Path(layouts_dir).resolve()
    card_config: Social_Cards = getattr(app.config, SPHINX_SOCIAL_CARDS_CONFIG_KEY)
    LOGGER.info("Adding social-card layouts path: %s", str(layouts_dir))
    card_config.cards_layout_dir.append(str(layouts_dir))
    setattr(app.config, SPHINX_SOCIAL_CARDS_CONFIG_KEY, card_config)


def add_images_dir(app: Sphinx, images_dir: Union[str, Path]):
    """Adds a `str` or :py:class:`~pathlib.Path` of new images to the
    `image_paths` `list`."""
    images_dir = Path(images_dir).resolve()
    card_config: Social_Cards = getattr(app.config, SPHINX_SOCIAL_CARDS_CONFIG_KEY)
    LOGGER.info("Adding social-card images path: %s", str(images_dir))
    card_config.image_paths.append(str(images_dir))
    setattr(app.config, SPHINX_SOCIAL_CARDS_CONFIG_KEY, card_config)
