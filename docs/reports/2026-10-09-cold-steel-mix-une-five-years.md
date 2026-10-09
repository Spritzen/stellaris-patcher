# Game report: Cold Steel Mix, a United Nations of Earth start, 9 October 2026

**A new galaxy as the United Nations of Earth, played five game years in
about eleven minutes, to 16 January 2205. The patch held, play logged
nothing, and the user saw nothing wrong. It's the first run with fix 21 in
the build. Problems rose from 47 to 67, but none is new to the mods: 17 are
the game's Life-Seeded check coming back, and 4 are the game's own United
Nations of Earth start. No new fix is proposed.**

- **The patch was loaded and its fixes held.** The build lists it last, and
  its 14 game files match our source byte for byte. That includes fix 21's
  Lithoid Budding file. None of the names the fixes removed is in the log.
  See [The patch's fixes](#the-patchs-fixes).
- **Fix 17's system is in this galaxy again, and it isn't sealed.** The save
  has a `sealed_system` flag, but on Distant Stars' own sealed system, where
  it belongs.
- **New: 4 entries from the game's own United Nations of Earth start.** The
  game runs its nomad setup for the Gundersen Research Society before that
  empire has a capital. Real Space's copy of the file is the same. Harmless.
  See [The United Nations of Earth start](#the-united-nations-of-earth-start).
- **The Life-Seeded check is back to 21, and the last report's open question
  is answered.** The 18 entries at galaxy creation come when the user's saved
  Divine Elven Order design isn't the empire being played. See
  [The Life-Seeded check](#the-games-life-seeded-check-21).
- **The Gundersen Research Society defaulted on its debts in May 2204.** The
  game logged it in `game.log`. Nothing in the error log points to a mod. See
  [During play](#during-play).

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 24 mods with `Cold Steel Mix patch` last. Starbase Extended 3.0, Planetary Diversity - Ascension Worlds and shrimpAI are still switched off. The same mods as the last run |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.09`, with fixes 1, 4–7, 10–12, 15–17 and 19's Lithoid Budding half, which now patches Planetary Diversity's copy (fix 21). Fixes 2 and 3 are left out: their mod is off. Its 14 game files in the build match our source folder byte for byte. A dry run of the builder today writes the same 14 files |
| Built | The Cold Steel build at 22:09 on the log's clock. The build record has no mismatches |
| Session | Started 22:10:13. New galaxy, seed 334799361, made at 22:11:19: medium, `spiral_3`, 18 empires, 588 systems. Played from `2200.01.01` to `2205.01.16`, about eleven minutes. Saved at 22:22. No sign of a crash |
| Empire | United Nations of Earth, in Real Space's Sol |
| Logs | `error.log`: 6,014 entries. 5,717 resources not installed and 230 override notices. 67 problems: 46 from loading and game start, 21 from the game's Life-Seeded check, none from play. `game.log`: event picks and one game log line, the Gundersen default |

The log's clock is one hour ahead of the file times, as before. The error
log's last entry is at 22:11:21, two seconds after the galaxy was made. The
first event pick is at 22:11:37, and `game.log` runs to 22:22:02.

The galaxy was made 15 seconds after the main menu loaded, so the empire was
most likely picked from the list, not made in the designer.

## Compared with earlier runs

| Group | Pre-upload | Three mods off | This run |
|---|---:|---:|---:|
| Problems while loading and at game start | 91 | 43 | 46 |
| The game's Life-Seeded check | 21 | 4 | 21 |
| Problems during play | 0 (7 minutes, 3 years) | 0 (11 minutes, 4 months) | 0 (11 minutes, 5 years) |
| Override notices | 755 | 230 | 230 |

The override notices are the same 230: 165 duplicate objects, 30 duplicate
entities, 23 duplicate events, 11 duplicate variables and Real Space's
initializer.

## The patch's fixes

**None of the names the fixes removed are in the log.** The raw log has no
`build_block_radius`, `starbase_formation_priority`, `sol_neighbor`,
`is_pd_planet_for_aqua_trait`, `starlit`, `voidspawn`, `rs_d_dark_matter`,
`fire_rate_reduction`, `hp_increased`, `PLANET_SCALE_SYSTEM`, `ZOOM_STEPS`,
`GetAdministratorPluralWithIcon`, `mod_planet_bureaucrats`, `t7_upkeep`,
`Malformed` or `lithoid_budding`. No entry names a patch file.

| Fix | What the log or save shows | In play |
|---|---|---|
| 11, 12 | Both duplicate event notices name More Events Mod's file, as before. The patch's events win | Not fired. Neither event can before year 20 |
| 15 | No `Malformed token` for `@shield_*_t7_upkeep_*` | Not checked in the save |
| 16 | Not logged. The build takes `mutation_weapon_components.csv` from the patch | No Large Mega Bombard fauna in this save |
| 17 | The initializer notice names Real Space's `special_system_initializers.txt` at line 2079. The patch's `!!_` file was read first. **The system is in this galaxy, Ultima Vigilis, a neutron star, and its flags have no `sealed_system`** | No jump drive yet, so the jump wasn't tried |
| 19, 21 | The patch's `!!_` traits file is in the build, with Planetary Diversity's `trait_lithoid_budding` and the game's `divide_over_pop_groups = no` | Not seen. One species has Lithoid Budding, but the one planet with a Massive Crater (`d_lithoid_crater`) belongs to an empire without it |
| 2, 3 | Left out. Their mod is switched off | |

The player's Sol is Real Space's `sol_system_initializer`, and all nine of
its neighbour systems are in the save. Fix 5 is for the Sol starts of
Planetary Diversity and More Events Mod, which this run didn't use.

## Loading

**46 entries. 42 match the last run group for group.**

| Group | Three mods off | This run | Change |
|---|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None: System Scale's 6 infernal ring world textures, Real Space 4.0's two `nospec.dds` |
| The game's own | 1 | 5 | The missing `trait_organic`. **+4 new**: the United Nations of Earth start |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| More Events Mod | 1 | 0 | **−1**: the Sadrell spawn notice depends on the galaxy. Its story isn't in this one |
| **Total** | **43** | **46** | |

### The United Nations of Earth start

**The game's own start script runs the nomad setup for the Gundersen
Research Society before that empire has a capital.** The four entries, at
22:11:21:

```
Script Error: Invalid context switch [capital_scope] from Gundersen Research Society [country], common/scripted_effects/01_start_of_game_effects.txt:5000 @ scripted effect nomad_country_initial_setup_effect at file: common/solar_system_initializers/prescripted_species_systems.txt line: 1248
could not get a coordinate from scope.  common/scripted_effects/01_start_of_game_effects.txt:5150 @ ...
could not get a coordinate from scope.  common/scripted_effects/01_start_of_game_effects.txt:5156 @ ...
Script Error: Invalid context switch [capital_scope] from Gundersen Research Society [country], common/scripted_effects/01_start_of_game_effects.txt:5167 @ ...
```

- **It's the game's.** The United Nations of Earth's Sol makes the
  Gundersen Research Society, a nomad empire, with `create_country`. Its
  `effect` calls `nomad_country_initial_setup_effect`. Only after that does
  the script make the Hyacinth arkship and set it as the capital. The effect
  is the game's own, not in the build.
- **Real Space doesn't change it.** The build takes
  `prescripted_species_systems.txt` from Real Space 4.0, which is why the
  log names line 1248, not the game's 1129. The Gundersen block is the same
  in both.
- **It's harmless.** The skipped parts are the shelter upgrade, which the
  arkship's own setup does next, the search for neighbour systems to convert,
  and the clean-up of the capital system's deposits. The Gundersen Research
  Society has its capital in the save.
- **Earlier runs didn't have it** because none played the United Nations of
  Earth.

## The game's Life-Seeded check (21)

**Back to 21: 3 at 22:11:14, as the empire list was shown, and 18 as the
galaxy was made, one per empire.** All are the game's own line in
`00_origins.txt`, about the user's saved Divine Elven Order design, a
Life-Seeded empire. Harmless.

The last report couldn't say why the 18 at galaxy creation went. Three runs
now give the pattern:

| Run | Player's empire | At galaxy creation |
|---|---|---:|
| Pre-upload | Commonwealth of Man | 18 |
| Three mods off | Divine Elven Order | 0 |
| This run | United Nations of Earth | 18 |

The 18 come when Divine Elven Order is a saved design but isn't the empire
being played. The game checks it once for each empire it places. Divine
Elven Order isn't in this galaxy.

## During play

**Nothing in the error log.** Play ran from 22:11:37 to the save at 22:22,
five game years.

**The Gundersen Research Society defaulted on 1 May 2204.** `game.log` has
the game's own log line from its deficit situation:

```
[2204.5.1] Log effect, common/scripted_effects/00_scripted_effects.txt:6256 @ scripted effect country_defaulted_effect at file: events/situation_deficit_events.txt line: 440. AI  in  defaulted as a result of
```

The blanks in the line are the game's: it logs names it can't fill in. The
save has `country_defaulted` on the Gundersen Research Society. Its flags show
void worms attacked it too. The four start entries didn't cause it: the
parts they skipped don't touch its income. An AI nomad running out of money
can happen in the game alone, and Stellar AI changes how AI empires spend.
One default in five years isn't enough to blame either.

## Other changes since the last run

**None.** Today's update check found no game or mod changes since its
baseline. The Cold Steel build is the only change: it now has fix 21.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 23 | The game's United Nations of Earth start logs 4 entries for the Gundersen Research Society | No fix. It's the game's own and harmless |
| 24 | The Gundersen Research Society defaulted in May 2204 | No fix. Watch in longer runs. If AI empires keep defaulting, look at Stellar AI's budgets |
| 21 | Fix 21, Planetary Diversity's Lithoid Budding | In the build and loaded. Still not seen in play: it needs a budding species on a Massive Crater |
| 18 | Trait resources on `planet_pops` | Unchanged. Left to the authors |
| 1 | Still unchecked in play | Fixes 11 and 12 firing, 15's upkeep in the ship designer, 16's fauna in combat, 17's jump, 21's crater bonus, 10's tooltip, 1's megastructures and storms |

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../src/stellaris_patcher/paradox/error_log.py).
- Split the entries by time. Loading lasted until the galaxy was made at
  22:11:19 (`game.log`). Game start lasted to 22:11:21. Play came after
  that. Grouped them by the source in the game's code, then by mod, the same
  way as the last run.
- Checked the build record lists the patch last, and compared its 14 game
  files with the patch folder byte for byte. Ran the builder without
  `--write` to check the patch is current. Read `dlc_load.json` for what the
  game loaded, and Cold Steel's playset for what's switched on.
- Searched the raw log for each name the fixes removed.
- Traced the four nomad entries through the build record to Real Space's
  `prescripted_species_systems.txt`, and compared its Gundersen block with
  the game's. Read the game's `nomad_country_initial_setup_effect`.
- Ran the update check.
- Unpacked the `2205.01.16` save into a scratch folder and read it with
  [script.py](../../src/stellaris_patcher/paradox/script.py). Looked for the
  Surveillance Supercomputer system and every `sealed_system` flag, the
  Gundersen Research Society and its default, Lithoid Budding and the
  `d_lithoid_crater` deposit, Sol and its neighbour systems, and the galaxy
  settings.

## Limits

- **Eleven minutes, five game years.** Longer than the last run in game
  time, still short in play.
- **What happened on screen.** The user saw nothing wrong. Visual problems,
  like the solid background, don't reach the logs.
- **The Life-Seeded pattern rests on three runs.** It fits all three, but it
  wasn't tested on purpose.
- **Why the Gundersen Research Society defaulted** wasn't traced. Its
  budget over the five years isn't in one save.
