# How a patch mod wins

**A patch file only works if the game picks it over every rival. Which file
wins depends on the game folder.** These rules were tested in game on
2026-10-01, unless marked otherwise.

## Who wins

- **It depends on the folder.** 14 folders keep the first definition, sorted
  by file name. The rest keep the last. `on_actions` merge. It's all in
  [merge_rules.json](../../src/stellaris_patcher/data/merge_rules.json), one
  row per folder ([decision 8](../decisions.md)). A row with a `checked`
  date was confirmed in game. The others come from Irony Mod Manager's rules.
- **Localisation outside a `replace/` folder keeps the first file name. A key
  in `replace/` beats it.** This isn't what Irony says.
- **File paths are matched ignoring case.** Not yet checked in game.
- **Graphics files (`.gfx`, `.gui`, `.asset`) define objects by their
  `name = …` field.** Pictures and sounds clash only as whole files.

## Naming a patch file to win

- **Where the last definition wins, start the name with `z`s.** Use `~`s
  instead if a rival's name starts with `~`, which sorts after `z`. A real
  mod names a file `~ariphaos_…` to sort last.
- **Where the first definition wins, start it with `!`s.**
- **Localisation goes in `localisation/<language>/replace/`.**
- **A whole file keeps its path**, and the patch mod loads last.

[write.py](../../src/stellaris_patcher/patchmod/write.py)'s `winning_name`
does this. On a real 33-mod playset, 699 patch files named this way all won.

## Before writing

- **Check every file we write**: it must parse, and a localisation file must
  name its language. One typo breaks the file in game.
- **Don't ship a choice made against text that has since changed.** It could
  quietly undo a mod's newer fix. Each fix checks its cause is still there
  ([decision 14](../decisions.md)).

## Where a patch mod lives

- **In our own data folder, linked into `mod/`, with a `.mod` file**
  ([decision 15](../decisions.md)). A rebuild is then live with no copying.
- **Never change a `.mod` file that isn't ours.**

## Lessons from the reports

From the [error-log reports](../README.md#reports).

- **Old copies of game files do the most damage.** A mod made for 4.2 that
  ships copies of vanilla files removes everything 4.5 added to those files.
  Ariphaos Unofficial Patch caused 5,361 of 11,463 log entries this way. A
  patch can't fix that object by object. The answer is to drop the mod, or
  leave its old copies out.
- **A version number alone proves nothing.** Real Space - System Scale says
  `v4.5.*` but ships old copies of three game `.asset` files that drop 116
  game entities (fix 1). To find these, compare what a mod's copy defines
  with what the game's copy defines.
- **A parse break loses the rest of the file**, and the errors then appear in
  other files that use what was lost. One renamed trigger
  (`any_system_colony` → `any_system_planet_colony`) cut six event files short.
- **Most of a log is harmless.** Universal Resource Patch's missing resources
  and override notices were 85% of the second run. Filter them out before
  counting.
- **Tracing an error to its mod**: match the file it names to the last mod in
  load order that has it. For an error that names no file, search the mods
  for the name it quotes, and accept a single owner only.
- **The launcher's playset must match Cold Steel's.** If the launcher's copy
  is out of date, starting from the launcher brings a removed mod back.
