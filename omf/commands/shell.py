from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

import click
from rich.console import Console

from omf import paths

console = Console()


@dataclass(frozen=True)
class Target:
    shell: str
    framework: str
    source_rel: str  # relative to integrations/
    custom_env: str
    default_custom: Path
    dest_rel: str  # relative to $CUSTOM
    rc_file: Path
    rc_hint: str


TARGETS: dict[str, Target] = {
    "zsh": Target(
        shell="zsh",
        framework="oh-my-zsh",
        source_rel="ohmyzsh/omf/omf.plugin.zsh",
        custom_env="ZSH_CUSTOM",
        default_custom=Path.home() / ".oh-my-zsh" / "custom",
        dest_rel="plugins/omf/omf.plugin.zsh",
        rc_file=Path.home() / ".zshrc",
        rc_hint='add `omf` to your `plugins=(...)` line in ~/.zshrc',
    ),
    "bash": Target(
        shell="bash",
        framework="oh-my-bash",
        source_rel="ohmybash/omf/omf.plugin.sh",
        custom_env="OSH_CUSTOM",
        default_custom=Path.home() / ".oh-my-bash" / "custom",
        dest_rel="plugins/omf/omf.plugin.sh",
        rc_file=Path.home() / ".bashrc",
        rc_hint='add `omf` to your `plugins=(...)` line in ~/.bashrc',
    ),
}


def _custom_dir(target: Target) -> Path:
    override = os.environ.get(target.custom_env)
    if override:
        return Path(override).expanduser()
    return target.default_custom


def _detect_available() -> list[str]:
    found: list[str] = []
    for key, target in TARGETS.items():
        if _custom_dir(target).parent.exists():
            found.append(key)
    return found


@click.group(help="Manage shell integrations (oh-my-zsh, oh-my-bash).")
def shell() -> None:
    pass


@shell.command("install", help="Copy the omf plugin into your shell framework.")
@click.option(
    "--shell",
    "shell_name",
    type=click.Choice(["zsh", "bash", "auto"]),
    default="auto",
    show_default=True,
)
@click.option("--force", is_flag=True, help="Overwrite an existing plugin file.")
def install(shell_name: str, force: bool) -> None:
    if shell_name == "auto":
        chosen = _detect_available()
        if not chosen:
            raise click.ClickException(
                "Neither ~/.oh-my-zsh nor ~/.oh-my-bash was found. "
                "Pass --shell zsh|bash after installing one."
            )
    else:
        chosen = [shell_name]

    src_root = paths.bundled_integrations_dir()
    for key in chosen:
        target = TARGETS[key]
        src = src_root / target.source_rel
        if not src.exists():
            raise click.ClickException(f"Bundled plugin missing: {src}")

        dest = _custom_dir(target) / target.dest_rel
        if dest.exists() and not force:
            console.print(
                f"[yellow]skip[/yellow] {target.framework}: {dest} already exists "
                "(use --force to overwrite)"
            )
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        console.print(f"[green]installed[/green] {target.framework} plugin -> {dest}")
        console.print(f"  next: {target.rc_hint}, then restart your shell.")


@shell.command("status", help="Show where omf would install each shell plugin.")
def status() -> None:
    for key, target in TARGETS.items():
        dest = _custom_dir(target) / target.dest_rel
        exists = "[green]present[/green]" if dest.exists() else "[grey50]missing[/grey50]"
        console.print(f"{target.framework}: {dest} ({exists})")
