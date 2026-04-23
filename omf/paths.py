from __future__ import annotations

import os
from pathlib import Path


def home() -> Path:
    override = os.environ.get("OMF_HOME")
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".omf"


def installed_dir() -> Path:
    p = home() / "installed"
    p.mkdir(parents=True, exist_ok=True)
    return p


def user_recipes_dir() -> Path:
    p = home() / "recipes"
    p.mkdir(parents=True, exist_ok=True)
    return p


def user_skeletons_dir() -> Path:
    p = home() / "skeletons"
    p.mkdir(parents=True, exist_ok=True)
    return p


def bundled_recipes_dir() -> Path:
    # When installed as a wheel, recipes are packaged under omf/_bundled.
    # In a source checkout, fall back to the repo-root recipes/ directory.
    pkg_bundled = Path(__file__).parent / "_bundled" / "recipes"
    if pkg_bundled.exists():
        return pkg_bundled
    return Path(__file__).parent.parent / "recipes"


def bundled_skeletons_dir() -> Path:
    pkg_bundled = Path(__file__).parent / "_bundled" / "skeletons"
    if pkg_bundled.exists():
        return pkg_bundled
    return Path(__file__).parent.parent / "skeletons"


def bundled_integrations_dir() -> Path:
    pkg_bundled = Path(__file__).parent / "_bundled" / "integrations"
    if pkg_bundled.exists():
        return pkg_bundled
    return Path(__file__).parent.parent / "integrations"


def repo_root() -> Path | None:
    """Return the source checkout root if omf is running from one, else None."""
    candidate = Path(__file__).parent.parent
    if (candidate / ".git").exists():
        return candidate
    return None
