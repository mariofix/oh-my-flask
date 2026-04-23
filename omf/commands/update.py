from __future__ import annotations

import subprocess
import sys

import click
from rich.console import Console

from omf import PIP_TARGET, paths

console = Console()


@click.command(
    help="Update omf itself (git pull when in a checkout, pip+git URL otherwise)."
)
@click.option(
    "--pip",
    is_flag=True,
    help="Force pip-based upgrade from the git URL even inside a checkout.",
)
def self_update(pip: bool) -> None:
    root = paths.repo_root()
    if pip or root is None:
        console.print(f"[bold]pip install --upgrade {PIP_TARGET}[/bold]")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", PIP_TARGET],
            check=True,
        )
        console.print("[green]omf updated.[/green]")
        return

    console.print(f"[bold]git pull[/bold] in {root}")
    subprocess.run(["git", "pull", "--ff-only"], cwd=str(root), check=True)
    console.print("[bold]pip install -e .[/bold]")
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", str(root)],
        check=True,
    )
    console.print("[green]omf updated.[/green]")
