from __future__ import annotations

import click

from omf import __version__
from omf.commands import install as install_cmd
from omf.commands import make as make_cmd
from omf.commands import recipes as recipes_cmd
from omf.commands import run as run_cmd
from omf.commands import shell as shell_cmd
from omf.commands import skeleton as skeleton_cmd
from omf.commands import update as update_cmd


@click.group(help="oh-my-flask: recipe-based personal tool installer.")
@click.version_option(__version__, prog_name="omf")
def main() -> None:
    pass


main.add_command(install_cmd.install)
main.add_command(make_cmd.make)
main.add_command(run_cmd.run)
main.add_command(update_cmd.self_update, name="self-update")
main.add_command(recipes_cmd.recipes)
main.add_command(shell_cmd.shell)
main.add_command(skeleton_cmd.skeleton)


if __name__ == "__main__":
    main()
