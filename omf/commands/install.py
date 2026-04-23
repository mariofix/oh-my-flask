from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import click
from rich.console import Console

from omf import paths, recipes

console = Console()


@click.command(help="Install a recipe: clone its repo and run post-install steps.")
@click.argument("name")
@click.option("--force", is_flag=True, help="Remove any existing install first.")
@click.option("--ref", default=None, help="Override git ref (branch/tag/sha).")
def install(name: str, force: bool, ref: str | None) -> None:
    recipe = recipes.find(name)
    if recipe is None:
        raise click.ClickException(f"No recipe named '{name}'. Try `omf recipes`.")

    if not recipe.git:
        raise click.ClickException(
            f"Recipe '{name}' has no `git:` url; nothing to install."
        )

    target = paths.installed_dir() / name
    if target.exists():
        if not force:
            raise click.ClickException(
                f"{target} already exists. Use --force to reinstall."
            )
        shutil.rmtree(target)

    console.print(f"[bold]Cloning[/bold] {recipe.git} -> {target}")
    cmd = ["git", "clone", recipe.git, str(target)]
    subprocess.run(cmd, check=True)

    checkout = ref or recipe.ref
    if checkout:
        subprocess.run(["git", "checkout", checkout], cwd=str(target), check=True)

    for step in recipe.post_install:
        console.print(f"[dim]$ {step}[/dim]")
        recipes.run_shell(step, cwd=target, env=recipe.env)

    console.print(f"[green]Installed[/green] {name} at {target}")
