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

It runs in an Arch Linux dev container ([.devcontainer/](.devcontainer/)), with
every package from pacman. Start with [docs/development.md](docs/development.md),
and see [docs/README.md](docs/README.md) for the rest.
