from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from omf import paths


@dataclass
class Recipe:
    name: str
    source: Path
    data: dict[str, Any]

    @property
    def kind(self) -> str:
        return self.data.get("kind", "install")

    @property
    def git(self) -> str | None:
        return self.data.get("git")

    @property
    def ref(self) -> str | None:
        return self.data.get("ref")

    @property
    def post_install(self) -> list[str]:
        steps = self.data.get("post_install") or []
        if isinstance(steps, str):
            return [steps]
        return list(steps)

    @property
    def run(self) -> str | None:
        return self.data.get("run")

    @property
    def skeleton(self) -> str | None:
        return self.data.get("skeleton")

    @property
    def env(self) -> dict[str, str]:
        return dict(self.data.get("env") or {})


def _search_dirs() -> list[Path]:
    # User recipes override bundled ones.
    return [paths.user_recipes_dir(), paths.bundled_recipes_dir()]


def find(name: str) -> Recipe | None:
    for d in _search_dirs():
        for suffix in (".yaml", ".yml"):
            candidate = d / f"{name}{suffix}"
            if candidate.exists():
                return load(candidate)
    return None


def load(path: Path) -> Recipe:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return Recipe(name=path.stem, source=path, data=data)


def list_all() -> list[Recipe]:
    seen: dict[str, Recipe] = {}
    for d in _search_dirs():
        if not d.exists():
            continue
        for path in sorted(d.glob("*.y*ml")):
            recipe = load(path)
            seen.setdefault(recipe.name, recipe)
    return list(seen.values())


def run_shell(cmd: str, cwd: Path, env: dict[str, str] | None = None) -> None:
    import os

    merged = os.environ.copy()
    if env:
        merged.update(env)
    subprocess.run(cmd, shell=True, check=True, cwd=str(cwd), env=merged)
