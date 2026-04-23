from __future__ import annotations

from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from rich.console import Console

from omf import paths, recipes

console = Console()


def _skeleton_dir(name: str) -> Path | None:
    for root in (paths.user_skeletons_dir(), paths.bundled_skeletons_dir()):
        candidate = root / name
        if candidate.exists():
            return candidate
    return None


@click.command(help="Generate a project skeleton from a template.")
@click.argument("template")
@click.option(
    "--out",
    "out_dir",
    type=click.Path(path_type=Path),
    default=None,
    help="Output directory (defaults to ./<name>).",
)
@click.option(
    "--name",
    "project_name",
    default=None,
    help="Project name used for templating (defaults to output dir name).",
)
@click.option(
    "--var",
    "extra_vars",
    multiple=True,
    metavar="KEY=VALUE",
    help="Extra template variables (repeatable).",
)
def make(
    template: str,
    out_dir: Path | None,
    project_name: str | None,
    extra_vars: tuple[str, ...],
) -> None:
    # A recipe can declare `kind: skeleton` and point at a skeleton dir;
    # otherwise we look up skeletons/<template>/ directly.
    recipe = recipes.find(template)
    skel_name = template
    if recipe and recipe.skeleton:
        skel_name = recipe.skeleton

    src = _skeleton_dir(skel_name)
    if src is None:
        raise click.ClickException(
            f"No skeleton named '{skel_name}'. Looked in user + bundled skeletons."
        )

    target = (out_dir or Path.cwd() / template).resolve()
    if target.exists() and any(target.iterdir()):
        raise click.ClickException(f"{target} exists and is non-empty.")
    target.mkdir(parents=True, exist_ok=True)

    ctx: dict[str, str] = {"name": project_name or target.name}
    for pair in extra_vars:
        if "=" not in pair:
            raise click.ClickException(f"--var expects KEY=VALUE, got {pair!r}")
        k, v = pair.split("=", 1)
        ctx[k] = v

    env = Environment(
        loader=FileSystemLoader(str(src)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
    )

    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        dest = target / rel
        if path.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        if path.suffix == ".j2":
            rendered = env.get_template(str(rel)).render(**ctx)
            dest = dest.with_suffix("")  # strip .j2
            dest.write_text(rendered, encoding="utf-8")
        else:
            dest.write_bytes(path.read_bytes())

    console.print(f"[green]Created[/green] {template} skeleton at {target}")
