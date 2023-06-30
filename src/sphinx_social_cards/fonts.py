"""A way of getting font's sources with `fontsource API <https://fontsource.org/docs/api/>`_."""
import json
from urllib.parse import quote
from pathlib import Path
from typing import Dict, Any, List

from PIL import features
from sphinx.util.logging import getLogger
from .validators import try_request
from .validators.layers import Font

_FONT_SOURCE_API = "https://api.fontsource.org/"
LOGGER = getLogger(__name__)


if not features.check_module("freetype2"):  # pragma: no cover
    raise OSError("pillow installation does not support ttf fonts on this system.")


class FontSourceManager:
    api_version = "v1/fonts"
    cache_path: Path

    @classmethod
    def get_font_file_name(cls, font: Font) -> str:
        return f"{font.family} {font.style} ({font.subset} {font.weight})"

    @classmethod
    def get_font(cls, font: Font) -> bool:
        cls.get_info(font)  # fills in unset `Font` specs
        font_file_name = cls.get_font_file_name(font)
        if Path(cls.cache_path, font_file_name).with_suffix(".ttf").exists():
            font.path = str(Path(cls.cache_path, font_file_name).with_suffix(".ttf"))
            return True
        return cls.download(font)

    @classmethod
    def get_info(cls, font: Font):
        info_cache = Path(cls.cache_path, font.family).with_suffix(".json")
        if info_cache.exists():
            font_info = json.loads(info_cache.read_text(encoding="utf-8"))
        else:
            url = f"{_FONT_SOURCE_API}{cls.api_version}?family={quote(font.family)}"
            response = try_request(url)
            if response.status_code is not None and response.status_code != 200:
                LOGGER.warning("failed to get info for font:\n%r", font)
                return {}
            info: List[Dict[str, Any]] = response.json()
            LOGGER.info("Polling font info using url: %s", url)
            if not info:
                LOGGER.info("no info for font query: %s", font.family)
                return {}
            if len(info) > 1:
                LOGGER.info(
                    "Found more than 1 font for family %s. Using the first entry:\n%s",
                    font.family,
                    json.dumps(info, indent=2),
                )
            font_info = info[0]
            info_cache.parent.mkdir(parents=True, exist_ok=True)
            info_cache.write_text(json.dumps(font_info, indent=2), encoding="utf-8")
        styles = font_info.get("styles", [])
        if font.style not in styles:
            raise ValueError(
                f"{font.family} font family has no {font.style} style; only: {styles}"
            )
        if font.subset is None:
            font.subset = font_info.get("defSubset", None)
            assert font.subset is not None
        else:
            subsets = font_info.get("subsets", None)
            assert subsets is not None
            if font.subset not in subsets:
                raise ValueError(
                    f"{font.family} font family has no {font.subset} subset; "
                    f"only {subsets}"
                )
        weights = font_info.get("weights", None)
        assert weights is not None
        if font.weight not in weights:
            # guess the closest weight value
            diffs = [abs(w - font.weight) for w in weights]
            closest = diffs[0]
            weight = weights[0]
            for index, diff in enumerate(diffs):
                if diff < closest:
                    closest = diff
                    weight = weights[index]
            font.weight = weight
        return font_info

    @classmethod
    def download(cls, font: Font) -> bool:
        info_cache = Path(cls.cache_path, font.family).with_suffix(".json")
        assert info_cache.exists()
        info: Dict[str, Any] = json.loads(info_cache.read_text(encoding="utf-8"))
        font_id = info.get("id", None)
        assert font_id is not None
        if "variants" not in info:
            response = try_request(f"{_FONT_SOURCE_API}{cls.api_version}/{font_id}")
            if response.status_code is not None and response.status_code != 200:
                return False
            info = response.json()
            info_cache.write_text(json.dumps(info, indent=2), encoding="utf-8")
        font_file_name = cls.get_font_file_name(font)
        font_path = Path(cls.cache_path, font_file_name).with_suffix(".ttf")
        LOGGER.info("Fetching font: %s", font_file_name)
        variants = info.get("variants", None)
        assert variants is not None
        variant_url = variants[str(font.weight)][font.style][font.subset].get(
            "url", None
        )
        assert variant_url is not None and "ttf" in variant_url
        response = try_request(variant_url["ttf"])
        if response.status_code is not None and response.status_code == 200:
            font_path.parent.mkdir(parents=True, exist_ok=True)
            font_path.write_bytes(response.content)
            font.path = str(font_path)
            return True
        return False