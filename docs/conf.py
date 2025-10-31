import os
from pathlib import Path
import platform
import time

import docutils.nodes
from importlib.metadata import metadata as get_metadata
from PySide6.QtGui import QGradient
import sphinx
import sphinx.addnodes
from sphinx.application import Sphinx
import sphinx.domains.python
from sphinx.environment import BuildEnvironment
import sphinx.config
from sphinx.util.logging import getLogger
import sphinx.util.typing
from typing import Literal, cast

LOGGER = getLogger(__name__)

if sphinx.version_info >= (6, 1):
    stringify = sphinx.util.typing.stringify_annotation
else:
    stringify = sphinx.util.typing.stringify

# Need a way to avoid hitting the GitHub REST API rate limit in repo CI
use_gh_rest_api = False
if "CI" not in os.environ or (os.environ.get("CI", False) and platform.system().lower() == "linux"):
    # Only use the GH REST API in CI when building docs for Linux.
    # Also allow local builds to use the GH REST API.
    use_gh_rest_api = True
    LOGGER.info("NOTE: GitHub REST API will be used (if info cache not found or outdated)")


pkg_meta: dict[str, str | list[str]] = get_metadata("sphinx-social-cards").json  # type: ignore[attr-defined]
assert "version" in pkg_meta
assert "name" in pkg_meta
assert "author_email" in pkg_meta
assert "summary" in pkg_meta
assert "project_url" in pkg_meta
urls = {}
for url_str in pkg_meta["project_url"]:
    name, url = url_str.split(", ")
    urls[name] = url

html_baseurl = os.environ.get(
    "READTHEDOCS_CANONICAL_URL", "https://2bndy5.github.io/sphinx-social-cards/"
)

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = pkg_meta["name"]
author = cast(str, pkg_meta["author_email"]).rsplit(" ", 1)[0]
copyright = f"2023, {author}"
release = pkg_meta["version"]

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx_jinja",
    "sphinx_immaterial",
    "sphinx_immaterial.theme_result",
    "sphinx_immaterial.task_lists",
    "sphinx_social_cards",
]

if use_gh_rest_api:
    extensions.append("sphinx_social_cards.plugins.github")

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
default_role = "any"
# BEGIN manually setting date
time_fmt = "%B %#d %Y" if platform.system().lower() == "windows" else "%B %-d %Y"
today = time.strftime(time_fmt, time.localtime())
# END manually setting date

# -- Options for sphinx_social_cards ------------------------------------------
social_cards = {
    "description": pkg_meta["summary"],
    "site_url": html_baseurl,
}

# -- Options for autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

autodoc_member_order = "bysource"
autodoc_default_options = {
    "exclude-members": "__init__, __new__, model_fields, model_config, model_computed_fields"
}
autodoc_class_signature = "separated"
add_module_names = False

# -- Options for intersphinx--------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "sphinx_doc": ("https://www.sphinx-doc.org/en/master", None),
    "sphinx_immaterial": ("https://sphinx-immaterial.readthedocs.io/en/latest", None),
    "jinja_doc": ("https://jinja.palletsprojects.com/en/latest", None),
    # "qt4py": ("https://doc.qt.io/qtforpython-6/", None),
}

# -- Options for extlinks ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html

extlinks = {
    "du-ref": (
        "http://docutils.sourceforge.net/docs/ref/rst/restructuredtext.html#%s",
        "rST %s",
    ),
    "du-dir": (
        "http://docutils.sourceforge.net/docs/ref/rst/directives.html#%s",
        "rST %s directive",
    ),
    "du-tree": (
        "https://docutils.sourceforge.io/docs/ref/doctree.html#%s",
        "%s",
    ),
    "sphinx-event": (
        "https://www.sphinx-doc.org/en/master/extdev/appapi.html#event-%s",
        "%s event",
    ),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_immaterial"
html_static_path = ["_static"]
html_title = "Sphinx Social Cards"
html_logo = "images/message.png"
html_favicon = "images/message.png"
html_css_files = ["extra-css.css"]

html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
        "edit": "material/file-edit-outline",
        "logo": "material/comment-text-multiple",
    },
    "repo_url": urls["Source"],
    "repo_name": "Sphinx-Social-Cards",
    "site_url": html_baseurl,
    "edit_uri": "blob/main/docs",
    "features": [
        "navigation.expand",
        # "navigation.tabs",
        # "toc.integrate",
        "navigation.sections",
        # "navigation.instant",
        "navigation.top",
        # "navigation.tracking",
        "search.share",
        "toc.follow",
        "toc.sticky",
        "content.tabs.link",
        "announce.dismiss",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "light-green",
            "accent": "light-blue",
            "toggle": {
                "icon": "material/lightbulb-outline",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "light-green",
            "accent": "light-blue",
            "toggle": {
                "icon": "material/lightbulb",
                "name": "Switch to light mode",
            },
        },
    ],
    "social": [
        {
            "icon": "fontawesome/brands/github",
            "link": "https://github.com/2bndy5/sphinx-social-cards",
            "name": "Source on github.com",
        },
        {
            "icon": "fontawesome/brands/python",
            "link": "https://pypi.org/project/sphinx-social-cards/",
        },
    ],
}

object_description_options = [
    (
        "std:meta-field",
        dict(toc_icon_class="data", toc_icon_text="M", generate_synopses="first_sentence"),
    ),
    ("py:class", dict(toc_icon_class="data", toc_icon_text="A")),
]

sphinx_immaterial_custom_admonitions = [
    {
        "name": "important",
        "icon": "material/alert-decagram",
        "override": True,
    },
    {
        "name": "tip",
        "icon": "material/school",
        "classes": ["success"],
        "override": True,
    },
    {
        "name": "yaml-power",
        "title": "The Power of YAML",
        "color": (223, 26, 137),
        "icon": "octicons/file-code-16",
    },
    {
        "name": "seealso",
        "color": (215, 59, 205),
        "icon": "octicons/eye-24",
        "override": True,
    },
]

custom_checkbox = True

sphinx_immaterial_icon_path = ["../src/sphinx_social_cards/.icons"]

rst_prolog = """
.. role:: python(code)
   :language: python
   :class: highlight

.. role:: yaml(code)
   :language: yaml
   :class: highlight

.. role:: jinja(code)
   :language: jinja
   :class: highlight

.. role:: rst(code)
   :language: rst
   :class: highlight

.. role:: html(code)
   :language: html
   :class: highlight

.. _sphinx-immaterial: https://jbms.github.io/sphinx-immaterial
.. _Fontsource: https://fontsource.org/
.. |Jinja syntax| replace:: :external:doc:`Jinja syntax <templates>`
"""

pkg_root = Path(__file__).parent.parent / "src" / "sphinx_social_cards"
shipped_layouts = Path(pkg_root, "layouts")
layouts = sorted(
    [
        layout.relative_to(shipped_layouts).with_suffix("").as_posix()
        for layout in shipped_layouts.rglob("*.yml")
    ],
    key=lambda n: n if n != "blog" else "z",
)

github_plugin_layouts = Path(pkg_root, "plugins", "github", "layouts")
if not use_gh_rest_api:
    github_layouts = []
else:
    github_layouts = sorted(
        [
            layout.relative_to(github_plugin_layouts).with_suffix("").as_posix()
            for layout in github_plugin_layouts.rglob("*.yml")
        ]
    )

pkg_deps = cast(list[str], pkg_meta["requires_dist"])
jinja_contexts = {
    "layouts": {"layouts": layouts},
    "github_plugin_layouts": {"layouts": github_layouts},
    "gradient_presets": {
        "presets": {p.value: p.name for p in list(QGradient.Preset) if p.name != "NumPresets"}
    },
    "deps": {"deps": pkg_deps},
}


def _parse_confval_signature(
    env: BuildEnvironment, signature: str, node: docutils.nodes.Node
) -> str:
    values = env.config.values
    registry_option = values.get(signature)
    node += sphinx.addnodes.desc_name(signature, signature)
    if not use_gh_rest_api and signature == "repo_url":
        # avoids triggering the below warning when CI is not supposed to use GH REST API
        return signature
    elif registry_option is None:
        LOGGER.error("Invalid config option: %r", signature, location=node)
    else:
        default, rebuild, types = registry_option
        if isinstance(types, sphinx.config.ENUM):
            types = (Literal[tuple(types.candidates)],)  # type: ignore
        if isinstance(types, type):
            types = (types,)
        if types:
            type_constraint = tuple(types)  # type: ignore
            node += sphinx.addnodes.desc_sig_punctuation(" : ", " : ")
            annotations = sphinx.domains.python._parse_annotation(stringify(type_constraint), env)
            node += sphinx.addnodes.desc_type("", "", *annotations)
        if not callable(default):
            node += sphinx.addnodes.desc_sig_punctuation(" = ", " = ")
            default_repr = repr(default)
            node += docutils.nodes.literal(  # type: ignore[assignment, operator]
                default_repr,
                default_repr,
                language="python",
                classes=["python", "code", "highlight"],
            )
    return signature


def setup(app: Sphinx):
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
        parse_node=_parse_confval_signature,
    )

    # only needed for cross-referencing theme configurations in sphinx-immaterial docs
    app.add_object_type(
        "themeconf",
        "themeconf",
        objname="theme configuration option",
        indextemplate="pair: %s; theme option",
    )

    app.add_object_type(
        "meta-field",
        "meta-field",
        objname="metadata field option",
        indextemplate="pair: %s; metadata field option",
    )
