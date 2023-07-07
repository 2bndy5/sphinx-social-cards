import json
import os
from pathlib import Path
import subprocess
import shutil
from typing import List, Dict, Any
from urllib.request import Request, urlopen
from setuptools import setup, Command
from setuptools.command.build import SubCommand
from setuptools.command.build_py import build_py
from setuptools.command.sdist import sdist

pkg_root = Path(__file__).parent
pkg_src = pkg_root / "src" / "sphinx_social_cards"
icon_pkgs = {
    "material": ["@mdi/svg/svg", "@mdi/svg/LICENSE"],
    "octicons": ["@primer/octicons/build/svg", "@primer/octicons/LICENSE"],
    "simple": ["simple-icons/icons", "simple-icons/LICENSE.md"],
    "fontawesome": [
        "@fortawesome/fontawesome-free/svgs",
        "@fortawesome/fontawesome-free/LICENSE.txt",
    ],
}


def download_fonts(font_id: str, font_cache: Path):
    """Downloads all weights and styles of the specified font (.ttf files only).

    :param font_id: The Fontsource font_id is not to be confused with the font family.
    """
    header = {
        # needed to avoid response 403
        "User-Agent": (
            "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
        ),
    }
    with urlopen(
        Request(f"https://api.fontsource.org/v1/fonts/{font_id}", headers=header)
    ) as response:
        data: Dict[str, Any] = json.loads(response.read())
    assert "family" in data
    family = data["family"]
    # cache the font info
    info_cache = Path(font_cache, family).with_suffix(".json")
    info_cache.write_text(json.dumps(data, indent=2), encoding="utf-8")

    # get all weights from default subset of normal style in TTF format
    assert "weights" in data and data["weights"]
    weights: List[int] = data["weights"]
    assert "defSubset" in data
    subset = data["defSubset"]
    assert "variants" in data
    assert "styles" in data
    for weight in weights:
        assert str(weight) in data["variants"]
        for style in data["styles"]:
            assert style in data["variants"][str(weight)]
            assert subset in data["variants"][str(weight)][style]
            assert "url" in data["variants"][str(weight)][style][subset]
            assert "ttf" in data["variants"][str(weight)][style][subset]["url"]
            ttf_url: str = data["variants"][str(weight)][style][subset]["url"]["ttf"]
            with urlopen(Request(ttf_url, headers=header)) as font:
                ttf = font.read()
                # cache ttf font
                font_file_name = f"{family} {style} ({subset} {weight})"
                ttf_cache = Path(font_cache, font_file_name).with_suffix(".ttf")
                ttf_cache.write_bytes(ttf)


class SrcDistCommand(sdist):
    """Custom sdist command."""

    def run(self):
        self.run_command("bundle-data")
        super().run()


class BuildPyCommand(build_py):
    """Custom bdist_wheel command."""

    def run(self):
        self.run_command("bundle-data")
        super().run()


class BundleCommand(Command, SubCommand):
    """A custom command to generate distributed assets (optimized SVG files and Roboto
    font variants)."""

    description = "Copy and optimize SVG files from npm modules."
    user_options = [
        # The format is (long option, short option, description).
        ("dirty", None, "skip bundling icons/fonts if they already exist in pkg src"),
    ]

    def initialize_options(self):
        """Set default values for options."""
        # Each user option must be listed here with their default value.
        self.dirty = None

    def finalize_options(self):
        """Post-process options."""
        if self.dirty is None:
            # If package.json and svgo config doesn't exist, then assume this is
            # building from sdist and icons should already be bundled.
            npm_able = (
                Path(pkg_root, "package.json").exists()
                and Path(pkg_root, "tools", "svgo_config.js").exists()
            )
            is_nox_session = os.environ.get("NOX_CURRENT_SESSION", "").startswith(
                "tests-3."
            )
            is_ci_building_dirty = (
                os.environ.get("SPHINX_SOCIAL_CARDS_BUILD_DIRTY", "") == "true"
            )
            self.dirty = not npm_able or is_nox_session or is_ci_building_dirty

        if self.dirty:
            # NOTE: As of setuptools v64.0.2, we cannot raise an exception here for
            # editable installs.
            if not Path(pkg_src, ".fonts").exists():
                self.dirty = False
                return
            for icon_set in icon_pkgs:
                if not Path(pkg_src, ".icons", icon_set).exists():
                    self.dirty = False
                    return

    def run(self) -> None:
        """Run command."""

        def __run_process(*cmd: str):
            args = " ".join(cmd)
            self.announce(f"Running {args}", level=2)
            subprocess.run(args, check=True, shell=True, cwd=str(pkg_root))

        if not self.dirty:
            # ensure icons from npm pkg exist
            __run_process("npm", "install")
            # optimize/copy icons to pkg as pkg data
            for name, sources in icon_pkgs.items():
                icons_dist = pkg_src / ".icons" / name
                for src in sources:
                    icons_src = pkg_root / "node_modules" / src
                    if icons_src.is_dir():
                        if icons_dist.exists():
                            shutil.rmtree(str(icons_dist))
                        # copy icons from npm pkg
                        __run_process(
                            "npx",
                            "svgo",
                            "--config",
                            str(pkg_root / "tools" / "svgo_config.js"),
                            "-r",
                            "-q",
                            "-f",
                            str(icons_src),
                            "-o",
                            str(icons_dist),
                        )
                    elif icons_src.is_file():
                        # copy the file (eg. LICENSE)
                        icons_dist.parent.mkdir(parents=True, exist_ok=True)
                        Path(icons_dist, icons_src.name).write_bytes(
                            icons_src.read_bytes()
                        )

            # get Roboto fonts and store as pkg data
            font_cache = Path(pkg_src, ".fonts")
            font_cache.mkdir(exist_ok=True)
            for font_id in [
                "roboto",
                "roboto-condensed",
                "roboto-flex",
                "roboto-mono",
                "roboto-serif",
                "roboto-slab",
            ]:
                download_fonts(font_id, font_cache)


# all install info is located in pyproject.toml
setup(
    cmdclass={
        "bundle-data": BundleCommand,
        "build_py": BuildPyCommand,
        "sdist": SrcDistCommand,
    },
)
