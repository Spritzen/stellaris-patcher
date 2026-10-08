# Stellaris Patcher

Builds **patch mods for Stellaris playsets**: a small mod that loads last and
fixes the clashes and breakages between the mods in a playset.

Kept in a **public GitHub repo**, under the MIT licence
([decision 4](docs/decisions.md)).

The user's playsets live in **Cold Steel**, a separate Stellaris mod manager.
We share its data files only, never its code
([decision 27](docs/decisions.md), [cold-steel-data.md](docs/reference/cold-steel-data.md)).

## Start here

| I want to… | Go to |
|---|---|
| check whether something is already decided | [docs/decisions.md](docs/decisions.md) |
| read or write Cold Steel's playsets and choices | [docs/reference/cold-steel-data.md](docs/reference/cold-steel-data.md) |
| check the playset after Stellaris or a mod updates | [docs/update-check.md](docs/update-check.md) |
| report on a game run's error log | [docs/game-report.md](docs/game-report.md) |
| know how a patch mod has to be built to win | [docs/reference/patch-rules.md](docs/reference/patch-rules.md) |
| run, test or lint the code | [docs/development.md](docs/development.md) |
| commit, open and merge a PR | [docs/development.md](docs/development.md#commit-and-merge) |
| build or change the Cold Steel Mix patch | [docs/patches/cold-steel-mix.md](docs/patches/cold-steel-mix.md) |
| find where Stellaris keeps its files | [docs/reference/stellaris-files.md](docs/reference/stellaris-files.md) |
| read past error-log investigations | [docs/reports/](docs/README.md#reports) |
| see everything else | [docs/README.md](docs/README.md) |

Each repeated task also has a skill in [.claude/skills/](.claude/skills/):
`update-check`, `game-report`, `build-patch`, `add-fix` and `commit`. A
skill only points at its doc and repeats the rules that are easy to miss.
The steps stay in the doc ([decision 28](docs/decisions.md)).

## Rules that always apply

1. **Playsets come from Cold Steel, and results go back to it**
   ([decision 11](docs/decisions.md)). Write its files only through
   `coldsteel/files.py`, which backs up first and refuses while Cold Steel is
   open. In the container, ask the user to close Cold Steel before writing.
2. **Back up before writing any Paradox file**, and never write while the
   launcher or the game is open.
3. **Steam and the game are read-only.** They're mounted that way in the
   container.
4. **Decisions go in [docs/decisions.md](docs/decisions.md)** as one row: the
   result first, then a one-line reason.
5. **Write docs plainly.** Short sentences, results before reasoning. See
   [docs/README.md](docs/README.md#how-we-write-docs).
6. **`make check` passes before a change is done.**

## Environment

Arch Linux dev container ([.devcontainer/](.devcontainer/)). Host paths are
mounted at the same paths inside, so `$STEAM_DIR` and `$PARADOX_DATA_DIR` are
real on both sides. Cold Steel's data (`~/.local/share/cold-steel`, read-write),
its settings (read-only) and our own `~/.local/share/stellaris-patcher` are
mounted too. All packages come from pacman: there is no venv and no pip.
