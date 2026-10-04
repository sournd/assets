"""sournd brand kit for Python: token values and the paths of the files.

    from sournd_assets import tokens, mark, icon, path
    tokens()["colour"]["petrol"]["light"]   # '#3A97A3'
    mark("dark")                            # Path to marks/sournd-wordmark-dark.svg
    icon(32)                                # the small cut
    path("web/favicon.ico")
"""

import json
from functools import lru_cache
from pathlib import Path

__version__ = "0.1.0"  # brand kit version; the major version is the brand generation

_HERE = Path(__file__).resolve().parent
# Installed wheel: the files sit inside the package. Repository checkout: they sit at the root.
ROOT = _HERE if (_HERE / "tokens").is_dir() else _HERE.parents[1]


def path(relative: str = "") -> Path:
    """Absolute path of a file in the kit."""
    return ROOT / relative


@lru_cache(maxsize=1)
def tokens() -> dict:
    return json.loads(path("tokens/tokens.json").read_text(encoding="utf-8"))


def mark(theme: str = "light") -> Path:
    """The wordmark SVG for a theme: light (on paper) or dark (on night)."""
    return path(f"marks/sournd-wordmark-{theme}.svg")


def icon_cut(px: int) -> str:
    """The icon cut for a pixel size: tiny below 20px, small up to 32px, full above."""
    return "tiny" if px < 20 else "small" if px <= 32 else "full"


def icon(size_or_cut="full") -> Path:
    """The icon SVG for a cut name (full, small, tiny) or a pixel size."""
    cut = icon_cut(size_or_cut) if isinstance(size_or_cut, int) else size_or_cut
    return path(f"marks/sournd-icon-{cut}.svg")


__all__ = ["__version__", "ROOT", "path", "tokens", "mark", "icon_cut", "icon"]
