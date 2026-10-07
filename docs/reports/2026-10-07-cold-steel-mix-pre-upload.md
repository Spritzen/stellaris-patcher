# Game report: Cold Steel Mix, the run before the Workshop upload, 7 October 2026

**A new galaxy, played three game years in about seven minutes, to
8 January 2203. The patch with fixes 15, 16, 17 and 19 was in the game and
held. Play logged nothing, and the user saw nothing wrong. Nothing in this
run stops the upload.**

- **The rebuilt patch was loaded.** It was built at 18:26 and Cold Steel
  rebuilt the playset seconds later. The build lists it last, and its 17
  game files match our source byte for byte. See [The run](#the-run).
- **Fix 15 works: the six shield upkeep errors are gone.** The log has no
  `Malformed token` and no `@shield_*_t7_upkeep_*`. See
  [The patch's fixes](#the-patchs-fixes).
- **Fix 17 wins.** The game logged Real Space's Surveillance Supercomputer
  system as a duplicate, so the patch's copy was read first and is the one in
  use. This galaxy has no Surveillance Supercomputer system, so the jump
  itself wasn't tried.
- **Fixes 16 and 19 can't be seen in the log.** The game doesn't log a
  replaced `.csv`, trait or game rule. Both sort where they should in the
  build.
- **One new entry, from More Events Mod: its Lost Emperor story couldn't
  place its system.** It sets its "spawned" flag anyway, so the story is
  lost in this galaxy. It's More Events Mod's own code, not a clash. See
  [More Events Mod](#more-events-mod-2).

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.07`, with fixes 1–7, 10–12, 15–17 and 19. Its 17 game files in the build match our source folder byte for byte. The Workshop copy (`3812655652`) isn't on disk |
| Built | Our patch at 18:26:11 local time, the Cold Steel build at 18:26:38. The build record has no mismatches |
| Session | Started 18:26:56. New galaxy, seed 1010586431, made at 18:27:53: medium, `spiral_3`, 18 empires, 592 systems. Played from `2200.01.01` to `2203.01.08`, about seven minutes. Saved at 18:35:34. No sign of a crash |
| Empire | Commonwealth of Man, in Sol (`com_sol_system`) |
| Logs | `error.log`: 6,584 entries. 5,717 resources not installed and 755 override notices. 112 problems: 91 from loading and game start, 21 from the game's Life-Seeded check, none from play. `game.log`: event picks and one More Events Mod log line |

The log's clock is local time, one hour ahead of the file times. The error
log's last entry is at 18:28:16, 23 seconds after the galaxy was made. The
first event pick is at 18:28:19, and `game.log` runs to 18:35:26.

The override notices are the last run's 754 plus Real Space's initializer
from fix 17.

## Compared with earlier runs

| Group | Run 5 (new galaxy) | 4.5.2 first run | This run |
|---|---:|---:|---:|
| Problems while loading and at game start | 89 | 96 | 91 |
| The game's Life-Seeded check | 36 | 21 | 21 |
| Problems during play | 24 (3.5 hours, 25 years) | 0 (4 minutes, 26 days) | 0 (7 minutes, 3 years) |

## The patch's fixes

**None of the names the fixes removed are in the log.** The raw log has no
`MEDIUM_GUN_01*`, `build_block_radius`, `starbase_formation_priority`,
`sol_neighbor`, `is_pd_planet_for_aqua_trait`, `starlit`, `voidspawn`,
`rs_d_dark_matter`, `fire_rate_reduction`, `hp_increased`, `nsc.requires`,
`PLANET_SCALE_SYSTEM`, `ZOOM_STEPS`, `GetAdministratorPluralWithIcon`,
`mod_planet_bureaucrats`, `t7_upkeep` or `Malformed`. No entry names a patch
file.

| Fix | What the log or build shows | In play |
|---|---|---|
| 11, 12 | Both duplicate event notices name More Events Mod's file, as in the last run. The patch's events win | Not fired. Neither event can before year 20 |
| 15 | The six `Malformed token` entries for `@shield_*_t7_upkeep_*` are gone. The game now reads the patch's definitions | No empire has researched the shield. The only design with it is More Events Mod's own ancient station, Utgard |
| 16 | Not logged. The build takes `mutation_weapon_components.csv` from the patch | No Large Mega Bombard fauna in this save |
| 17 | `An initializer called "surveillance_supercomputer_system" already exists`, naming Real Space's `special_system_initializers.txt` at line 2079, where its copy starts. The patch's `!!_` file was read first | This galaxy has no Surveillance Supercomputer system |
| 19 | Not logged. The game logs no duplicate trait or game rule: Planetary Diversity's 12 copies of game traits aren't logged either. In the build, the patch's trait file sorts first and its game rule file sorts last | A species in the save has Lithoid Budding. No Massive Crater or consecrated world was checked |

Fix 17's notice is the same check fixes 11 and 12 give, and it will be in
every run. [cold-steel-mix.md](../patches/cold-steel-mix.md#check-in-game)
says the log "may" name Real Space's copy. Item 2 below corrects it.

## Loading

**91 entries. 89 match run 5 and the first 4.5.2 run group for group. The
other 2 are More Events Mod's.**

| Group | 4.5.2 first run | This run | Change |
|---|---:|---:|---|
| Starbase Extended 3.0 | 47 | 47 | None. 3 of them come at game start, as before |
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| The game's own | 1 | 1 | The missing `trait_organic` |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| More Events Mod | 7 | 2 | **−6** shield upkeep entries, fixed by fix 15. **+1 new**: the Lost Emperor spawn. The ship set notice is back |
| **Total** | **96** | **91** | |

### More Events Mod (2)

**The Lost Emperor story couldn't place its system, so the story is lost in
this galaxy.** At game start, `mem_lost_emperor.1000` rolled the newer
Neochadamus story. It calls `test_spawn_neochadamus` on the player's home
system (`common/scripted_effects/mem_descended_scripted_effects.txt`,
line 28). The game logged:

```
spawn_system: found no possible system for the new system to connect with around  common/scripted_effects/mem_descended_scripted_effects.txt:28 @ scripted effect test_spawn_neochadamus at file: events/mem_lost_emperor.txt line: 65
```

- **The effect sets `mem_system_spawned` before it spawns.** The save has
  that flag, and no `mem_descended_system`.
- **The story starts only when a ship enters the system it failed to make**
  (`mem_descended.1` checks the star flag `mem_descended_system`). So it never
  starts, and nothing else happens. No error follows.
- **`game.log`'s "spawned Delta Cancri" is wrong.** The effect logs
  `last_created_system`, which is still the last system made before it:
  Distant Stars' sealed system.
- **The cause is the request, not a clash.** It asks for a spot 8 to 15
  units from the home system that connects to a system 4 to 8 jumps away.
  Close to home, most systems are fewer jumps away. The game's own
  `spawn_system` calls with a jump limit almost all connect within 0 or 1
  jumps, and none asks for a minimum above 2. Both files are More Events Mod's alone.

It depends on the galaxy and on a roll. The story picks nothing two times in
three, and no earlier report has this entry.

The other entry is the ship set notice: an empire switched to More Events
Mod's `mem_ancient_01` at game start. It isn't an error. Run 3 and the first
4.5.2 run had it too.

## The game's Life-Seeded check (21)

**The same 21 as the last run.** 3 came in the empire designer at 18:27:47.
18 came as the galaxy was made, one per empire. All are the game's own
line in `00_origins.txt`. Harmless.

## During play

**Nothing.** Play ran from 18:28:19 to 18:35:26, three game years, and
logged no entries. Run 5 averaged about one entry per game year, so this is
fewer than expected. Seven minutes is still short.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 1 | Upload the patch to the Workshop | Nothing in this run stops it. Still unchecked in play: fixes 11 and 12 firing, 15's upkeep in the ship designer, 16's fauna in combat, 17's jump, 19's crater bonus and terraforming, 10's tooltip, 1's megastructures and storms |
| 2 | [cold-steel-mix.md](../patches/cold-steel-mix.md#check-in-game) says the log "may" name Real Space's copy for fix 17 | **Done** on 7 October. Was: Say instead that it names Real Space's `special_system_initializers.txt` once, and that this is the check that the patch wins, as for fixes 11 and 12. Also say fix 15's check at load: no `Malformed token` for `@shield_*_t7_upkeep_*` |
| 20 | More Events Mod's Lost Emperor story can fail to place its system, and then never starts | **Left to the author** on 7 October, and listed on the patch's Workshop page ([decision 33](../decisions.md)). Was: Leave it to More Events Mod's author. It's their own code and rare. A patch would copy one scripted effect for a story that rolls in one game in three. Add it to the Workshop page's known issues only if it shows again ([decision 33](../decisions.md)) |
| 8, 9, 18 | Starbase Extended's starbase items and triggers, the trait stacking | Unchanged. Left to the authors and listed on the Workshop page |

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../src/stellaris_patcher/paradox/error_log.py).
- Split the entries by time. Loading lasted until the galaxy was made at
  18:27:53 (`game.log`). Game start lasted to 18:28:16. Play came after
  that. Grouped them by the source in the game's code, then by mod, the same
  way as the last run. The totals match the last run's groups with only the
  changes above.
- Checked the build record lists the patch last, and compared its 17 game
  files with the patch folder byte for byte. Read `dlc_load.json` for what
  the game loaded.
- Searched the raw log for each name the fixes removed, and for the
  patch's events, initializer, trait and game rule.
- Listed where the fix 17 and 19 files sort among the build's other files,
  and which files define the system, trait and rule.
- Unpacked the `2203.01.08` save into a scratch folder. Searched it for the
  Surveillance Supercomputer system, Progenitor shields, Large Mega Bombard,
  Lithoid Budding, the Ziaskehorn flag and the Lost Emperor's flag and system.
- Read More Events Mod's `mem_lost_emperor.txt`, `mem_descended.txt` and
  `mem_descended_scripted_effects.txt`. Compared its `spawn_system` jump
  limits with the game's own.

## Limits

- **Seven minutes, three game years.** Too short to say much about play.
- **What happened on screen.** The user saw nothing wrong. Visual problems,
  like the solid background, don't reach the logs.
- **Fixes 16 and 19 aren't confirmed in game.** That traits go to the first
  file and game rules to the last comes from Irony's rules. The log can't
  show it.
- **The Lost Emperor's odds.** How often the spawn fails wasn't measured. It
  may depend on galaxy size and shape.
- **Groups were matched by totals.** No copy of the last run's log was kept,
  so the unchanged groups were compared by count, not entry by entry.
