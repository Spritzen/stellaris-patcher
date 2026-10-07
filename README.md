# Stellaris Patcher

Builds **patch mods for Stellaris playsets**: a small mod that loads last and
fixes the clashes and breakages between the mods in a playset. Its one patch
today is the [Cold Steel Mix patch](docs/patches/cold-steel-mix.md).

Playsets come from the Cold Steel mod manager's data files
([cold-steel-data.md](docs/reference/cold-steel-data.md)).

```sh
make check                                                # lint, types, tests, doc links
PYTHONPATH=src python3 -m stellaris_patcher cold-steel-mix  # show what the patch would write
PYTHONPATH=src python3 -m stellaris_patcher check-update --notes  # after a game or mod update
```

## Working with Claude Code

**Start a session with one of these skills. Each knows its steps and rules,
so it needs no more context.** Type it as a slash command, or just describe
the task and Claude picks the skill.

| Command | When |
|---|---|
| `/update-check` | Stellaris or a playset mod has updated. Checks what changed, writes a report and proposes fixes |
| `/game-report` | You've played the playset. Reads the error log, traces each entry to its mod and writes a report. Say how long you played and anything that looked wrong |
| `/add-fix` | You've agreed to a fix from a report. Adds it to the patch, with tests and docs |
| `/build-patch` | Builds the patch mod and links it into the game. Then rebuild Cold Steel Mix in Cold Steel |
| `/commit` | Commits the changes on a branch, opens and merges a PR, goes back to `main`, and deletes the branches merged into `main`, locally and on GitHub |

A report proposes fixes but adds none until you agree. Claude asks you to
close the game, the launcher and Cold Steel before anything is written. The
skills are in [.claude/skills/](.claude/skills/) and point at the docs that
hold the steps.

## Setup

It runs in an Arch Linux dev container ([.devcontainer/](.devcontainer/)), with
every package from pacman. Start with [docs/development.md](docs/development.md),
and see [docs/README.md](docs/README.md) for the rest.
