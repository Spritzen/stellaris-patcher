# Game report: Cold Steel Mix with three mods switched off, 9 October 2026

**A new galaxy, played four game months in about eleven minutes, to
2 May 2200. It's the first run with Starbase Extended 3.0, Ascension Worlds
and shrimpAI switched off ([decision 35](../decisions.md)). The patch held,
play logged nothing, and the user saw nothing wrong. Problems fell from 112
to 47. One thing came back: with Ascension Worlds off, Planetary Diversity's
own Lithoid Budding is the one in use, and it has the same 4.5.2 gap fix 19
patched.**

- **Switching the three mods off cleared 65 problems.** Starbase Extended's
  47 are gone. The game's Life-Seeded check fell from 21 entries to 4. Override
  notices fell from 755 to 230. See [Compared with earlier runs](#compared-with-earlier-runs).
- **The patch was loaded and its fixes held.** The build lists it last, and
  its 13 game files match our source byte for byte. None of the names the
  fixes removed is in the log. See [The patch's fixes](#the-patchs-fixes).
- **Fix 17's system is in this galaxy, and it isn't sealed.** The save has
  the Surveillance Supercomputer system without the `sealed_system` flag. The
  jump itself wasn't tried.
- **New: Planetary Diversity's Lithoid Budding splits the Massive Crater
  bonus again.** Ascension Worlds' copy of `04_species_traits.txt` used to
  replace Planetary Diversity's. Fix 19 patched Ascension Worlds' copy. With
  it off, Planetary Diversity's copy is the one in use, and it lacks the same
  line. Fix 19 is left out, so the 4.5.2 fix is undone again. See
  [Lithoid Budding](#planetary-diversitys-lithoid-budding).
- **One new entry, from More Events Mod, and it's harmless.** Its Sadrell
  story couldn't place a system at the usual spacing, so the game retried
  without it. All five Sadrell systems are in the save.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 24 mods with `Cold Steel Mix patch` last. Starbase Extended 3.0, Planetary Diversity - Ascension Worlds and shrimpAI are switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.08`, with fixes 1, 4–7, 10–12 and 15–17. Fixes 2, 3 and 19 are left out: their mods are off. Its 13 game files in the build match our source folder byte for byte. A dry run of the builder today writes the same 13 files. The Workshop copy (`3812655652`) isn't on disk |
| Built | The Cold Steel build at 21:35 local time. The build record has no mismatches |
| Session | Started 21:36:04. New galaxy, seed 911099098, made at 21:37:33: medium, `spiral_3`, 18 empires, 588 systems. Played from `2200.01.01` to `2200.05.02`, about eleven minutes. Saved at 21:49. No sign of a crash |
| Empire | Divine Elven Order, a Life-Seeded origin |
| Logs | `error.log`: 5,994 entries. 5,717 resources not installed and 230 override notices. 47 problems: 43 from loading and game start, 4 from the game's Life-Seeded check, none from play. `game.log`: four event picks |

The log's clock is local time, one hour ahead of the file times. The error
log's last entry is at 21:37:45, 12 seconds after the galaxy was made. The
first event pick is at 21:38:11, and `game.log` runs to 21:47:45.

The game logs an `Invalid supported_version` for every `.mod` file in its
mod folder, loaded or not. So Starbase Extended's `.mod` file is still in the
log, though the mod isn't loaded.

## Compared with earlier runs

| Group | 4.5.2 first run | Pre-upload | This run |
|---|---:|---:|---:|
| Problems while loading and at game start | 96 | 91 | 43 |
| The game's Life-Seeded check | 21 | 21 | 4 |
| Problems during play | 0 (4 minutes, 26 days) | 0 (7 minutes, 3 years) | 0 (11 minutes, 4 months) |
| Override notices | 754 | 755 | 230 |

- **Override notices: 525 fewer.** Starbase Extended and Ascension Worlds
  have about 520 top-level blocks in their `common/` and `events/` folders,
  many of them copies of the game's or Planetary Diversity's. That's about
  the size of the drop.
- **The Life-Seeded check: 17 fewer.** The 4 left all came in the empire
  designer, for the player's own Life-Seeded empire. The pre-upload run also
  had 18 as the galaxy was made, one per empire, and this run has none, with
  the same 18 empires. Neither switched-off mod touches the origin or the
  trigger, so the cause wasn't found. The entries were harmless either way.

## The patch's fixes

**None of the names the fixes removed are in the log.** The raw log has no
`build_block_radius`, `starbase_formation_priority`, `sol_neighbor`,
`is_pd_planet_for_aqua_trait`, `starlit`, `voidspawn`, `rs_d_dark_matter`,
`fire_rate_reduction`, `hp_increased`, `PLANET_SCALE_SYSTEM`, `ZOOM_STEPS`,
`GetAdministratorPluralWithIcon`, `mod_planet_bureaucrats`, `t7_upkeep` or
`Malformed`. No entry names a patch file. Fixes 2 and 3's
`MEDIUM_GUN_01*` and `nsc.requires` are gone too, with Starbase Extended.

| Fix | What the log or save shows | In play |
|---|---|---|
| 11, 12 | Both duplicate event notices name More Events Mod's file, as before. The patch's events win | Not fired. Neither event can before year 20 |
| 15 | No `Malformed token` for `@shield_*_t7_upkeep_*` | No empire has researched the shield |
| 16 | Not logged. The build takes `mutation_weapon_components.csv` from the patch | No Large Mega Bombard fauna in this save |
| 17 | `An initializer called "surveillance_supercomputer_system" already exists`, naming Real Space's `special_system_initializers.txt` at line 2079. The patch's `!!_` file was read first. **The system is in this galaxy, a neutron star, and its flags have no `sealed_system`** | No jump drive yet, so the jump wasn't tried |
| 2, 3, 19 | Left out. Their mods are switched off | Fix 19's Lithoid Budding problem is back through Planetary Diversity. See below |

## Loading

**43 entries. 42 match the pre-upload run group for group. Starbase
Extended's 47 are gone.**

| Group | Pre-upload | This run | Change |
|---|---:|---:|---|
| Starbase Extended 3.0 | 47 | 0 | **−47**: switched off. Its 3 game-start entries went too |
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| The game's own | 1 | 1 | The missing `trait_organic` |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| More Events Mod | 2 | 1 | The Lost Emperor and ship set entries depend on the galaxy and aren't in this one. **+1 new**: the Sadrell spawn |
| **Total** | **91** | **43** | |

### More Events Mod (1)

**The Sadrell story's science system was placed closer to its neighbours
than the game prefers.** At game start, `mem_sadrell.1` spawns five systems
with `spawn_system` (`events/mem_sadrell.txt`, line 125). The game logged:

```
spawn_system/move_system: Failed to find position at minimum distance SPAWN_SYSTEM_BUFFER_DISTANCE = 10 from other systems at  file: events/mem_sadrell.txt line: 125; retrying without checking SPAWN_SYSTEM_BUFFER_DISTANCE
```

The retry worked. The save has all five systems: the home cluster and its
industrial, agricultural, homeworld and science systems. It's a notice, not
an error, and it depends on the galaxy. No earlier report has it.

## Planetary Diversity's Lithoid Budding

**The Massive Crater's budding bonus is split over the planet's pop groups
again, as it was before 4.5.2.** It's row D of the
[first 4.5.2 report](2026-10-07-cold-steel-mix-4.5.2-first-run.md#mod-copies-that-undo-a-fix),
now from Planetary Diversity instead of Ascension Worlds.

- **Both mods ship a whole `common/traits/04_species_traits.txt`.** The same
  name replaces the game's file. Ascension Worlds loads after Planetary
  Diversity, so its copy used to replace Planetary Diversity's too. With it
  off, the build takes Planetary Diversity's.
- **Planetary Diversity's `trait_lithoid_budding` lacks
  `divide_over_pop_groups = no` on the crater bonus**, the line 4.5.2 added
  ("Crystallization now gives its full bonus on a Massive Crater"). Its file
  dates from 22 September.
- **Fix 19 only looks at Ascension Worlds' copy.** It's left out while that
  mod is off, so nothing patches Planetary Diversity's.

Today's update check found it. It lists 11 of Planetary Diversity's objects
as new, because they're in use now:

| Objects | What differs from the game's | Effect |
|---|---|---|
| `trait_lithoid_budding` | The missing line above. Its `colony?` checks are written as `exists = planet`, which means the same | The crater bonus is split, as above |
| `trait_cybernetic`, `trait_lithoid_gaseous_byproducts`, `trait_lithoid_scintillating`, `trait_lithoid_volatile_excretions`, `trait_plantoid_phototrophic`, `trait_plantoid_radiotrophic` | `planet_pops`, not 4.5.2's `planet_pops_traits` | Item 18, already [left to the authors](../patches/cold-steel-mix.md#left-to-the-authors). These six came from Ascension Worlds' copy before; now from Planetary Diversity's, which the item already names |
| `trait_plantoid_bloomed`, `trait_plantoid_radiotrophic`, `trait_survivor`, `toxoids.1` | Planetary Diversity's own planet classes added to the game's checks | Planetary Diversity's own work. Nothing of the game's is missing |
| `trait_resilient` | One line moved | None |

The game's terraforming rule is fine. Fix 19's other half isn't needed while
Ascension Worlds is off: More Events Mod's two copies of
`can_terraform_planet` are commented out, so the game's own rule is in use.

A species in this save has Lithoid Budding (the Tharbarite, lithoid). No
planet in the save has a Massive Crater, so the split wasn't seen.

## During play

**Nothing.** Play ran from 21:38:11 to the save at 21:49, four game months,
and logged no entries. Eleven minutes is still short.

## Other changes since the last run

UI Overhaul Dynamic changed one file on 8 October,
`interface/ui_overhaul_qhd-gfx/ui_overhaul_qhd_fixes.gfx`, for QHD screens.
The update check found no game file it undoes.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 21 | Planetary Diversity's Lithoid Budding splits the Massive Crater bonus, now that Ascension Worlds is off | **Done** on 9 October ([patch](../patches/cold-steel-mix.md#what-each-fix-does), [decision 37](../decisions.md)). Not yet checked in game. Was: Widen fix 19's budding half to whichever mod's copy is in use, Planetary Diversity's or Ascension Worlds'. Same method: a copy of the one trait with the game's line added, in the `!!_` traits file. Fix 19 then lists Planetary Diversity too, so it's written while either is on. It ships one Planetary Diversity trait, so add it to the Whose work table. The terraforming half stays tied to Ascension Worlds |
| 22 | The [switched-off section](../patches/cold-steel-mix.md#mods-switched-off-for-now) doesn't say a switched-off mod can uncover another mod's older copy | **Done** on 9 October, in the [patch doc](../patches/cold-steel-mix.md#mods-switched-off-for-now). Was: Add one line: switching a mod off can put another mod's copy back in use, so run the update check and read its "new" copies, as this report did |
| 18 | Trait resources on `planet_pops` | Unchanged. The same six traits, now from Planetary Diversity alone. Left to the authors |
| 1 | Still unchecked in play | Fixes 11 and 12 firing, 15's upkeep in the ship designer, 16's fauna in combat, 17's jump (its system is in this galaxy), 10's tooltip, 1's megastructures and storms |

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../src/stellaris_patcher/paradox/error_log.py).
- Split the entries by time. Loading lasted until the galaxy was made at
  21:37:33 (`game.log`). Game start lasted to 21:37:45. Play came after
  that. Grouped them by the source in the game's code, then by mod, the same
  way as the last run.
- Checked the build record lists the patch last, and compared its 13 game
  files with the patch folder byte for byte. Ran the builder without
  `--write` to check the patch is current. Read `dlc_load.json` for what the
  game loaded.
- Searched the raw log for each name the fixes removed, and for the
  patch's events and initializer.
- Ran the update check. Read the diffs for Planetary Diversity's 11 new
  copies, and compared the trait lists in the game's, Planetary Diversity's
  and Ascension Worlds' `04_species_traits.txt`: all three have the same 67
  traits.
- Searched the game and every playset mod for `can_terraform_planet`.
- Unpacked the `2200.05.02` save into a scratch folder. Searched it for the
  Surveillance Supercomputer system and its flags, the Sadrell systems,
  Lithoid Budding, Massive Craters, Progenitor shields and Large Mega
  Bombard.
- Counted the top-level objects in Starbase Extended's and Ascension Worlds'
  `common/` and `events/` folders.

## Limits

- **Eleven minutes, four game months.** Too short to say much about play.
- **What happened on screen.** The user saw nothing wrong. Visual problems,
  like the solid background, don't reach the logs.
- **The override notice drop was matched by count.** No copy of the last
  run's log was kept, so the 525 weren't traced entry by entry to the two
  mods.
- **Why the 18 Life-Seeded entries at galaxy creation went** wasn't found.
- **The Lithoid Budding split is read from the files.** It wasn't seen in
  game.
