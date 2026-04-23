from __future__ import annotations

import click
from rich.console import Console
from rich.table import Table

from omf import recipes as recipes_mod

console = Console()


@click.command(help="List available recipes.")
def recipes() -> None:
    all_recipes = recipes_mod.list_all()
    if not all_recipes:
        console.print("[yellow]No recipes found.[/yellow]")
        return

    table = Table(title="omf recipes")
    table.add_column("name", style="bold")
    table.add_column("kind")
    table.add_column("source")
    table.add_column("summary")

    for r in all_recipes:
        summary = r.data.get("description") or ""
        table.add_row(r.name, r.kind, str(r.source), summary)

    console.print(table)
