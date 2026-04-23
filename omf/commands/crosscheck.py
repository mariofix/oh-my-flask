from __future__ import annotations

import shutil
import subprocess

import click
from rich.console import Console

console = Console()

CMD_TOOLS = {
    "pipx",
    "pyenv",
    "poetry",
    "uv",
    "bat",
}


def get_version(tool: str) -> str | None:
    try:
        result = subprocess.run(
            [tool, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.stdout.strip() or result.stderr.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None


@click.group(help="Check and report common tools.")
def crosscheck() -> None:
    pass


@crosscheck.command("reportar", help="crosscheck and report.")
def reportar() -> None:
    for tool in sorted(CMD_TOOLS):
        path = shutil.which(tool)
        if path:
            version = get_version(tool) or "unknown"
            console.print(f"[green]✓ {tool}[/green] → {version}")
        else:
            console.print(f"[red]✗ {tool}[/red] → not found")