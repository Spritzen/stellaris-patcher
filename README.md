# Stellaris Patcher

Builds **patch mods for Stellaris playsets**: a small mod that loads last and
fixes the clashes and breakages between the mods in a playset. Its one patch
today is the [Cold Steel Mix patch](docs/patches/cold-steel-mix.md), for a
26-mod playset on Stellaris 4.5.2. Playsets come from
[Cold Steel](https://github.com/Spritzen/cold-steel), a separate Stellaris
mod manager.

This README is a tutorial. It explains how the tool works, sets it up, walks
through a first build, and then shows how to point it at your own playset and
write your own fixes. The detail lives in [docs/](docs/README.md), and each
section links to it.

- [How it works](#how-it-works)
- [What you need](#what-you-need)
- [Set it up](#set-it-up)
- [Your first build](#your-first-build)
- [The two loops: after a game, after an update](#the-two-loops-after-a-game-after-an-update)
- [Adapt it to your own playset](#adapt-it-to-your-own-playset)
- [Write a fix](#write-a-fix)
- [Upload it to the Workshop](#upload-it-to-the-workshop)
- [Work with Claude Code](#work-with-claude-code)
- [Safety rules](#safety-rules)
- [Limits](#limits)
- [Where to read more](#where-to-read-more)

## How it works

**A patch mod is a list of small fixes, each worked out from the files on
disk every time you build.** Nothing is saved between builds. When a game or
mod update removes a fix's cause, the build leaves that fix out and prints
why ([decision 14](docs/decisions.md)). This matters because saved copies of
game files go stale. Two mods in this playset broke it exactly that way.

The build works in four steps:

1. **Read the playset.** The game's own files come first, then each enabled
   mod in load order. Each one is a *layer*
   ([layers.py](src/stellaris_patcher/patchmod/layers.py)).
2. **Run each fix.** A fix is a Python function. It looks at the layers,
   checks its problem is still there, and returns the files to ship. If the
   problem is gone, it raises `FixError` with the reason.
3. **Check every file.** Each must parse, and a localisation file must name
   its language. One typo would break the file in game, so nothing is written
   if any file fails.
4. **Write the mod and link it.** The mod goes in our own data folder. The
   game's `mod/` folder gets a link and a `.mod` file. A rebuild is then live
   with no copying.

**Who wins a clash depends on the game folder.** In most folders the last
definition wins, sorted by file name. In 14 folders, such as `events/` and
`common/traits/`, the first one wins. `on_actions` merge. The rules are in
[merge_rules.json](src/stellaris_patcher/data/merge_rules.json), one row per
folder, and were checked in game. A patch file wins by its name: `zz_…` to
sort last, `!!_…` to sort first, or `localisation/<language>/replace/` for
text. See [patch-rules.md](docs/reference/patch-rules.md).

**The work goes round in a loop:**

```
         ┌───────────── play ◄──────────────┐
         ▼                                  │
  error log ─► game report ─► you agree ─► add fix ─► build ─► rebuild in Cold Steel
         ▲                       to a fix
         │
  game or mod update ─► update check ─► update report
```

A report proposes fixes. None is added until you agree
([decision 25](docs/decisions.md)).

## What you need

| What | Why |
|---|---|
| **Linux, with Stellaris from Steam** | The tool finds the game through Steam's library list, in `~/.local/share/Steam` or `~/.steam/steam`. It tells whether the game is running from `/proc` |
| **Python 3.14, msgspec and xxhash** | The code. msgspec reads and writes the JSON, xxhash hashes files |
| **pytest, ruff and mypy** | Only for `make check` |
| **[Cold Steel](https://github.com/Spritzen/cold-steel)** | The mod manager that holds the playsets. You can do without it: see [Without Cold Steel](#without-cold-steel) |
| Optional: Docker or Podman, and VS Code | For the dev container |
| Optional: Claude Code, and the GitHub CLI | For the [skills](#work-with-claude-code) and the PR flow |

## Set it up

### In the dev container

This is how the project is developed
([.devcontainer/](.devcontainer/), [decision 5](docs/decisions.md)).

1. **Run Stellaris and Cold Steel once on the host**, so their folders exist.
2. **Open the folder in VS Code** and (F1) choose **Rebuild and Reopen in Container**. The
   container is Arch Linux. Every package comes from pacman, so there's no
   venv and nothing to `pip install` ([decision 2](docs/decisions.md)).
   You only need to rebuild once and then you can just select **Reopen in Container**.
4. **Read the post-create output.** It installs Claude Code, takes one-time
   backups of the launcher's database and Cold Steel's playsets, and checks
   each mount. A red ✗ names what's missing.

The container mounts each host folder **at the same path**, so the paths
written into `.mod` files work for the game on the host:

| Host folder | In the container | Holds |
|---|---|---|
| `~/.local/share/Steam` | read-only | The game and every Workshop mod |
| `~/.local/share/Paradox Interactive` | read-write | `mod/`, `dlc_load.json`, the launcher's database, `logs/` |
| `~/.local/share/cold-steel` | read-write | Cold Steel's playsets, conflict choices and builds |
| `~/.config/cold-steel` | read-only | Cold Steel's settings |
| `~/.local/share/stellaris-patcher` | read-write | Our built mods, backups, baselines and patch notes |

**The container can't see host processes.** Before anything writes, close the
game, the launcher and Cold Steel yourself. Commands that write to Cold
Steel's files then need `--cold-steel-closed` ([decision 12](docs/decisions.md)).
A change to the mounts takes effect only after **Rebuild Container**.

### On the host

On Arch:

```sh
sudo pacman -S python python-msgspec python-xxhash python-pytest ruff mypy librsvg
```

On another distribution, install the same packages its own way. The code
isn't installed as a package: `make` sets `PYTHONPATH=src`. On the host, the
tool checks for the game, the launcher and Cold Steel itself.

### Check it works

```sh
make check    # lint, types, tests and doc links: all must pass
PYTHONPATH=src python3 -c 'from stellaris_patcher.paradox.game import DEFAULT_STEAM_DIRS, find_game; print(find_game(DEFAULT_STEAM_DIRS).version)'
```

The second line prints the game's version, such as `v4.5.2`. If it can't find
the game, see [stellaris-files.md](docs/reference/stellaris-files.md) for
where it looks. More on `make` in [development.md](docs/development.md).

## Your first build

**1. See what it would write.** This reads only, and is safe while the game
is open:

```sh
PYTHONPATH=src python3 -m stellaris_patcher cold-steel-mix
```

Each fix prints `ok` with what it did, or `left out` with the reason:

```
4. The system view uses System Scale's own 8 zoom steps, in place of Cinematic Camera's 13: …: ok
     Zoom steps: workshop:703156866's 13 → System Scale's 8
     ENTER_SYSTEM_ZOOM_STEP: System Scale's 7
6. A More Events Mod anomaly recognises Planetary Diversity's ocean worlds again: ok
     is_pd_planet_for_aqua_trait calls pd_is_planet_for_aqua_trait
2. The Starlit Starbase design gets 12 of its 13 guns in Starbase Extended's citadel: left out
     The playset has none of its mods now: workshop:3250900527.

13 files. Nothing written: pass --write.
```

Read every `left out` line. It usually means an update fixed the problem, or
that the mod is switched off.

**2. Write it.** Close the game and the Paradox launcher first.

```sh
PYTHONPATH=src python3 -m stellaris_patcher cold-steel-mix --write
```

This writes:

- the mod, in `~/.local/share/stellaris-patcher/mods/cold_steel_mix_patch/`;
- a link to it, `mod/stellaris_patcher_cold_steel_mix`, with a `.mod` file;
- its `descriptor.mod`, dated, naming the mods it patches as `dependencies`;
- its Workshop description, beside it as `cold_steel_mix_patch.workshop.txt`.

**3. Put it in the playset.** Close Cold Steel first.

```sh
PYTHONPATH=src python3 -m stellaris_patcher cold-steel-mix --write --add-to-playset --cold-steel-closed
```

It goes last, but before Cold Steel's own patch mod, which must stay last
([decision 15](docs/decisions.md)). Cold Steel's `playsets.json` is backed up
first. Run this once. Later rebuilds keep the patch where it is.

**4. Rebuild the playset in Cold Steel, then play.** You play Cold Steel's
built copy of the playset, so it only has the patch once it's rebuilt.

The full steps are in [cold-steel-mix.md](docs/patches/cold-steel-mix.md#build-it).

## The two loops: after a game, after an update

### After a game: the game report

**Play, then read the error log and trace each entry to its mod.** The log is
`logs/error.log` in the game's data folder. Our reader is
[error_log.py](src/stellaris_patcher/paradox/error_log.py):

```sh
PYTHONPATH=src python3 -c 'import os; from pathlib import Path; from stellaris_patcher.paradox.error_log import read_error_log; print(len(read_error_log(Path(os.environ["PARADOX_DATA_DIR"], "Stellaris"))))'
```

Split the entries by time: loading, game start, play. Play entries matter
most. To trace an entry, look up the file it names in Cold Steel's build
record, which says which mod each file came from. Then write a report in
`docs/reports/` and propose fixes. Visual problems often log nothing, so note
what looked wrong as you play.

Steps: [game-report.md](docs/game-report.md). Good model report:
[the new-galaxy run](docs/reports/2026-10-05-cold-steel-mix-new-galaxy.md).

### After an update: the update check

**When Stellaris or a mod updates, compare everything with the last accepted
check.** It reads only, and needs no game run.

```sh
PYTHONPATH=src python3 -m stellaris_patcher check-update --notes    # what changed
PYTHONPATH=src python3 -m stellaris_patcher check-update --accept   # once you've reviewed it
```

`--notes` also fetches Steam's patch notes and keeps them. The check writes a
folder under `~/.cache/stellaris-patcher/checks/`. Start with its `check.md`.
It shows:

- which mods and fixes the update affects;
- mod copies of game files the update changed, with diffs;
- names the update removed that mods still use;
- **older mod copies**: a mod's copy that wins over a newer game file. These
  quietly undo game fixes and log nothing. On 4.5.2, 24 of 26 mods hadn't
  updated.

`--accept` saves the game and the mods as the next baseline, about 25 MB.
Steam keeps no copy of the old game, so this is the only one. Run the first
`--accept` now, before the next update. Without a baseline, the check can
only guess what changed from file times.

Steps: [update-check.md](docs/update-check.md).

## Adapt it to your own playset

The code is general: finding the game, reading mods, layers, merge rules,
writing and linking a mod, the update check. Three things are specific to
Cold Steel Mix: the playset's name, its fixes, and the history in
`docs/reports/`.

### 1. Take a copy

Fork or copy the repo. Keep `docs/reports/` as worked examples, or delete
them along with their rows in [docs/README.md](docs/README.md#reports).
`make check` checks every doc link, so remove links to anything you delete.

### 2. Point it at your playset

#### With Cold Steel

Make the playset in Cold Steel. Then set `PLAYSET` in your patch module (step
3) to its name. The tool reads `~/.local/share/cold-steel/playsets.json` and
refuses unless exactly one playset has that name.

#### Without Cold Steel

The build needs only a `Playset`: an ordered list of mod keys,
`workshop:<id>` or `local:<.mod file name>`. You can make one from the
Paradox launcher's `dlc_load.json`, which lists the mods the game loads, in
order:

```python
from pathlib import PurePosixPath

from stellaris_patcher.coldsteel.records import Playset, PlaysetEntry
from stellaris_patcher.paradox.dlc_load import read_dlc_load
from stellaris_patcher.paradox.game import DEFAULT_STEAM_DIRS, find_game
from stellaris_patcher.patchmod.layers import Layers


def key(mod: str) -> str:
    """mod/ugc_123.mod -> workshop:123, and mod/my_mod.mod -> local:my_mod."""
    stem = PurePosixPath(mod).stem
    return f"workshop:{stem[4:]}" if stem.startswith("ugc_") else f"local:{stem}"


game = find_game(DEFAULT_STEAM_DIRS)
load = read_dlc_load(game.data_dir)  # None if the game was never started from the launcher
playset = Playset("mine", "My Mix", tuple(PlaysetEntry(key(m)) for m in load.enabled_mods))
layers = Layers.for_playset(playset, game, skip=["local:stellaris_patcher_my_mix"])
```

`skip` leaves out the patch itself, or the build reads its own files as
another mod's. Use it in place of `_playset()` in
[\_\_main\_\_.py](src/stellaris_patcher/__main__.py). Leave out
`--add-to-playset`, which writes Cold Steel's files. Add the patch to the
playset in the launcher by hand, last. Don't write the launcher's database:
the launcher holds playsets in memory and saves over it.

### 3. Make your own patch module

[cold_steel_mix.py](src/stellaris_patcher/patchmod/cold_steel_mix.py) is
the only patch. Copy it to `patchmod/<your_mix>.py`, keep the shared parts,
and empty the rest:

| Keep | Change |
|---|---|
| `FixError`, `Outcome`, `Made`, `plan()`, `patched_mods()`, `workshop_key()`, `own_keys()` | `NAME`: the mod's name in the launcher |
| `workshop_description()`, after editing its wording | `FOLDER`: its folder in `~/.local/share/stellaris-patcher/mods/` |
| | `LINK` and `KEY`: its link in `mod/` and its playset key |
| | `PLAYSET`: your playset's name |
| | `TAIL`: the end of every file name it ships, so its files are easy to spot |
| | The mod constants (`SYSTEM_SCALE = "workshop:1887282318"` …): your mods |
| | `FIXES`, `LEFT_TO_AUTHORS`, `SWITCHED_OFF`: empty to start |

Then point [\_\_main\_\_.py](src/stellaris_patcher/__main__.py) at it. It
names `cold_steel_mix` in `_playset()`, `_check_update()` and
`_cold_steel_mix()`. Rename the `cold-steel-mix` command to match.

Copy [patch-icon.svg](src/stellaris_patcher/data/patch-icon.svg) for your own
thumbnail, and render it to a 512×512 `thumbnail.png`:

```sh
rsvg-convert -w 512 -h 512 src/stellaris_patcher/data/patch-icon.svg -o src/stellaris_patcher/data/thumbnail.png
```

### 4. Find your playset's problems

**Play a short game, then read the error log** as in
[The two loops](#after-a-game-the-game-report). The first run on a new
playset is usually thousands of entries. Most of them don't matter. Lessons
from this playset's reports
([patch-rules.md](docs/reference/patch-rules.md#lessons-from-the-reports)):

- **Old copies of game files do the most damage.** A mod made for an older
  version that ships whole game files takes out everything newer versions
  added to them. One such mod caused half of an 11,463-entry log. Patching
  can't fix that. Drop the mod.
- **A version number proves nothing.** Compare what a mod's copy defines with
  what the game's copy defines.
- **A parse break loses the rest of the file**, and the errors show up in
  other files that used what was lost.
- **Filter out the harmless entries before counting.** In one run, a single
  mod's notices were 85% of the log.

Then sort what's left. Is a fix small and safe? Or would it copy a large part
of a mod whose author will likely fix it soon? Leave those to the author, and
list them on the Workshop page ([decision 33](docs/decisions.md)).

## Write a fix

### What a fix is

**A fix is a function that takes the layers and returns `(files, notes)`.**
`files` maps each path in the mod to its bytes. `notes` are lines the build
prints. If its problem is gone, it raises `FixError` with the reason. Here is
fix 6, the simplest, in full. More Events Mod calls a trigger by the name
Planetary Diversity used to give it:

```python
OLD_TRIGGER, NEW_TRIGGER = "is_pd_planet_for_aqua_trait", "pd_is_planet_for_aqua_trait"


def fix_pd_trigger(layers: Layers) -> Made:
    defined = layers.defined("common/scripted_triggers")
    if OLD_TRIGGER in defined:
        raise FixError(f"{OLD_TRIGGER} is defined now.")
    if NEW_TRIGGER not in defined:
        raise FixError(f"{NEW_TRIGGER} isn't defined any more.")
    text = (
        f"# More Events Mod still uses Planetary Diversity's old name.\n"
        f"{OLD_TRIGGER} = {{\n\t{NEW_TRIGGER} = yes\n}}\n"
    )
    notes = [f"{OLD_TRIGGER} calls {NEW_TRIGGER}"]
    return {f"common/scripted_triggers/{TAIL}.txt": text.encode()}, notes
```

It checks both ends of the problem: the old name is still missing, and the
new one still exists. Then it adds the old name. Nothing else defines that
name, so the file's name doesn't matter here.

Register it in `FIXES` with a number, the line players see on the Workshop
page, the function, and the mods it patches:

```python
FIXES = (
    (
        6,
        "A More Events Mod anomaly recognises Planetary Diversity's ocean worlds again",
        fix_pd_trigger,
        (PLANETARY_DIVERSITY, MORE_EVENTS),
    ),
)
```

When none of a fix's mods is switched on, the build leaves it out without
running it.

### What `Layers` gives you

| Call | Returns |
|---|---|
| `layers.read(key, path)` | A file's bytes, from one layer |
| `layers.has(key, path)` | Whether that layer has the file |
| `layers.winner(path)` | The layer whose copy of the file the game uses |
| `layers.files(folder, suffix)` | Every file the game reads under a folder, and the layer each comes from |
| `layers.ordered(folder)` | The same, sorted by file name as the game sorts them |
| `layers.defined(folder)` | Each top-level key in a folder, and the file that defines it first |
| `layers.localisation("l_english")` | Every text key the game has, in one language |
| `layers.define("NCamera", "ZOOM_STEPS_SYSTEM_PERCENTAGES")` | A define's winning value, and its layer |
| `layers.name(key)` | A mod's name, from its `descriptor.mod` |

For the contents of a file, use [script.py](src/stellaris_patcher/paradox/script.py).
`scan()` is a fast scanner that finds each top-level block and where it
starts and ends. Use it to copy or edit one block and leave the rest of the
file byte for byte. `parse()` gives a full tree, which is easier to read but
slower. [localisation.py](src/stellaris_patcher/paradox/localisation.py)
reads `.yml` text files.

### Rules for a fix

- **Check the cause first.** Raise `FixError` if it's gone. The reason is
  printed at every build, and the update check shows it.
- **Make your file win.** Look up the folder in
  [merge_rules.json](src/stellaris_patcher/data/merge_rules.json). If the
  first definition wins, start the file name with `!!_`. If the last wins,
  use `zz_`. `winning_name()` in
  [write.py](src/stellaris_patcher/patchmod/write.py) picks a name that sorts
  past every rival. Text goes in `localisation/<language>/replace/`.
- **Copy as little as you can.** Copy one event, trait or system, not the
  mod's whole file. Then the rest of the mod's next update still reaches the
  game ([decision 23](docs/decisions.md)).
- **Only replace a whole file while it still comes from the mod you expect.**
  Check `layers.winner(path)` first, or you could undo another mod's newer
  copy.
- **Don't guess numbers.** Take them from the game's or the mod's own files,
  so the fix follows the mod's choices.
- **Write any choice the fix makes into [decisions.md](docs/decisions.md)**,
  as one row.

### Test it

Give each fix two tests in [test_patchmod.py](tests/test_patchmod.py): one
that it fixes the problem, and one that it's left out once the cause is
gone. `_layers()` there builds a small fake game and mods in a temporary
folder. Fix 6's:

```python
PD_TRIGGERS = "common/scripted_triggers/pd.txt"
PD_TRIGGER = "pd_is_planet_for_aqua_trait = { always = yes }\n"


def test_fix_6_calls_the_new_trigger_by_its_old_name(game: Game) -> None:
    layers = _layers(game, {cold_steel_mix.PLANETARY_DIVERSITY: {PD_TRIGGERS: PD_TRIGGER}})
    files, _ = cold_steel_mix.fix_pd_trigger(layers)
    (data,) = files.values()
    assert b"is_pd_planet_for_aqua_trait = {\n\tpd_is_planet_for_aqua_trait = yes\n}" in data
    assert check_files(files) == []


def test_fix_6_is_left_out_once_the_old_name_is_defined(game: Game) -> None:
    both = PD_TRIGGER + "is_pd_planet_for_aqua_trait = { always = yes }\n"
    layers = _layers(game, {cold_steel_mix.PLANETARY_DIVERSITY: {PD_TRIGGERS: both}})
    with pytest.raises(FixError, match="is defined now"):
        cold_steel_mix.fix_pd_trigger(layers)
```

`check_files()` parses each file the way the build does. Run `make check`.

### Build and check it in game

Build as in [Your first build](#your-first-build), rebuild the playset, and
play. Then check that the log entries the fix aimed at are gone. When the
fix copies an event or system, the log has a notice that one with that id
already exists, naming the mod's file. That notice is the proof the patch's
copy won.

The full checklist for adding a fix is in
[cold-steel-mix.md](docs/patches/cold-steel-mix.md#add-a-fix).

## Upload it to the Workshop

This is optional. Each build keeps the mod ready
([decisions 20 and 21](docs/decisions.md)):

1. **Ask the other authors first.** A fix that copies a mod's file ships their
   work. The game's own files are fine to ship. Keep a table of whose work is
   in the mod, like
   [this one](docs/patches/cold-steel-mix.md#uploading-it-to-the-workshop).
2. **Upload it from the Paradox launcher.** The launcher saves the Workshop id
   in the `.mod` file. Later builds keep it, so the next upload updates the
   same item, and the build skips the Workshop copy as well as the local one.
3. **Paste the description** from `mods/<folder>.workshop.txt`. It lists the
   fixes that were written, the mods needed, the problems left to their
   authors, and the mods switched off for now.
4. **Add the needed mods as Required items** on the Workshop page. Steam
   doesn't read `dependencies`.

## Work with Claude Code

The project is built to be run with Claude Code. **Start a session with one
of these skills.** Each knows its steps and rules. Type it as a slash
command, or describe the task and Claude picks the skill.

| Command | When |
|---|---|
| `/update-check` | Stellaris or a playset mod has updated. Checks what changed, writes a report and proposes fixes |
| `/game-report` | You've played the playset. Reads the error log, traces each entry to its mod and writes a report. Say how long you played and anything that looked wrong |
| `/add-fix` | You've agreed to a fix from a report. Adds it to the patch, with tests and docs |
| `/build-patch` | Builds the patch mod and links it into the game. Then rebuild the playset in Cold Steel |
| `/commit` | Commits on a branch, opens and merges a PR, goes back to `main`, and deletes the merged branches, locally and on GitHub |

Claude asks you to close the game, the launcher and Cold Steel before
anything is written.

**To adapt them:** the skills in [.claude/skills/](.claude/skills/) are short.
Each points at its doc, which holds the steps
([decision 28](docs/decisions.md)). They name Cold Steel Mix, so rename the
playset in each skill and in its doc. [CLAUDE.md](CLAUDE.md) is what Claude
reads first in every session: keep its rules, and change the table to your
docs.

## Safety rules

These hold in every command, and are worth keeping in your copy:

- **Back up before writing any Paradox or Cold Steel file.** Cold Steel's
  files are backed up into `~/.local/share/stellaris-patcher/backups/`, the
  newest 20 of each. The container's first start also keeps one untouched
  copy of Cold Steel's playsets there, and one of the launcher's database
  beside it, as `launcher-v2.stellaris-patcher-orig.sqlite`. Neither is ever
  overwritten ([decision 6](docs/decisions.md)).
- **Never write while the game, the launcher or Cold Steel is open.** Each
  loads its files when it starts and saves over them later, undoing the
  change.
- **Steam's folders and the game are read-only.** A zipped Workshop mod is
  read in place, never unpacked into Steam's folder.
- **Only write Cold Steel files we fully understand.** If Cold Steel adds a
  field, writing is refused until
  [records.py](src/stellaris_patcher/coldsteel/records.py) has it, and a test
  fails ([decision 13](docs/decisions.md)).
- **Never change a `.mod` file that isn't ours.**

## Limits

- **Linux and Steam only.** Flatpak and Snap Steam aren't found on their
  own. Windows and macOS paths aren't handled.
- **Fixes can't patch zipped mods.** Layers read loose files only. The update
  check reads inside zips.
- **English only.** Missing text is added in English
  ([decision 19](docs/decisions.md)), and baselines keep English text.
- **Some merge rules are unchecked.** Rows in `merge_rules.json` with no
  `checked` date come from Irony Mod Manager's rules, not a game test.
- **It's a working tool, not a release.** There's no package, and the CLI
  builds one named patch.

## Where to read more

| I want to… | Read |
|---|---|
| see every settled decision and why | [decisions.md](docs/decisions.md) |
| know how a patch file wins | [patch-rules.md](docs/reference/patch-rules.md) |
| find where Stellaris, Steam and the launcher keep things | [stellaris-files.md](docs/reference/stellaris-files.md) |
| read or write Cold Steel's files | [cold-steel-data.md](docs/reference/cold-steel-data.md) |
| see what each Cold Steel Mix fix does | [cold-steel-mix.md](docs/patches/cold-steel-mix.md#what-each-fix-does) |
| run, test and lint, and see the code layout | [development.md](docs/development.md#code-layout) |
| commit, open and merge a PR | [development.md](docs/development.md#commit-and-merge) |
| read real reports | [docs/README.md](docs/README.md#reports) |
| write docs the house way | [docs/README.md](docs/README.md#how-we-write-docs) |

## Licence

MIT. See [LICENSE](LICENSE).
