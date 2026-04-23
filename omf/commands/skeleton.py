from __future__ import annotations

import fnmatch
import shutil
from pathlib import Path

import click
import yaml
from rich.console import Console

from omf import paths

console = Console()

IGNORED_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".idea",
    ".vscode",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    "dist",
    "build",
}
IGNORED_DIR_GLOBS = ("*.egg-info",)
IGNORED_FILE_SUFFIXES = {".pyc", ".pyo", ".so", ".dylib"}


def _is_ignored(rel: Path) -> bool:
    for part in rel.parts[:-1]:
        if part in IGNORED_DIRS:
            return True
        if any(fnmatch.fnmatch(part, pat) for pat in IGNORED_DIR_GLOBS):
            return True
    name = rel.parts[-1]
    if name in IGNORED_DIRS:
        return True
    if Path(name).suffix in IGNORED_FILE_SUFFIXES:
        return True
    return False


def _looks_text(path: Path) -> bool:
    try:
        chunk = path.read_bytes()[:8192]
    except OSError:
        return False
    if b"\x00" in chunk:
        return False
    try:
        chunk.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True


def _build_needles(
    project_name: str, extras: tuple[str, ...]
) -> dict[str, str]:
    needles: dict[str, str] = {}
    if project_name:
        needles[project_name] = "{{ name }}"
    for pair in extras:
        if "=" not in pair:
            raise click.ClickException(f"--var expects KEY=NEEDLE, got {pair!r}")
        key, needle = pair.split("=", 1)
        if not needle:
            raise click.ClickException(f"--var {key} has empty needle")
        needles[needle] = f"{{{{ {key} }}}}"
    return needles


def _substitute(text: str, needles: dict[str, str]) -> tuple[str, bool]:
    changed = False
    # Longest needles first so e.g. "myproj_v2" wins over "myproj".
    for needle, repl in sorted(needles.items(), key=lambda kv: -len(kv[0])):
        if needle in text:
            text = text.replace(needle, repl)
            changed = True
    return text, changed


@click.group(help="Build and manage local skeletons.")
def skeleton() -> None:
    pass


@skeleton.command("create", help="Capture a directory as a Jinja skeleton.")
@click.argument("name")
@click.option(
    "--from",
    "src_dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=Path.cwd,
    help="Directory to skeletonize (default: current directory).",
)
@click.option(
    "--project-name",
    default=None,
    help="String in the source to replace with `{{ name }}`. "
    "Defaults to the source dir's basename. Pass empty to disable.",
)
@click.option(
    "--var",
    "extra_vars",
    multiple=True,
    metavar="KEY=NEEDLE",
    help="Replace NEEDLE with `{{ KEY }}` in templated files (repeatable).",
)
@click.option("--force", is_flag=True, help="Overwrite an existing skeleton dir.")
@click.option(
    "--no-recipe",
    is_flag=True,
    help="Skip writing the matching recipes/<name>.yaml stub.",
)
def create(
    name: str,
    src_dir: Path,
    project_name: str | None,
    extra_vars: tuple[str, ...],
    force: bool,
    no_recipe: bool,
) -> None:
    src = src_dir.resolve()
    if project_name is None:
        project_name = src.name

    needles = _build_needles(project_name, extra_vars)

    dest_root = paths.user_skeletons_dir() / name
    if dest_root.exists():
        if not force:
            raise click.ClickException(
                f"{dest_root} already exists. Use --force to overwrite."
            )
        shutil.rmtree(dest_root)
    dest_root.mkdir(parents=True)

    text_count = 0
    binary_count = 0
    skipped_count = 0

    for path in sorted(src.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(src)
        if _is_ignored(rel):
            skipped_count += 1
            continue

        dest = dest_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)

        if _looks_text(path):
            text = path.read_text(encoding="utf-8")
            rendered, changed = _substitute(text, needles)
            if changed:
                dest = dest.with_name(dest.name + ".j2")
                dest.write_text(rendered, encoding="utf-8")
                text_count += 1
            else:
                dest.write_text(text, encoding="utf-8")
                binary_count += 1  # counted as "as-is"
        else:
            dest.write_bytes(path.read_bytes())
            binary_count += 1

    console.print(
        f"[green]Captured[/green] {src} -> {dest_root} "
        f"({text_count} templated, {binary_count} as-is, {skipped_count} skipped)"
    )

    if not no_recipe:
        recipe_path = paths.user_recipes_dir() / f"{name}.yaml"
        if recipe_path.exists() and not force:
            console.print(
                f"[yellow]recipe exists, leaving alone:[/yellow] {recipe_path}"
            )
        else:
            recipe_path.write_text(
                yaml.safe_dump(
                    {
                        "kind": "skeleton",
                        "description": f"Captured from {src}.",
                        "skeleton": name,
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            console.print(f"[green]Wrote recipe[/green] {recipe_path}")

    console.print(f"\nRender it with:  [bold]omf make {name} --out ./somewhere[/bold]")
