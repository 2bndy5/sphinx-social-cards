import pathlib
import platform
import shutil
import time
from typing import Dict, Callable, Generator
import pytest
from sphinx.testing.path import path as SphinxPath


time_fmt = "%B %#d %Y" if platform.system().lower() == "windows" else "%B %-d %Y"
today = time.strftime(time_fmt, time.localtime())

pytest_plugins = ("sphinx.testing.fixtures",)
# from sphinx.testing.fixtures import make_app as mk_app


@pytest.fixture
def sphinx_make_app(
    tmp_path: pathlib.Path,
    make_app: Callable[[dict, pytest.MonkeyPatch], Generator[Callable, None, None]],
):
    conf = f"""
today = "{today}"
author = "Brendan Doherty"
extensions = ["sphinx_social_cards"]
html_logo = "images/message.png"
social_cards = {{
    "site_url": "https://github.com/2bndy5/sphinx-social-cards",
    "description": "Generate social media preview cards for your sphinx documentation.",
    "image_paths": ["images"],
}}
"""

    def make(files: Dict[str, str], extra_conf: str = "", **kwargs):
        (tmp_path / "conf.py").write_text(conf + extra_conf, encoding="utf-8")
        shutil.copytree(
            str(pathlib.Path(__file__).parent.parent / "docs" / "images"),
            tmp_path / "images",
        )
        for filename, content in files.items():
            (tmp_path / filename).write_text(content, encoding="utf-8")
        app = make_app(
            srcdir=SphinxPath(str(tmp_path)), **kwargs  # type: ignore[call-arg]
        )
        return app

    yield make