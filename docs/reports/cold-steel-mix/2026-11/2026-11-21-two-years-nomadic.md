# Two years as a Nomadic empire: Cold Steel Mix, 21 November 2026

**The first run with Starbase Extended 1.3.6 and fix 44 logged 1,754
problems, against last run's 50. 1,708 of them are new, and all are ACoT's
ship sizes in Starbase Extended's starbase trigger.** No mod in the
playset defines those 28 sizes. The game logs each one at every use of the
trigger, 61 times. Fix 44's copy keeps them, so the entries name the
patch's file, but Starbase Extended 1.3.6 alone would log the same. A
change to fix 44 is proposed: take out the sizes nothing defines too. The
other 46 problems are the same as last run's. Play logged nothing. Fix 44
holds: every tier-3 arkship design in the save has the arkship combat
computer and a juggernaut reactor.

- **ACoT's sizes log 1,708 entries at load.** `Failed to deferred read key
  reference acot_… from database`, 61 for each of the 28 sizes, one per
  use of `ship_uses_starbase_components` in the game's component
  templates. The [Starbase Extended 1.3.6 update](2026-11-21-starbase-extended-1.3.6-update.md)
  left this open. Now it's known: the game checks them.
- **Fix 44 works.** The trigger's duplicate notice names the patch's file,
  so its copy wins. All 34 empires' default tier-3 arkship designs have
  `COMBAT_COMPUTER_ARKSHIP` and a `JUGGERNAUT_…_REACTOR`. The log has no
  entry for the three arkship sizes the fix takes out.
- **The patch held.** Cold Steel built the playset at 20:58, just after the
  patch was written. Its 75 patch files match our folder byte for byte, as
  do Starbase Extended's 92 winning files. 41 duplicate object notices name
  the patch's files: last run's 40 and fix 44's trigger. None of the names
  the fixes removed are in the log.
- **The player's arkship stayed at tier 1.** It's a science arkship, with
  its own computer. An upgrade to tier 3 wasn't reached in two years.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.4 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, written at 20:58 with all 32 fixes. Its 75 files in the build match our patch folder byte for byte |
| Built | The Cold Steel build at 20:58, after Starbase Extended 1.3.6 and the patch. The build record has no mismatches |
| Session | Started 20:59:19. The galaxy was made at 21:00:47. The ironman save reached 2202.02.23 at 21:13:56. Two years and two months in about 13 minutes |
| Empire | Gundersen Research Society, the game's `humans3` preset: Lost Colony, imperial, Philosopher King and Star Seekers. Nomadic, with one tier-1 science arkship, the Wayfarer |
| Logs | `error.log`: 8,312 entries. 5,724 resources not installed, 834 override notices and 1,754 problems: 1,753 from loading and the empire designer, 1 from game start, none from play. `game.log`: event picks only |

## Compared with earlier runs

Two years, against 17 months in the [first 4.5.4 run](2026-11-14-4.5.4-first-run.md)
and two years in the [two years on 4.5.3](2026-11-04-two-years-4.5.3.md)
run. All three are new galaxies.

**Resources not installed: 5,724, the same.** Universal Resource Patch's
topbar lists, as before.

**Override notices: 834, one more.** 288 duplicate objects, 480 entities, 23
section templates, 31 events and 12 variables. The one new notice is fix
44's `ship_uses_starbase_components`.

| Group | Two years on 4.5.3 | First 4.5.4 run | This run | Change |
|---|---:|---:|---:|---|
| **Starbase Extended 1.3.6's ACoT sizes, while loading** | 0 | 0 | **1,708** | New. See [ACoT's ship sizes](#acots-ship-sizes-1708) |
| Diverse Rooms (All in One) | 27 | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | 6 | None |
| The game's own, while loading | 1 | 1 | 1 | None: the missing `trait_organic` |
| Real Space and the four-star classes, while loading | 53 | 0 | 0 | Gone with fix 43 |
| The game's `founder_species` check, in the empire designer | 3 | 3 | 3 | None |
| More Events Mod, at game start | 1 | 0 | 1 | Its ancient empire's culture notice, as in the 4.5.3 run |
| In play | 0 | 5 | **0** | The astral rift message didn't come |
| **Total** | **100** | **50** | **1,754** | |

## The patch's fixes

**The game uses every copy the patch ships.** 41 duplicate object notices
name the patch's files:

| Fix | Objects | Notices naming the patch |
|---|---|---:|
| 34 | 21 starbase sizes | 21 |
| 32 | 8 of Starbase Extended's buildings and 2 of its modules | 10 |
| 41 | 4 Gaia Seeders | 4 |
| 29 | Asteroid Mining, Space Foundry, Space Factory | 3 |
| 37 | The Archaeostudies Faculty | 1 |
| 28 | shrimpAI's Hyper Relay | 1 |
| **44** | `ship_uses_starbase_components` | **1** |

The duplicate event notices for fixes 11, 12, 26 and 40 name More Events
Mod's own files, so the patch's copies win.

**None of the names the fixes removed are in the log**, the same list as the
[ten years](../2026-10/2026-10-10-ten-years.md#the-patchs-fixes) run, with
`leader_forge_leader`, the two four-star classes, fix 42's trait and
variable, and fix 44's three arkship sizes. The log has no `solar_system`
and no `Unknown promotion`. Its one `ion_core_effect` is a duplicate entity
notice.

| Fix | In game |
|---|---|
| 44 | **Works in the save.** Every empire has default designs for the three tier-3 arkships, 102 in all. Each has `COMBAT_COMPUTER_ARKSHIP` and a juggernaut reactor, as in the game. No starbase computer or reactor. But its copy logs ACoT's 28 sizes. See below |
| 32 | **The log half is seen again** on a Nomadic empire: no `solar_system` error from `sbx_3_0_starbase_buildings.txt` |
| 43 | Holds. No four-star class entries |
| 5 | Not reached: a Lost Colony start, not Sol |
| 41, 40, 38, 37, 36, 28 | Not reached in two years |

## ACoT's ship sizes (1,708)

All between 20:59:53 and 20:59:54, while loading:

```
Failed to deferred read key reference acot_starbase_citadel_dm from database
common/scripted_triggers/zzzz_stellaris_patcher_cold_steel_mix_starbase_components.txt:32
@ in scripted trigger ship_uses_starbase_components at file: common/component_templates/00_biogenesis_weapons.txt line: 2555
```

- **28 sizes, 61 entries each.** Lines 32 to 58 and 60 of the patch's copy:
  ACoT's 27 starbase, ring, behemoth, arkship and waystation sizes, and
  `precursor_colossus`. No mod in the playset defines any of them. The game
  reads a scripted trigger again at each use, and the game's component
  templates use this one 61 times.
- **Starbase Extended 1.3.6 brought them.** Its 1.3.6 change log says
  "Reworked ACoT compatibility". 1.3.5 had none. Fix 44 copies its trigger,
  so the patch's copy is the one the game reads. Without fix 44, the same
  1,708 would name Starbase Extended's file.
- **They're harmless in play.** A size nothing defines can't match a ship.
  They only fill the log, and slow loading a little.
- **Its second trigger logs nothing.** `ship_uses_special_starbase_components`
  has the same sizes, but nothing uses it.

## Loading, the empire designer and game start (46)

The same 42 loading problems as the first 4.5.4 run, group for group.
Details of each group are in
[run 3](../2026-10/2026-10-03-errors-run-3.md#whats-left-by-mod). Plus the
same 3 `founder_species` entries in the empire designer, and More Events
Mod's culture notice at game start: `Changing from GfxCulture '' to
'mem_ancient_01'`, as in the [two years on 4.5.3](2026-11-04-two-years-4.5.3.md)
run.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 48 | Starbase Extended 1.3.6's trigger names 28 ACoT ship sizes no mod in the playset defines: 1,708 load entries | **Done** after this report was written ([decision 64](../../../decisions.md), changed). Was: **Change fix 44**: also take out each `is_ship_size` line naming a size no ship size file in the playset defines. Its own and the game's sizes stay. Then the copy has only sizes that exist, and the 1,708 entries go. Decision 64 kept ACoT's sizes, as Starbase Extended's intent. This run shows they cost 1,708 entries, so it would change. With ACoT in a playset, its sizes are defined, and they stay |
| — | A tier-3 arkship in play | Not reached. The default designs in the save already show fix 44 working. To see it in play, upgrade an arkship to tier 3 and look at its actions |
| — | Volcanic Climate Mods in the species designer | Not looked at, as last run |
| 5, 41, 40, 38, 37, 36, 28 | Not checked in game | Not reached. Fix 5 needs a Sol start |

## How it was worked out

- `error.log` was read with our
  [error_log.py](../../../../src/stellaris_patcher/paradox/error_log.py) and
  split by time with `game.log`: the game started at 20:59:19 and made the
  galaxy at 21:00:47. The last entry is at 21:00:50.
- Entries were grouped by source and text. Universal Resource Patch's
  `strategic_resources_gui_group.cpp` entries, and the duplicate object,
  entity, section template, event and variable notices, were counted apart.
  The ACoT entries were counted by file and line.
- `dlc_load.json` showed the one mod loaded. Cold Steel's build record
  (`builds/d8f5e037….json`) gave the build time, the patch's place last,
  and the source of each file. Each patch and Starbase Extended file in the
  built mod was compared with its source.
- Each duplicate object notice was matched to the files the patch ships.
- The raw log was searched for the names the fixes removed.
- Each ACoT size was looked up in the game's and every subscribed mod's
  `common/ship_sizes`.
- The ironman save was unpacked to a scratch folder. Every arkship design's
  ship size and required components were read, and the player's country,
  government and ships.

## Limits

- **Two years only.** The player's arkship never reached tier 3, so fix 44
  was seen in the default designs, not on an upgraded arkship.
- **Without fix 44 isn't known.** No run had Starbase Extended 1.3.6
  without the fix, so it's not seen whether the game would have picked a
  starbase computer.
- **Nothing on screen was checked against the report.** Nothing was
  reported looking wrong in game.
