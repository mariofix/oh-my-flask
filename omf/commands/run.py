from __future__ import annotations

import click
from rich.console import Console

from omf import paths, recipes

console = Console()


@click.command(
    help="Run the command declared by a recipe.",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
@click.argument("name")
@click.argument("args", nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def run(ctx: click.Context, name: str, args: tuple[str, ...]) -> None:
    recipe = recipes.find(name)
    if recipe is None:
        raise click.ClickException(f"No recipe named '{name}'. Try `omf recipes`.")
    if not recipe.run:
        raise click.ClickException(f"Recipe '{name}' has no `run:` command.")

    install_dir = paths.installed_dir() / name
    cwd = install_dir if install_dir.exists() else paths.home()

    cmd = recipe.run
    if args:
        cmd = f"{cmd} {' '.join(args)}"

    console.print(f"[dim]$ {cmd}[/dim] [grey50](cwd={cwd})[/grey50]")
    recipes.run_shell(cmd, cwd=cwd, env=recipe.env)
