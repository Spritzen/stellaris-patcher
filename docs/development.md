# Development

**Everything runs through `make`.** Run `make check` before calling a change
done.

| Command | Does |
|---|---|
| `make check` | Everything below except `bench` and `format` |
| `make lint` | ruff (lint and format check), then mypy |
| `make format` | Fixes formatting and the lint issues ruff can fix itself |
| `make test` | Runs the tests |
| `make bench` | Runs only the timing benchmarks |
| `make docs` | Checks that every link in the docs points at a real file and heading |

To build a patch mod, see [patches/cold-steel-mix.md](patches/cold-steel-mix.md). After
a game or mod update, see [update-check.md](update-check.md).

## Setup

Open the folder in the dev container ([.devcontainer/](../.devcontainer/)). It
installs every package from pacman ([decision 2](decisions.md)). There is no
venv and nothing to `pip install`.

The code isn't installed as a package. `make` sets `PYTHONPATH=src`, and
pytest does the same through `pyproject.toml`. To run Python by hand:

```sh
PYTHONPATH=src python3 -c 'from stellaris_patcher.paradox.game import DEFAULT_STEAM_DIRS, find_game; print(find_game(DEFAULT_STEAM_DIRS).version)'
```

## Code layout

```
src/stellaris_patcher/
├── __main__.py      the command line: python3 -m stellaris_patcher
├── coldsteel/       Cold Steel's own files: its playsets and conflict choices
│   ├── files.py     where they are; loading; guarded saving (closed, known fields, backed up)
│   └── records.py   the records in its data files
├── core/            plain Python built on paradox/
│   ├── definitions.py  one file → the objects it defines, using its folder's rule
│   ├── merge_rules.py  reads merge_rules.json: who wins, per game folder
│   └── version.py   is a mod outdated?
├── data/
│   ├── merge_rules.json  who wins a clash, one row per game folder
│   └── patch-icon.svg, thumbnail.png  our patch mods' icon
├── paradox/         reading and writing Paradox and Steam files
│   ├── backup.py    dated backups, made before every write
│   ├── descriptor.py  .mod files
│   ├── dlc.py       the installed DLC, and the launcher's names for them
│   ├── dlc_load.py  dlc_load.json: what the game loads
│   ├── error_log.py logs/error.log: its entries, and the file each one names
│   ├── game.py      finding Stellaris through Steam's libraries
│   ├── launcher_db.py  launcher-v2.sqlite: read, and write one playset
│   ├── localisation.py  .yml localisation keys, and the game's language
│   ├── processes.py is the launcher, the game or Steam running?
│   ├── script.py    the Paradox script parser, and the fast scanner
│   ├── vdf.py       Steam's .vdf files
│   └── workshop.py  when Steam last updated each Workshop mod
├── patchmod/        making a patch mod
│   ├── cold_steel_mix.py  the Cold Steel Mix patch's fixes
│   ├── layers.py    a playset as the game sees it: which file wins, what's defined
│   └── write.py     checking, writing and linking a patch mod; adding it to a playset
├── store/
│   ├── files.py     atomic msgspec save and load
│   └── paths.py     where our data lives (XDG folders)
└── update/          the check after a game or mod update
    ├── check.py     what changed, and what it may break; check.md and diffs
    ├── notes.py     Stellaris's announcements from Steam's news API, and our archive of them
    ├── older.py     mod copies older than the game files they replace; names the notes removed
    └── snapshot.py  baselines: the game's and mods' text files at the last check
tests/               pytest; fixtures/ is a small fake install
tools/               check_links.py
```

The code started as a copy of Cold Steel's parsers, and is now ours
([decision 7](decisions.md)). It doesn't import or follow Cold Steel's code.

## Container and host

The container sees Cold Steel's files but not its process, so a write there
needs the user to say Cold Steel is closed
([decision 12](decisions.md)). On the host, the check is automatic.

New mounts in [devcontainer.json](../.devcontainer/devcontainer.json) take
effect only after **Rebuild Container**. `initializeCommand` makes the mounted
folders on the host first, since a missing one stops the container starting.

## Tests

- `tests/fixtures/` holds a small fake install: two Steam libraries, three
  Workshop mods (one zipped), a local mod and a launcher database.
  `conftest.py` copies it to a temporary folder for each test, and builds the
  binary parts there. The `sample_install` fixture gives its paths.
- `snapshot()` in `conftest.py` records every file under a folder. Use it to
  prove a test changed nothing it shouldn't.
- `test_records_read_cold_steels_real_files` reads Cold Steel's real data
  files with our records, and fails when they hold something new
  ([decision 13](decisions.md)). It's skipped when there's no Cold Steel data.
- Tests marked `real_install` read the real install and must never write to it.
- Timing tests use pytest-benchmark's `benchmark` fixture. `make test` skips
  them, and `make bench` runs only them.

## Type checking

mypy runs in strict mode on `src/`, `tests/` and `tools/`
([decision 3](decisions.md)). `tests/` is on mypy's path, so tests can import
helpers from `conftest.py`.
