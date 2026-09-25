import math
import mimetypes
import re
from logging import getLogger
from pathlib import Path
from urllib.parse import urlsplit

import img_gen
from jinja2 import TemplateNotFound, FileSystemLoader, Template
from jinja2.sandbox import SandboxedEnvironment
from sphinx.util import isurl
import yaml

from .validators import Social_Cards, try_request
from .validators.contexts import JinjaContexts

LOGGER = getLogger(__name__)
_DEFAULT_LAYOUT_DIR = Path(__file__).parent / "layouts"


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

    doc_src: str | Path = ""

    def __init__(self, context: JinjaContexts, config: Social_Cards):
        self.context = context.model_dump()
        self.context["math"] = math
        self.config = config
        self.jinja_env = SandboxedEnvironment(
            loader=FileSystemLoader(
                [
                    str(fp if Path(fp).is_absolute() else Path(self.doc_src, fp).resolve())
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
        self.jinja_env.line_comment_prefix = "##"
        self.jinja_env.finalize = lambda output: "null" if output is None else output
        self.jinja_env.filters["yaml"] = self._yaml_filter
        self.jinja_env.filters["cache_url"] = self._cache_url

    @staticmethod
    def _yaml_filter(x) -> str:
        """Serialize a value to an inline YAML string for use in Jinja2 templates."""
        if isinstance(x, img_gen.Font):
            data: dict = {
                "family": x.family,
                "style": x.style,
                "subset": x.subset,
                "weight": x.weight.value,
            }
            if x.path is not None:
                data["path"] = x.path
            return yaml.safe_dump(data, default_flow_style=True).rstrip("\n...\n").rstrip("\n")
        if isinstance(x, img_gen.Icon):
            data = {"image": x.image}
            return yaml.safe_dump(data, default_flow_style=True).rstrip("\n...\n").rstrip("\n")
        return yaml.safe_dump(x, default_flow_style=True).rstrip("\n...\n").rstrip("\n")

    def _cache_url(self, url: str) -> str:
        """Jinja2 | cache_url filter: download a remote URL to cache_dir and return the
        local path string relative to cache_dir. Non-URL values are returned unchanged."""
        if not isurl(url):
            return url
        response = try_request(url)
        stem = Path(urlsplit(url).path).name or "cached"
        # Derive file extension from the response Content-Type header
        content_type = response.headers.get("Content-Type", "").split(";")[0].strip()
        ext = mimetypes.guess_extension(content_type) or Path(urlsplit(url).path).suffix
        # Normalize platform aliases (Windows mimetypes can return .jpe, .jpeg)
        ext = {".jpe": ".jpg", ".jpeg": ".jpg"}.get(ext, ext)
        fname = stem + ext
        cached = Path(self.config.cache_dir, fname)
        cached.write_bytes(response.content)
        # Return absolute path with forward slashes — backslashes would be invalid
        # YAML escape sequences when embedded in a double-quoted YAML string.
        return cached.as_posix()

    def parse_layout(self, content: str | None = None):
        """Render the Jinja2 layout template and store the resulting YAML string in
        ``self._rendered_yaml``."""
        template: Template
        if content is not None:
            template = self.jinja_env.from_string(content)
            self._rendered_yaml: str = template.render(self.context).strip()
        else:
            for ext in (".yml", ".yaml", ".YML", ".YAML"):
                try:
                    template = self.jinja_env.get_template(self.config.cards_layout + ext)
                    break
                except TemplateNotFound:
                    continue
            else:
                raise ValueError(f"Could not find layout: '{self.config.cards_layout}'")
            self._rendered_yaml = template.render(self.context)
