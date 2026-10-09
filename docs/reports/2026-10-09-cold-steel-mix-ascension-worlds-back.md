# Game report: Cold Steel Mix with Ascension Worlds back on, 9 October 2026

**A new galaxy as the United Nations of Earth, played two game years in
about four minutes, to 1 February 2202. It's the first run with Planetary
Diversity - Ascension Worlds switched back on, and with fix 25 in the build.
The patch held, and the user saw nothing wrong. Switching Ascension Worlds
back on added no problems, only 51 override notices. Play logged one entry,
More Events Mod's. It's harmless, but it's a real bug, and fix 26 now
mends it.**

- **The patch was loaded and its fixes held.** The build lists it last, and
  its 34 game files match our source byte for byte. That includes fix 19's
  Lithoid Budding, now from Ascension Worlds again, its terraforming rule, and
  fix 25's 19 translation files. None of the names the fixes removed is in
  the log. See [The patch's fixes](#the-patchs-fixes).
- **Ascension Worlds logged no problems.** It brought back 51 override
  notices: 45 duplicate objects, 5 duplicate events and 1 duplicate variable.
  See [Compared with earlier runs](#compared-with-earlier-runs).
- **New, during play: More Events Mod's Under the Blanket story tried to give
  a Fallen Empire's heir a trait the game doesn't allow.** The game refused
  Substance Abuser, because an autocracy's heir can't take normal leader
  traits. Harmless, and mended by fix 26. See [During play](#during-play).
- **Back: More Events Mod's Lost Emperor story couldn't place its system.**
  It's item 20, already
  [left to the author](../patches/cold-steel-mix.md#left-to-the-authors).
- **The United Nations of Earth start logged nothing this time.** Its 4
  entries in the last run came from Real Space's Vela system, not from Sol,
  and this galaxy has no Vela. See [Loading](#loading).

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 25 mods with `Cold Steel Mix patch` last. Planetary Diversity - Ascension Worlds is back on. Starbase Extended 3.0 and shrimpAI are still switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.09`, with fixes 1, 4–7, 10–12, 15–17, 19 and 25. Fix 19 copies Ascension Worlds' Lithoid Budding again, and has its terraforming half back. Fixes 2 and 3 are left out: their mod is off. Its 34 game files in the build match our source folder byte for byte. A dry run of the builder today writes the same 34 files |
| Built | The Cold Steel build at 23:23 on the log's clock. The build record has no mismatches |
| Session | Started 23:44:46. New galaxy, seed 1288013849, made at 23:45:48: medium, `spiral_3`, 18 empires, one Fallen Empire, 589 systems. Played from `2200.01.01` to `2202.02.01`, about four minutes. Saved at 23:50. No sign of a crash |
| Empire | United Nations of Earth, in Sol (`sol_system_initializer`) |
| Logs | `error.log`: 6,063 entries. 5,717 resources not installed and 281 override notices. 65 problems: 43 from loading and game start, 21 from the game's Life-Seeded check, 1 from play. `game.log`: event picks and the Lost Emperor's log line |

The log's clock is one hour ahead of the file times, as before. The main
menu loaded at 23:45:35, and the galaxy was made 13 seconds later, so the
empire was picked from the list. The error log's game start entries end at
23:46:02. The first event pick is at 23:46:11, and `game.log` runs to
23:50:14.

## Compared with earlier runs

The pre-upload run is the last one with Ascension Worlds on. It had
Starbase Extended on too, which logged 47 problems.

| Group | Pre-upload | UNE five years | This run |
|---|---:|---:|---:|
| Problems while loading and at game start | 91 | 46 | 43 |
| The game's Life-Seeded check | 21 | 21 | 21 |
| Problems during play | 0 (7 minutes, 3 years) | 0 (11 minutes, 5 years) | 1 (4 minutes, 2 years) |
| Override notices | 755 | 230 | 281 |

**The override notices: 51 more, all from Ascension Worlds.**

| Kind | UNE five years | This run | Change |
|---|---:|---:|---|
| Duplicate objects | 165 | 210 | +45. 46 of the 210 are keys Ascension Worlds defines |
| Duplicate entities | 30 | 30 | None |
| Duplicate events | 23 | 28 | +5: Ascension Worlds' copies of `toxoids.1`, `ancrel.2025`, `aquatics.1005`, `crisis.7225` and `planet_destruction.700` |
| Duplicate variables | 11 | 12 | +1: More Events Mod's `has_planetary_diversity_ascension_worlds`, which Ascension Worlds now defines first |
| Real Space's initializer | 1 | 1 | None |
| **Total** | **230** | **281** | **+51** |

## The patch's fixes

**None of the names the fixes removed are in the log.** The raw log has no
`build_block_radius`, `starbase_formation_priority`, `sol_neighbor`,
`is_pd_planet_for_aqua_trait`, `starlit`, `voidspawn`, `rs_d_dark_matter`,
`fire_rate_reduction`, `hp_increased`, `PLANET_SCALE_SYSTEM`, `ZOOM_STEPS`,
`GetAdministratorPluralWithIcon`, `mod_planet_bureaucrats`, `t7_upkeep`,
`Malformed`, `lithoid_budding` or `can_terraform_planet`. No entry names a
patch file or a `planetarydiversity` translation file.

| Fix | What the log or save shows | In play |
|---|---|---|
| 11, 12 | Both duplicate event notices name More Events Mod's file, as before. The patch's events win | Not fired. Neither event can before year 20 |
| 15 | No `Malformed token` for `@shield_*_t7_upkeep_*` | Not checked in the save |
| 16 | Not logged. The build takes `mutation_weapon_components.csv` from the patch | Not checked in the save |
| 17 | The initializer notice names Real Space's `special_system_initializers.txt` at line 2079. The patch's `!!_` file was read first | This galaxy has no Surveillance Supercomputer system. The one `sealed_system` flag is on Distant Stars' `distar_sealed_1_2`, Thirimora, where it belongs |
| 19 | The build has the patch's `!!_` traits file, with Ascension Worlds' `trait_lithoid_budding`, and its `zz_` terraforming rule | Not seen. No species has Lithoid Budding. The galaxy has one Massive Crater (`d_lithoid_crater`) |
| 25 | The build has the patch's 19 translation files, with 22 lines mended | Not in play. The game is in English and reads only English text. Earlier runs never logged these lines either: Cold Steel's health check is the check, and it passes |
| 2, 3 | Left out. Their mod is switched off | |

## Loading

**43 entries. All 43 match earlier runs group for group.**

| Group | UNE five years | This run | Change |
|---|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None: System Scale's 6 infernal ring world textures, Real Space 4.0's two `nospec.dds` |
| The game's own | 5 | 1 | The missing `trait_organic`. **−4**: no Gundersen Research Society in this galaxy. See below |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| More Events Mod | 0 | 1 | **+1**: the Lost Emperor spawn, item 20, last seen in the pre-upload run |
| **Total** | **46** | **43** | |

**The Gundersen Research Society comes from Vela, not Sol.** The last
report said Sol makes it. The block is in Real Space's
`prescripted_species_systems.txt`, but under `une_vela_system`. That system
isn't in this galaxy, so its 4 entries aren't either. The last report's
finding stands otherwise: the entries are the game's own and harmless.

**The Lost Emperor story couldn't place its system, as in the
[pre-upload run](2026-10-07-cold-steel-mix-pre-upload.md#more-events-mod-2).**
At 23:46:02, `test_spawn_neochadamus` logged:

```
spawn_system: found no possible system for the new system to connect with around  common/scripted_effects/mem_descended_scripted_effects.txt:28 @ scripted effect test_spawn_neochadamus at file: events/mem_lost_emperor.txt line: 65
```

The save has the global flag `mem_system_spawned` and no
`mem_descended_system`, so the story never starts. `game.log`'s "spawned
Thirimora" names the last system made before it, Distant Stars' sealed
system, as the pre-upload run found. It's item 20, already left to the author.

## The game's Life-Seeded check (21)

**21 again: 3 at 23:45:39, as the empire list was shown, and 18 as the
galaxy was made, one per empire.** All are the game's own line in
`00_origins.txt`, about the user's saved Divine Elven Order design. Harmless.

The pattern from the last report holds for a fourth run:

| Run | Player's empire | At galaxy creation |
|---|---|---:|
| Pre-upload | Commonwealth of Man | 18 |
| Three mods off | Divine Elven Order | 0 |
| UNE five years | United Nations of Earth | 18 |
| This run | United Nations of Earth | 18 |

## During play

**One entry, at 23:49:41: More Events Mod's Under the Blanket story tried
to give a Fallen Empire's heir Substance Abuser.**

```
Unable to add trait for [reason] rules_leader_cannot_get_normal_trait [at]  file: events/mem_under_blanket.txt line: 657
```

- **What happened.** The story fires on a colony's first birthday
  (`on_colony_1_year_old`). It fired on 1 January 2201 for Boundary, a
  Planetary Diversity cold Gaia world the Ytrellan Fallen Empire has held
  since the start. Of empires, its trigger leaves out only homicidal ones.
- **It picked the empire's heir.** The story takes a scientist, any one for
  an empire that isn't a gestalt. In the save, the leader with
  `mem_under_blanket_selected_leader` is a scientist with
  `trait_imperial_heir`, and the Fallen Empire's government names him heir.
  It's an imperial autocracy.
- **The game refused one trait.** Event `mem_under_blanket.10` adds
  Substance Abuser, then Paranoid. The game's rule `can_leader_get_normal_trait`
  refuses normal traits to an autocracy's ruler or heir. Substance Abuser is
  one. Paranoid is a council trait, which the rule doesn't cover, so the heir
  got it.
- **It's More Events Mod's own.** The rule is the game's, and the trait, the
  rule and its trigger all come from the game in the build. More Events
  Mod's event is the same file as on the Workshop. No other mod touches it.
- **It's harmless here, but it reaches the player too.** The heir misses one
  negative trait. Two other endings give Archaeologist or Adaptable, both
  normal traits, so a player's ruler or heir would miss a reward.
- **Fix 26 mends it, and keeps Fallen Empires out of the story**
  ([decision 40](../decisions.md)). Its scientist picks now call the game's
  `can_leader_get_normal_trait_trigger`, and it starts only for normal
  empires. The game's Strange Worlds colony events check the same.
- **Earlier runs didn't have it.** The story is a small roll on each
  colony's first birthday, and this outcome event is one of several.

## Other changes since the last run

**Only Ascension Worlds.** Today's update check found no game file changes.
It lists Ascension Worlds as new, because the last accept was made while it
was off, and 15 of its copies of game files as unreviewed. The
[first 4.5.2 run](2026-10-07-cold-steel-mix-4.5.2-first-run.md) read them
all on 7 October, and Ascension Worlds hasn't updated since 22 September:

| Copies | What they are |
|---|---|
| `trait_lithoid_budding`, `can_terraform_planet` | Fix 19 |
| 7 traits, among them `trait_cybernetic` and the lithoid and plantoid ones | `planet_pops`, not 4.5.2's `planet_pops_traits`. Item 18, left to the authors |
| `trait_psionic`, `trait_latent_psionic`, `trait_survivor`, `trait_resilient`, `flooded_habitat`, `crisis.7225`, `toxoids.1` | Ascension Worlds' own work: an inline script, its own planet classes, its own flooded world modifier, a shrouded planet event and a line moved. Nothing of the game's is missing |

The check was accepted after this report, so the next one skips these
([decision 30](../decisions.md)).

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 26 | More Events Mod's Under the Blanket story can pick an autocracy's ruler or heir, and the game then refuses Substance Abuser, Archaeologist or Adaptable. It also starts for Fallen Empires | **Done** on 9 October, with the Fallen Empire check ([patch](../patches/cold-steel-mix.md#what-each-fix-does), [decision 40](../decisions.md)). Not yet checked in game. Was: No fix. It's More Events Mod's own and harmless |
| 20 | More Events Mod's Lost Emperor story can fail to place its system | Unchanged. Left to the author |
| 23 | The game's United Nations of Earth start logs 4 entries for the Gundersen Research Society | Unchanged, no fix. The [last report](2026-10-09-cold-steel-mix-une-five-years.md#the-united-nations-of-earth-start) names Sol as its source. It's Vela (`une_vela_system`) |
| 1 | Still unchecked in play | Fixes 11 and 12 firing, 15's upkeep in the ship designer, 16's fauna in combat, 17's jump, 19's crater bonus and terraforming, 10's tooltip, 1's megastructures and storms. Fix 25 needs a game in German, Russian, Polish, Japanese, Korean or one of Ascension Worlds' languages |

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../src/stellaris_patcher/paradox/error_log.py).
- Split the entries by time. Loading lasted until the galaxy was made at
  23:45:48 (`game.log`). Game start lasted to 23:46:02. Play came after
  that. Grouped them by the source in the game's code, then by mod, the same
  way as the last run.
- Checked the build record lists the patch last, and compared its 34 game
  files with the patch folder byte for byte. Ran the builder without
  `--write` to check the patch is current. Read `dlc_load.json` for what the
  game loaded.
- Searched the raw log for each name the fixes removed, and for fix 25's
  file names and keys.
- Traced each duplicate event id to the mod file that defines it, and each
  duplicate object key against Ascension Worlds' files.
- Traced the play entry through the build record to More Events Mod's
  `mem_under_blanket.txt`, compared it with the Workshop copy, and read the
  game's `can_leader_get_normal_trait` rule and its trigger, and the two
  traits.
- Traced the Gundersen block in Real Space's `prescripted_species_systems.txt`
  to its initializer.
- Ran the update check, and read Ascension Worlds' 15 diffs.
- Unpacked the `2202.02.01` save into a scratch folder and read it with
  [script.py](../../src/stellaris_patcher/paradox/script.py). Looked for the
  story's flags, its leader and the Fallen Empire's government, the planet
  it fired on, every `sealed_system` flag, the Lost Emperor's flags, Lithoid
  Budding and the `d_lithoid_crater` deposit, the Gundersen Research Society,
  and the galaxy settings.

## Limits

- **Four minutes, two game years.** The shortest play of recent runs.
- **What happened on screen.** The user saw nothing wrong. Visual problems,
  like the solid background, don't reach the logs.
- **Whether the leader was heir at the moment of the refusal** wasn't traced.
  The story exiles him and brings him back. He's heir in the save, a year
  later, and the rule's reason fits.
- **Why this galaxy has no Vela** wasn't looked into.
