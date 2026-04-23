# oh-my-flask (`omf`)

A recipe-based personal CLI for cloning/configuring tools and scaffolding
projects. Add a YAML file, get a new command.

## Install

Use [pipx](https://pipx.pypa.io/) so `omf` is globally available and isolated
from your project virtualenvs:

```bash
pipx install git+https://github.com/mariofix/oh-my-flask.git
# or, from a local checkout:
pipx install -e .
```

pipx drops the `omf` binary in `~/.local/bin`. The shell integrations below
make sure that dir is on your `PATH`.

This tool isn't published to PyPI — install (and self-update) always pull
from the git repo.

### Shell integrations (oh-my-zsh / oh-my-bash)

```bash
omf shell install                 # auto-detects zsh/bash
omf shell install --shell zsh     # or be explicit
omf shell status                  # show where the plugins would live
```

This copies the plugin to `$ZSH_CUSTOM/plugins/omf/` or
`$OSH_CUSTOM/plugins/omf/`. Then:

- **oh-my-zsh:** add `omf` to the `plugins=(...)` line in `~/.zshrc`.
- **oh-my-bash:** add `omf` to the `plugins=(...)` line in `~/.bashrc`.

Restart your shell. You get tab completion, `~/.local/bin` added to `PATH`,
and these aliases: `omfi`, `omfm`, `omfr`, `omfls`, `omfu`.

## Commands

| Command                  | What it does                                                 |
|--------------------------|--------------------------------------------------------------|
| `omf recipes`            | List every recipe omf can see.                               |
| `omf install <name>`     | Clone the recipe's repo and run its `post_install` steps.    |
| `omf make <template>`    | Render a skeleton into a new directory.                      |
| `omf run <name> [args]`  | Execute the recipe's `run:` command.                         |
| `omf self-update`        | `git pull` + `pip install -e .` on the omf checkout.         |
| `omf shell install`      | Drop the oh-my-zsh / oh-my-bash plugin into your shell.      |
| `omf shell status`       | Show where the plugins are (or would go).                    |
| `omf skeleton create`    | Capture a directory as a reusable Jinja skeleton.            |

## Layout

```
omf/                     Python package (Click CLI + subcommands)
recipes/                 Bundled recipes (YAML)
skeletons/               Bundled Jinja2 project templates
~/.omf/recipes/          User-defined recipes (override bundled ones)
~/.omf/skeletons/        User-defined skeletons
~/.omf/installed/        Where `omf install` clones things
```

User recipes beat bundled ones with the same name, so you can shadow anything
shipped in this repo without editing it.

## Recipe format

```yaml
# recipes/daleks.yaml
kind: install                  # install | skeleton
description: Short summary shown by `omf recipes`.
git: https://github.com/you/daleks.git
ref: main                      # optional branch/tag/sha

env:
  DALEKS_HOME: "${HOME}/.omf/installed/daleks"

post_install:                  # shell steps, run in the clone dir
  - python -m venv .venv
  - .venv/bin/pip install -e .

run: ".venv/bin/daleks"        # `omf run daleks -- foo bar` appends args
```

Skeleton recipes (`kind: skeleton`) only need:

```yaml
kind: skeleton
skeleton: flask                # directory under skeletons/
description: Minimal Flask app.
```

Any file ending in `.j2` inside a skeleton is rendered with Jinja2; everything
else is copied byte-for-byte. The `name` variable is always available; pass
more with `--var key=value`.

## Capturing a project as a skeleton

Turn the current directory into a reusable template:

```bash
cd ~/code/myproj
omf skeleton create myproj-template                 # uses dir name as the {{ name }} needle
omf skeleton create svc --project-name myproj       # explicit needle
omf skeleton create svc --var author="Jane Doe"     # extra substitutions
```

This walks the source tree, skips junk (`.git`, `__pycache__`, `.venv`, `node_modules`, …),
detects binary files, and writes:

- `~/.omf/skeletons/<name>/` — text files that contained substitutions become
  `*.j2`; everything else is copied byte-for-byte.
- `~/.omf/recipes/<name>.yaml` — a `kind: skeleton` stub so `omf make <name>`
  works immediately. Pass `--no-recipe` to skip.

Render it back out anywhere with `omf make <name> --out ./somewhere --name newproj`.

## Adding a new command

1. Drop `recipes/foo.yaml`.
2. `omf recipes` should list it.
3. `omf install foo` / `omf run foo` / `omf make foo` just work.

No Python changes needed for routine additions. When a recipe gets complex,
have `post_install` call a checked-in Python script instead of inlining shell.

## Self-update

```bash
omf self-update           # git pull + editable reinstall (when in a checkout)
omf self-update --pip     # pip install --upgrade git+https://github.com/...
```
