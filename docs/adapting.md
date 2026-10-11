# Adapt it to your own playset

**The code is general. Three things are specific to Cold Steel Mix: the
playset's name, its fixes, and the reports in `docs/reports/`.** With Claude
Code, ask it to "adapt this project to my playset, <name>". This page holds
the steps it follows, and what you read to check its work.

## How a build works

**A patch mod is a list of small fixes, each worked out from the files on
disk every time you build.** Nothing is saved between builds. When a game or
mod update removes a fix's cause, the build leaves that fix out and prints
why ([decision 14](decisions.md)). Saved copies of game files go stale: two
mods in this playset broke it exactly that way.

1. **Read the playset.** The game's own files come first, then each enabled
   mod in load order. Each one is a *layer*
   ([layers.py](../src/stellaris_patcher/patchmod/layers.py)).
2. **Run each fix.** A fix is a Python function. It looks at the layers,
   checks its problem is still there, and returns the files to ship. If the
   problem is gone, it raises `FixError` with the reason.
3. **Check every file.** Each must parse, and a localisation file must name
   its language. One typo would break the file in game, so nothing is
   written if any file fails.
4. **Write the mod and link it.** The mod goes in our own data folder. The
   game's `mod/` folder gets a link and a `.mod` file. A rebuild is then
   live with no copying.

**Who wins a clash depends on the game folder.** In most folders the last
definition wins, sorted by file name. In 14 folders, such as `events/` and
`common/traits/`, the first one wins. `on_actions` merge. The rules are in
[merge_rules.json](../src/stellaris_patcher/data/merge_rules.json), one row
per folder. A patch file wins by its name: `zz_…` to sort last, `!!_…` to
sort first, or `localisation/<language>/replace/` for text. See
[patch-rules.md](reference/patch-rules.md).

## 1. Take a copy

Fork or copy the repo. Keep `docs/reports/` as worked examples, or delete
them along with their rows in [docs/README.md](README.md#reports).
`make check` checks every doc link, so remove links to anything you delete.

## 2. Point it at your playset

### With Cold Steel

Make the playset in [Cold Steel](https://github.com/Spritzen/cold-steel).
Then set `PLAYSET` in your patch module (step 3) to its name. The tool reads
`~/.local/share/cold-steel/playsets.json` and refuses unless exactly one
playset has that name.

### Without Cold Steel

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
[\_\_main\_\_.py](../src/stellaris_patcher/__main__.py). Leave out
`--add-to-playset`, which writes Cold Steel's files. Add the patch to the
playset in the launcher by hand, last. Don't write the launcher's database:
the launcher holds playsets in memory and saves over it.

## 3. Make your own patch module

[cold_steel_mix.py](../src/stellaris_patcher/patchmod/cold_steel_mix.py) is
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
| | `FIXES`, `FIX_GROUPS`, `LEFT_TO_AUTHORS`, `NEEDS`: empty to start |

Then point [\_\_main\_\_.py](../src/stellaris_patcher/__main__.py) at it. It
names `cold_steel_mix` in `_playset()`, `_check_update()` and
`_cold_steel_mix()`. Rename the `cold-steel-mix` command to match.

Copy [patch-icon.svg](../src/stellaris_patcher/data/patch-icon.svg) for your
own thumbnail, and render it to a 512×512 `thumbnail.png`:

```sh
rsvg-convert -w 512 -h 512 src/stellaris_patcher/data/patch-icon.svg -o src/stellaris_patcher/data/thumbnail.png
```

The skills in [.claude/skills/](../.claude/skills/) and their docs name Cold
Steel Mix: rename the playset in each. [CLAUDE.md](../CLAUDE.md) is what
Claude reads first in every session: keep its rules, and change its table
to your docs.

## 4. Find your playset's problems

**Play a short game, then run `/game-report`.** The first run on a new
playset is usually thousands of entries, and most don't matter. Lessons
from this playset's reports
([patch-rules.md](reference/patch-rules.md#lessons-from-the-reports)):

- **Old copies of game files do the most damage.** A mod made for an older
  version that ships whole game files takes out everything newer versions
  added to them. One such mod caused half of an 11,463-entry log. Patching
  can't fix that. Drop the mod.
- **A version number proves nothing.** Compare what a mod's copy defines
  with what the game's copy defines.
- **A parse break loses the rest of the file**, and the errors show up in
  other files that used what was lost.
- **Filter out the harmless entries before counting.** In one run, a single
  mod's notices were 85% of the log.

Then sort what's left. Is a fix small and safe? Or would it copy a large
part of a mod whose author will likely fix it soon? Leave those to the
author, and list them on the Workshop page ([decision 33](decisions.md)).

## Write a fix

`/add-fix` writes a fix once you've agreed to it. This is what it writes.

### What a fix is

**A fix is a function that takes the layers and returns `(files, notes)`.**
`files` maps each path in the mod to its bytes. `notes` are lines the build
prints. If its problem is gone, it raises `FixError` with the reason. Here
is fix 6, the simplest, in full. More Events Mod calls a trigger by the
name Planetary Diversity used to give it:

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

For the contents of a file, use
[script.py](../src/stellaris_patcher/paradox/script.py). `scan()` is a fast
scanner that finds each top-level block and where it starts and ends. Use
it to copy or edit one block and leave the rest of the file byte for byte.
`parse()` gives a full tree, which is easier to read but slower.
[localisation.py](../src/stellaris_patcher/paradox/localisation.py) reads
`.yml` text files.

### Rules for a fix

- **Check the cause first.** Raise `FixError` if it's gone. The reason is
  printed at every build, and the update check shows it.
- **Make your file win.** Look up the folder in
  [merge_rules.json](../src/stellaris_patcher/data/merge_rules.json). If the
  first definition wins, start the file name with `!!_`. If the last wins,
  use `zz_`. `winning_name()` in
  [write.py](../src/stellaris_patcher/patchmod/write.py) picks a name that
  sorts past every rival. Text goes in `localisation/<language>/replace/`.
- **Copy as little as you can.** Copy one event, trait or system, not the
  mod's whole file. Then the rest of the mod's next update still reaches
  the game ([decision 23](decisions.md)).
- **Only replace a whole file while it still comes from the mod you
  expect.** Check `layers.winner(path)` first, or you could undo another
  mod's newer copy.
- **Don't guess numbers.** Take them from the game's or the mod's own
  files, so the fix follows the mod's choices.
- **Write any choice the fix makes into [decisions.md](decisions.md)**, as
  one row.

### Test it

Give each fix two tests in [test_patchmod.py](../tests/test_patchmod.py):
one that it fixes the problem, and one that it's left out once the cause is
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

### Check it in game

Build, rebuild the playset, and play. Then check that the log entries the
fix aimed at are gone. When the fix copies an event or system, the log has
a notice that one with that id already exists, naming the mod's file. That
notice is the proof the patch's copy won.

The full checklist for adding a fix is in
[cold-steel-mix.md](patches/cold-steel-mix.md#add-a-fix).
