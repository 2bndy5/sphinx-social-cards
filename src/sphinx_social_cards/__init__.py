"""
This extension enables the generation and embedding of social media cards (AKA "social
media previews").

.. social-card:: {"cards_layout": "default/variant"}
.. image-generator:: default/variant

.. note::
    This extension is heavily influenced by the `mkdocs-material theme's builtin social
    plugin <https://squidfunk.github.io/mkdocs-material/setup/setting-up-social-cards>`_.
    Beware that this does not imply interoperability. Some features supported in this
    extension are not supported in the mkdocs-material implementation and vice versa.

Dependencies
------------

The following dependencies are required:

- `PySide6 <https://doc.qt.io/qtforpython-6/quickstart.html>`_

Installing
----------

.. code-block:: text
    :caption: Install using ``pip``

    pip install sphinx-social-cards

Installing from the source hosted at https://github.com/2bndy5/sphinx-social-cards will
require Node.js (and npm) available to optimize and bundle SVG icons from npm packages.
See `image_paths` for a list of bundled icons.

Usage
-----

The :doc:`config` describes how to use this extension in your documentation's conf.py.
Additionally, the social cards generated can be tailored with :doc:`layouts/index`.
There are also :doc:`directive` provided for finite control over the generated image for
a specific page. Lastly, :doc:`plugins/index` can be used to easily share customizations
between documentation projects.
"""
import hashlib
import json
from pathlib import Path
import re
from typing import List, cast, Union, Any, Dict, Set, Optional
from urllib.parse import urlparse

import docutils.nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst.directives.images import Image
from pydantic import TypeAdapter
from sphinx.application import Sphinx
from sphinx.builders.html import StandaloneHTMLBuilder
from sphinx.directives.code import container_wrapper
from sphinx.environment import BuildEnvironment
from sphinx.transforms import SphinxTransform
from sphinx.config import Config
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger
from .validators import Social_Cards
from .validators.contexts import (
    JinjaContexts,
    Page,
    Config as ConfigCtx,
    Cards_Layout_Options,
)
from .generator import CardGenerator
from .metadata import (
    get_doc_meta_data,
    complete_doc_meta_data,
    add_doc_meta_data,
    get_default_page_title,
)
from .plugins import SPHINX_SOCIAL_CARDS_CONFIG_KEY, SPHINX_SOCIAL_CARDS_PLUGINS_ENV_KEY

LOGGER = getLogger(__name__)
_CARD_IMG_CHECK = re.compile(r"(?:property=og|name=twitter):image")

config_parser: TypeAdapter[Social_Cards] = TypeAdapter(Social_Cards)
layout_ctx_parser: TypeAdapter[Cards_Layout_Options] = TypeAdapter(Cards_Layout_Options)


def _load_config(app: Sphinx, config: Config):
    assert hasattr(config, "social_cards"), f"config not found: {dir(config)}"
    user_config: Dict[str, Any] = getattr(config, "social_cards")
    # LOGGER.info("config loaded: %r", user_config)
    card_config: Social_Cards = config_parser.validate_python(user_config)
    # LOGGER.info("layout options: %r", card_config.cards_layout_options)
    card_config.set_defaults(app.srcdir, config)
    # LOGGER.info("config parsed: %r", card_config)
    setattr(config, SPHINX_SOCIAL_CARDS_CONFIG_KEY, card_config)
    CardGenerator.doc_src = app.srcdir


def _assert_plugin_context(app: Sphinx):
    if not hasattr(app.env, SPHINX_SOCIAL_CARDS_PLUGINS_ENV_KEY):
        setattr(app.env, SPHINX_SOCIAL_CARDS_PLUGINS_ENV_KEY, {})


def flush_cache(
    app: Sphinx,
    env: BuildEnvironment,
    added: Set[str],
    changed: Set[str],
    removed: Set[str],
):
    ext_config: Social_Cards = app.config[SPHINX_SOCIAL_CARDS_CONFIG_KEY]
    assert isinstance(ext_config.cache_dir, (str, Path))
    cache_root = Path(app.srcdir, ext_config.cache_dir)
    # flush all resized images
    resized_images = cache_root.glob("*.png")
    for img in resized_images:
        img.unlink()
    # removing example images (from directive dry-runs)
    cache_root = cache_root / ".social_card_examples"
    for doc_name in added | changed | removed:
        parts = doc_name.split("/")
        basename = parts[-1]
        ex_images = Path(cache_root, *parts[:-1]).glob(f"{basename}-*.png")
        for img in ex_images:
            img.unlink()
    return []


class SocialCardTransform(SphinxTransform):
    """Adds metadata and creates an image if needed."""

    default_priority = 600

    def apply(self, **kwargs: Any) -> None:
        conf: Social_Cards = self.config[SPHINX_SOCIAL_CARDS_CONFIG_KEY]
        builder = self.app.builder
        if self.document is None or not isinstance(builder, StandaloneHTMLBuilder):
            return
        doc_path = self.env.doc2path(self.env.docname, base=False)
        if conf.enable and (
            doc_path in conf.cards_exclude and doc_path not in conf.cards_include
        ):
            return
        elif not conf.enable and doc_path not in conf.cards_include:
            return

        meta_data = get_doc_meta_data(self.document)
        LOGGER.debug("meta_data found:\n%s", json.dumps(meta_data, indent=2))

        page_meta: Dict[str, str] = {}
        if "title" in meta_data:
            page_meta.update(title=meta_data["title"])
        if "description" in meta_data:
            page_meta.update(description=meta_data["description"])
        if "icon" in meta_data:
            page_meta.update(icon=meta_data.pop("icon"))
        if "card-icon" in meta_data:
            page_meta.update(icon=meta_data.pop("card-icon"))
        page_meta.update({k: v for k, v in meta_data.items()})
        page_title = get_default_page_title(self.document)
        description = cast(str, page_meta.get("description", conf.description))
        site_url = urlparse(conf.site_url)
        ctx_url = site_url.netloc + site_url.path
        page_uri = builder.get_target_uri(self.env.docname).rstrip(builder.link_suffix)

        # check if image was already generated by the social-card directive
        for key in meta_data.keys():
            if _CARD_IMG_CHECK.match(key) is not None:
                # LOGGER.info("card already generated for %s", self.env.docname)
                return

        # generate the image
        card_contexts = JinjaContexts(
            layout=conf.cards_layout_options,
            config=ConfigCtx(
                docstitle=getattr(self.config, "project", ""),
                theme=getattr(self.config, "html_theme_options", {}),
                site_url=ctx_url,
                author=getattr(self.config, "author", ""),
                language=cast(str, getattr(self.config, "language", "en")),
                today=getattr(self.config, "today", None),
                site_description=conf.description,
            ),
            page=Page(
                meta=page_meta,
                title=page_title,
                canonical_url="/".join([ctx_url, page_uri]),
                is_homepage=self.env.docname == getattr(self.config, "master_doc"),
            ),
            plugin=getattr(self.env, SPHINX_SOCIAL_CARDS_PLUGINS_ENV_KEY, {}),
        )
        factory = CardGenerator(config=conf, context=card_contexts)
        factory.parse_layout()
        card = factory.render_card()
        file_hash = hashlib.sha256(card.bits()).hexdigest()[:16]

        # add the updated meta_data
        img_uri, added_meta_data = complete_doc_meta_data(
            meta_data,
            builder,
            page_meta.get("title", page_title),
            description,
            conf,
            self.env.docname,
            file_hash,
        )
        assert img_uri is not None

        # save the image (& meta_data)
        img_path = Path(self.app.outdir, conf.path, img_uri)
        img_path.parent.mkdir(parents=True, exist_ok=True)
        card.save(str(img_path))
        add_doc_meta_data(self.document, added_meta_data)


class SocialCardDirective(SphinxDirective):
    optional_arguments = 1  # conf is an optional json string
    final_argument_whitespace = True
    has_content = True  # an example layout will be our content
    option_spec = {
        "name": directives.unchanged,
        "class": directives.class_option,
        "meta-data": directives.unchanged,  # meta-data is an optional json string
        "hide-conf": directives.flag,
        "hide-meta-data": directives.flag,
        "hide-layout": directives.flag,
        "dry-run": directives.flag,
        "meta-data-caption": directives.unchanged,
        "layout-caption": directives.unchanged,
        "conf-caption": directives.unchanged,
    }

    def run(self) -> List[docutils.nodes.Node]:
        """Run the directive."""
        container_node = docutils.nodes.container("", classes=["results"])

        # get existing meta_data, merge in meta_data overrides
        existing_meta_data = get_doc_meta_data(self.state.document)
        merged_meta_data = existing_meta_data.copy()
        new_meta_data = {}
        meta_overrides = self.options.get("meta-data", None)
        if meta_overrides is not None:
            new_meta_data = json.loads(meta_overrides)
            merged_meta_data.update(new_meta_data)

        # handle social_cards config
        conf_src = cast(Dict[str, Any], self.config["social_cards"]).copy()
        if not self.arguments:
            self.options["hide-conf"] = True
        else:
            conf_src.update(cast(dict, json.loads("".join(self.arguments))))
        conf: Social_Cards = config_parser.validate_python(conf_src)

        dry_run = "dry-run" in self.options
        valid_conf: Social_Cards = getattr(self.config, SPHINX_SOCIAL_CARDS_CONFIG_KEY)

        # render meta_data overrides (if any)
        if (
            "hide-meta-data" not in self.options
            and "meta-data" in self.options
            and dry_run
        ):
            meta_data_rst = "\n".join(
                [f":{key}: {val or ''}" for key, val in new_meta_data.items()]
            )
            meta_data_block = docutils.nodes.literal_block(
                meta_data_rst, meta_data_rst, language="rst"
            )
            caption_text = self.options.get(
                "meta-data-caption", "my-document.rst (meta-data)"
            )
            if caption_text:
                container_node += container_wrapper(self, meta_data_block, caption_text)
            else:
                container_node += meta_data_block

        # render social_cards config overrides (if any)
        if "hide-conf" not in self.options and dry_run:
            conf_py = f"social_cards = {json.dumps(conf_src, indent=4)}"
            conf_py = conf_py.replace(": true", ": True").replace(": false", ": False")
            conf_py_block = docutils.nodes.literal_block(
                conf_py, conf_py, language="python"
            )
            caption_text = self.options.get("conf-caption", "conf.py")
            if caption_text:
                container_node += container_wrapper(self, conf_py_block, caption_text)
            else:
                container_node += conf_py_block

        # merge in plugins contexts/layouts
        # NOTE: done before parsing layout and after creating code block
        conf.cards_layout_dir = list(
            set(conf.cards_layout_dir) | set(valid_conf.cards_layout_dir)
        )

        theme_options: dict = getattr(self.config, "html_theme_options")
        site_url = urlparse(conf.site_url)
        ctx_url = site_url.netloc + site_url.path.rstrip("/")
        page_uri = ""
        builder = self.env.app.builder
        if isinstance(builder, StandaloneHTMLBuilder):
            page_uri = builder.get_target_uri(self.env.docname).rstrip(
                builder.link_suffix
            )
        page_title = get_default_page_title(self.state.document)
        if page_title is None:
            LOGGER.error(
                "Could not find page title for %s. Did you place the directive after "
                "the top-level section title? NOTE: Top-level section titles in "
                "docstrings (via `autodoc` directives) may not be detected.",
                self.env.doc2path(self.env.docname, base=False),
            )

        contexts = JinjaContexts(
            layout=conf.cards_layout_options,
            page=Page(
                meta={key: val for key, val in merged_meta_data.items()},
                title=page_title,
                canonical_url="/".join([u for u in (ctx_url, page_uri) if u]),
                is_homepage=self.env.docname == getattr(self.config, "master_doc"),
            ),
            config=ConfigCtx(
                theme=theme_options,
                site_description=conf.description,
                site_url=ctx_url,
                docstitle=getattr(
                    self.config, "project", "An example name for a project"
                ),
                author=getattr(self.config, "author", ""),
                language=cast(str, getattr(self.config, "language", "en")),
                today=getattr(self.config, "today", None),
            ),
            plugin=getattr(self.env, SPHINX_SOCIAL_CARDS_PLUGINS_ENV_KEY, {}),
        )

        # set defaults after creating nodes to display config & meta_data
        conf.set_defaults(self.env.app.srcdir, self.config)

        factory = CardGenerator(context=contexts, config=conf)

        # render layout overrides (if any)
        layout_src: Optional[str] = None
        if self.content:
            layout_src = "\n".join(self.content)
            if "hide-layout" not in self.options and dry_run:
                layout_block = docutils.nodes.literal_block(
                    layout_src, layout_src, language="yaml"
                )
                caption_text = self.options.get("layout-caption", "my-layout.yml")
                if caption_text:
                    container_node += container_wrapper(
                        self, layout_block, caption_text
                    )
                else:
                    container_node += layout_block
        factory.parse_layout(layout_src)

        # generate the image
        img = factory.render_card()
        file_hash = hashlib.sha256(img.bits()).hexdigest()[:16]
        img_name = f"{self.env.docname}-{file_hash}.png"

        # save image; path (& meta_data injection) depends on `dry-run` option
        output_path: Union[Path, str] = Path(self.env.app.outdir, conf.path)
        if dry_run:
            output_path = self.env.app.srcdir
            uri_parts = Path(img_name).parts
            ref_uri = "../" * (len(uri_parts) - 1) + f"_images/{uri_parts[-1]}"
            ref_node = docutils.nodes.reference(refuri=ref_uri)
            img_name = str(Path(conf.cache_dir, ".social_card_examples", img_name))
            img_node = docutils.nodes.image(
                "",
                uri="../" * (len(uri_parts) - 1)
                + str(Path(img_name).relative_to(self.env.srcdir)),
                alt="A image generated by sphinx-social-cards",
                align="center",
                classes=self.options.get("class", []),
            )
            ref_node += img_node
            par_node = docutils.nodes.paragraph("", "", ref_node, classes=["result"])
            container_node += par_node
        else:
            # set meta_data and add it to the doctree
            existing_meta_data.pop("card-icon", None)
            img_uri, added_meta_data = complete_doc_meta_data(
                existing_meta_data,
                self.env.app.builder,
                title=merged_meta_data.get("title", "None"),
                description=merged_meta_data.get("description", conf.description),
                card_config=conf,
                page_name=self.env.docname,
                img_hash=file_hash,
            )
            if img_uri is None:  # if not using html builder
                return []  # this directive is incompatible with non-html builders
            add_doc_meta_data(self.state.document, added_meta_data)
        img_path = Path(output_path, img_name)
        img_path.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(img_path))

        self.set_source_info(container_node)
        self.add_name(container_node)
        return [container_node] if dry_run else []


class CardGeneratorDirective(SocialCardDirective, Image):
    has_content = True
    required_arguments = 0
    option_spec = {
        "name": directives.unchanged,
        "class": directives.class_option,
        "target": directives.unchanged,
        "alt": directives.unchanged,
        "height": directives.length_or_unitless,  # type: ignore[dict-item]
        "width": directives.length_or_percentage_or_unitless,
        "scale": directives.percentage,  # type: ignore[dict-item]
        "align": lambda arg: directives.choice(arg, Image.align_values),
    }
    hardcoded_options = ["dry-run", "hide-meta", "hide-conf", "hide-layout"]

    def run(self) -> List[docutils.nodes.Node]:
        # run the social-card directive and get the image's path and hyperlink refuri
        for key in self.hardcoded_options:
            self.options[key] = True
        conf: Social_Cards = getattr(self.config, SPHINX_SOCIAL_CARDS_CONFIG_KEY)
        self.arguments = json.dumps(
            {"cards_layout": "".join(self.arguments or [conf.cards_layout])}
        ).splitlines()
        results = SocialCardDirective.run(self)
        # structure returned should always be the same because we used hardcoded_options
        container_node = cast(List[docutils.nodes.Element], results)[0]
        assert container_node.children
        assert isinstance(container_node[0], docutils.nodes.paragraph)
        assert cast(docutils.nodes.Element, container_node[0]).children
        assert isinstance(container_node[0][0], docutils.nodes.reference)
        assert cast(docutils.nodes.Element, container_node[0][0]).children
        assert isinstance(container_node[0][0][0], docutils.nodes.image)
        img_uri = cast(str, container_node[0][0][0]["uri"]).replace("\\", "\\\\")
        ref_uri = container_node[0][0]["refuri"]

        # now run the image directive with the info from the social-card directive
        for key in self.hardcoded_options:
            self.options.pop(key)
        if "target" not in self.options:
            self.options["target"] = ref_uri
        self.arguments = [str(img_uri)]
        return Image.run(self)


def setup(app: Sphinx):
    app.add_config_value(
        "social_cards", default={}, rebuild="html", types=[Social_Cards]
    )
    app.add_transform(SocialCardTransform)
    app.connect("config-inited", _load_config)
    app.connect("builder-inited", _assert_plugin_context, priority=999)
    app.connect("env-get-outdated", flush_cache)
    app.add_directive("social-card", SocialCardDirective)
    app.add_directive("image-generator", CardGeneratorDirective)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
