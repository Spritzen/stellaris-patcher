# Game report: Cold Steel Mix build, long session, 4 October 2026

**Ten and a half hours of play, from 2244 to 2282, and the error log shows
nothing that breaks the game. The patch's fixes all held, and no entry comes
from the patch.** Play logged 95 entries, about two and a half per game year.
80 of them are bugs in the game's own script.

- **The patch holds over a long game.** None of the entries fixes 1–7
  removed in [run 4](2026-10-03-cold-steel-mix-errors-run-4.md) came back,
  and no entry names one of the patch's files. Fix 4's zoom mismatch stays
  gone. Fix 1 is still untested in play: the save has no Dyson sphere,
  quantum catapult, Starlit system or Voidspawn storm.
- **Loading logged 108 problems, against 96 in run 4. The causes are the
  same.** This run loaded a 2244 save instead of making a new galaxy, so more
  starbases and event text were read while loading. See [Loading](#loading).
- **Mods caused 15 of the 95 play entries.** More Events Mod 11, Starbase
  Extended 3, Planetary Diversity 1. Only Planetary Diversity's shows in
  play: broken text in a tooltip. See [During play](#during-play).
- **One new patch candidate.** Planetary Diversity's text calls
  `[GetAdministratorPluralWithIcon]`, which the game no longer has. See
  [Planetary Diversity](#planetary-diversity-1).
- **The Workshop upload works, but our builder doesn't handle it yet.** The
  patch is now played from its Workshop copy, as intended. The builder
  doesn't recognise that copy as itself, so a rebuild would leave out all
  seven fixes. See
  [The builder](#the-builder-would-drop-every-fix).

## The run

| | |
|---|---|
| Game | Stellaris 4.5.1 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last |
| Patch | The Workshop copy, `workshop:3812655652`, version `2026.10.03`. This is the deployed patch: the local link and `.mod` file were removed from the game's `mod/` folder after the upload. The Workshop copy matches our source folder byte for byte |
| Built | 08:12 local time on 4 October. The playset hasn't changed since, and the build record has no mismatches |
| Session | Started 11:38 local time. Loaded the `2244.10.01` save and played to `2282.08.11`, saved at 22:14 |
| Empire | Elven Divine Order, the same game as the [solid-background report](2026-10-03-cold-steel-mix-solid-background.md) |
| Logs | `error.log`: 9,141 lines, 6,672 entries. 6,577 are from loading (11:38–11:39), 95 from play (11:44–22:12). `game.log`: event picks and 12 AI defaults |

The mods are the same as in run 4. **Stellar AI**, second in load order, has
been in the playset since run 3. The earlier reports don't name it because
it logs nothing but 85 override notices.

## Compared with run 4

| Group | Run 4 | This run |
|---|---:|---:|
| Universal Resource Patch: resources not installed | 5,717 | 5,717 |
| Override notices | 752 | 752 |
| Problems while loading | 96 | 108 |
| Problems during play | 0 (3 minutes) | 95 (10.5 hours) |
| **Total** | **6,565** | **6,672** |

## The patch's fixes

**None of the names the fixes removed appear in the log.** Searched the raw
log as in run 4: no `MEDIUM_GUN_01*`, `build_block_radius`,
`starbase_formation_priority`, `sol_neighbor`, `is_pd_planet_for_aqua_trait`,
`starlit`, `voidspawn`, `rs_d_dark_matter`, `fire_rate_reduction`,
`hp_increased`, `nsc.requires`, `PLANET_SCALE_SYSTEM` or `ZOOM_STEPS`. No
entry names a patch file.

Two fixes weren't really tested by this run:

- **Fix 1**: the entities it restores only load when one of those
  megastructures or storms exists. The save has 12 Dyson swarms, which fix 1
  doesn't touch, and none of the four it does.
- **Fix 5**: Sol neighbours only matter when a galaxy is made. This run
  loaded a save. Run 4 checked it.

Whether the solid background came back can't be seen here. It logged
nothing the first time either.

## Loading

**Same causes as run 4, with more instances because a save was loaded.**
Run 4's log is gone, so the groups are compared by kind, not line by line.

| Group | Run 4 | This run | Change |
|---|---:|---:|---|
| Starbase Extended 3.0 | 47 | 50 | +3: the humanoid starport asks for attach points `part5`–`part7` as well as `part4`. Same cause, logged while the save loaded |
| Diverse Rooms (All in One) | 28 | 30 | +2 of the same kind: names of ethics and governments from mods not installed. Which two can't be told without run 4's log |
| Real Space family, with Cinematic Camera | 9 | 8 | −1: the zoom mismatch, removed by fix 4 |
| More Events Mod | 0 | 6 | Two specimen descriptions (`mem_laser_rifle_desc_details`, `mem_holo_projector_desc_short`) use `[From.From.GetName]`, which has nothing to point at while a save loads. Text only |
| The game's own | 5 | 6 | Five lines of game text with nothing to point at while loading, and the missing `trait_organic` from before. Run 4's four `founder_species` entries fired during play instead (2) |
| Small things | 7 | 8 | +1: "Could not find files for mod" for Diverse Rooms' Workshop folder. The folder is there and the build carries its files, so it's harmless. Cause not found |
| **Total** | **96** | **108** | |

Details of each group are in
[run 3](2026-10-03-cold-steel-mix-errors-run-3.md#whats-left-by-mod).

## During play

**95 entries over 38 game years. None stopped play.**

| Source | Entries | Matters? |
|---|---:|---|
| The game's own script | 80 | No, or not that the log shows. Two of these are in files a mod replaces, see [below](#the-games-own-80) |
| More Events Mod | 11 | No. Each check gives the right result |
| Starbase Extended 3.0 | 3 | No |
| Planetary Diversity | 1 | Yes, a little: broken text in a tooltip |
| **Total** | **95** | |

### The game's own (80)

All in the game's own files, which no mod in the build replaces, unless
noted.

| What | Entries | Where |
|---|---:|---|
| The Expel Population decision saves `refugee_pop`, then can't find it inside `refugee_pop_effect`. The check for a destination fails. The log doesn't say what then happens to the pop | 28 | `decision_expel_population`, line 324 of `common/decisions/01_political_decisions.txt`. AI empires used it twice, at 15:59 and 20:14 |
| Tooltip text checks an empire's ethics or authority on a colony or a situation. Run 4's `founder_species` entries are 2 of these | 13 | `common/scripted_loc/07_scripted_loc_first_contact_dlc.txt` and `13_scripted_loc_shroud.txt` |
| Event text names something with nothing to point at: the Astral Rift nomads message, the pirate event, a Zroni relic site, and one bare `[GetName]`. `pirate.1` also couldn't find its system | 12 | `nomads_1`, `events_1` and `ancient_relics_events` text |
| An observatory's output is worked out for an empty starbase (no name, id 4294967295) | 7 | `starbase_observatory_physics_output_mult`, from line 613 of `common/starbase_buildings/00_starbase_buildings.txt` |
| One-off event script errors: traits that can't be added (3), pop ethics (2), `ancrel.9076` with no valid options, a relic already owned, trust added to oneself, three Curator targets, `random_situation` in the wrong scope, a planet with no owner in `timeline_events.txt`, a trade deal command that wouldn't parse, two missing sounds | 16 | Various |
| A First Contact pre-FTL planet, "Mantle", has no room for a foundry and a research lab when it's given them | 2 | The game's pre-FTL and game-start scripts |
| A machine empire's Lost Colony parent can't get its research zone | 1 | Real Space 4.0's copy of `federations_initializers.txt`, line 1179. The game's own file has the same code, so the bug is the game's |
| The situation log can't find a list named `entries` | 1 | UI Overhaul Dynamic's `interface/situation_log.gui`. The game's own file has the same names, so the game most likely logs this without the mod |

### More Events Mod (11)

- **9: `leader_forge_leader` isn't set.** When an Ancestors' Grudge relic is
  used, `mem_ancestors_grudge/random_leader.txt` compares leaders with
  `event_target:leader_forge_leader`. That's only set when the relic's planet
  has a governor. Comparing with an unset target logs an error but gives the
  right answer. It fired three times, 3 entries each.
- **1: a relic added twice**, line 3,234 of `mem_ancestors_grudge_events.txt`.
  The empire already had it.
- **1: `mem_surveyor.301` checks `from.owner`** ten years after it's queued
  (line 7,042 of `mem_surveyor.txt`). The planet had no owner by then. The
  trigger fails, which is the right result.

### Starbase Extended 3.0 (3)

- **1: a building check on an arkship.** `advanced_military_program`
  (line 772 of `sbx_3_0_starbase_buildings.txt`) checks the starbase's
  `solar_system`. The game checked it on starbase 351, "New Opalag", which
  the save shows is a science arkship: a moving starbase with no system. The
  check fails, so the building isn't offered there. Correct result.
- **2: the humanoid starhold asks for attach points `part6` and `part7`.**
  The same cause as the starport's, in run 3's animations row.

### Planetary Diversity (1)

**The one play entry worth fixing.** Planetary Diversity replaces the
game's text for the bureaucrats' unity modifier,
`mod_planet_bureaucrats_unity_produces_mult`, with one that calls
`[GetAdministratorPluralWithIcon]`. The game no longer has that function.
Its own text uses `$bureaucrat_type_plural_with_icon$`, and other game text
uses `[GetBureaucratPluralWithIcon]`. It was logged once, at 15:11, showing
"+15%".

Three more keys call the same function: `pd_necro_planet_tooltip`,
`pd_aw_necro_planet_tooltip` and `pd_aw_necro_city_planet_tooltip`, in
Planetary Diversity and its Ascension Worlds add-on. Those tooltips show the
same broken text whenever they're shown.

## Not errors: AI empires defaulting

**12 AI empires defaulted on their debts between 2247 and 2282**, about one
every three years (`game.log`, the game's deficit situation). At the end,
three more were in deficit, all with the "do nothing" approach. Stellar AI
runs the AI's economy in this playset. With no game without it to compare
against, this report can't say whether that's high. The log line leaves the
country and resource blank; that's the game's own text.

## The builder would drop every fix

**The patch is now deployed from the Workshop, as `workshop:3812655652`, and
that's how it stays. The builder only skips its own layer under the local key,
`local:stellaris_patcher_cold_steel_mix`** (in
[\_\_main\_\_.py](../../src/stellaris_patcher/__main__.py)). So it treats the
Workshop copy as another mod that already ships the patch's files. A dry run
now reports, for example, "`nsc_starbases.txt` now comes from
workshop:3812655652, not Starbase Extended", and leaves out all seven fixes.

The Workshop patch is fine. But the next rebuild, after a game or mod update,
would write a patch with nothing in it. `--add-to-playset` would also add a
local copy beside the Workshop one, and re-create the link that was removed. `make check` fails on it too:
`test_every_fix_applies_to_the_real_cold_steel_mix` reads the real playset
and gets all seven fixes left out.

**Fix: skip both keys.** The Workshop id is the `remote_file_id` the
launcher saves in the patch's descriptor
([decision 20](../decisions.md)). `--add-to-playset` should also leave the
playset alone when the Workshop copy is already in it.

## What to do next

| # | Problem | Status |
|---|---|---|
| | The builder doesn't skip the patch's Workshop copy | **Done** on 5 October: it skips both keys |
| 8 | Starbase Extended's duplicate `potential` blocks, the `category` trigger, two missing buildings | Open, from [run 3](2026-10-03-cold-steel-mix-errors-run-3.md#what-a-patch-mod-could-fix) |
| 9 | Orbital ring sections, starbase window items, sounds, animations | Open, from run 3. Cosmetic |
| 10 | Planetary Diversity's `[GetAdministratorPluralWithIcon]`: one modifier line and three necro world tooltips | **Done** on 5 October, in `replace/` ([patch](../patches/cold-steel-mix.md#what-each-fix-does)). Was: Ship the four keys with `[GetBureaucratPluralWithIcon]`, or the game's own text for the modifier. Outside `replace/`, the file whose name sorts first wins ([merge_rules.json](../../src/stellaris_patcher/data/merge_rules.json)), so the patch's file must sort before Planetary Diversity's, or go in `replace/` |

Still to check in game: whether the solid background came back, and fix 1's
megastructures.

## How this was worked out

- Ran Cold Steel's error reader (`ErrorReader`) read-only, from its mounted
  source, with its cache in a scratch folder, as in runs 3 and 4.
- Split the entries at 11:39:28, after the last entry from loading the save.
- Moved entries from "Game / unknown" to the mods their files or text belong
  to: three `.anim` files to Starbase Extended, `nospec.dds` to Real Space
  4.0, the track to Apocryphos, six text lines to More Events Mod, one to
  Planetary Diversity. Moved two the other way, to the game, after comparing
  Real Space's `federations_initializers.txt` and UI Overhaul's
  `situation_log.gui` with the game's own.
- For each play entry, looked up which mod the named file came from in the
  build record, and read the code at that line.
- Unpacked the 2244 and 2282 saves into a scratch folder. Looked up starbase
  351, and listed the megastructures and deficit situations.
- Compared the patch's Workshop copy with our source folder, and ran the
  builder without `--write`.
- Searched the raw log for each name the fixes removed, as in run 4.

**Limits.** Run 4's log is gone, so loading is compared by kind. One galaxy
and one empire: fix 1 and fix 5 weren't exercised. Visual problems, like the
solid background, don't reach the logs.
