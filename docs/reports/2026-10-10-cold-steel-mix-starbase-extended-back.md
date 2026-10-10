# Game report: Cold Steel Mix with Starbase Extended back on, 10 October 2026

**A new galaxy as a psionic empire, looked at for about three minutes on
1 January 2200, without unpausing. It's the first run with Starbase Extended
3.0 back on and fixes 29–34 in the build. The patch held. Starbase Extended,
which logged 47 problems each run before, now logs 7: its descriptor's
version and six parse warnings from its own module file, whose objects the
patch replaces. Play logged nothing. The user looked at the starbase window,
and everything worked.**

- **Fix 30 works in game.** The starbase window showed every module and
  building slot, and Upgrade sat away from Dismantle. Nothing looked wrong.
- **Fix 31's models load cleanly.** The galaxy started with 21 Starports in
  12 ship cultures, ten of them on meshes that lack attach points Starbase
  Extended's sizes ask for. Fix 31 adds them, copying the game's psionic and
  infernal models to do so. The log has no attach point, sound,
  particle or animation entry at all. See [The patch's fixes](#the-patchs-fixes).
- **Every copy the patch ships is the one the game uses.** The game's
  duplicate notices name the patch's file for all 42 objects it copies. Its
  67 files in the build match our source byte for byte.
- **Six of Starbase Extended's old problems stay in the log, harmlessly.**
  The game still reads its module files and logs their duplicate
  `potential` blocks, though fix 32's merged copies replace those modules. A
  fix could ship the two files whole instead, as fix 31 does for its models.
  See [Starbase Extended](#starbase-extended-7).
- **Override notices tripled, to 849, all from Starbase Extended and the
  patch's copies of it.** They're notices, not problems.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. Starbase Extended 3.0 and shrimpAI are both back on. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.10`, with all 25 fixes. Fixes 2, 3, 18, 26–34 are in a build for the first time. Its 67 files in the build match our source folder byte for byte |
| Built | The Cold Steel build at 10:41 on the log's clock, a minute after the patch was written. The build record has no mismatches |
| Session | Started 10:42:32. New galaxy, seed 319144729, made at 10:45:54: medium, `spiral_3`, 18 empires, one Fallen Empire, one Marauder, 586 systems. Saved at 10:49, still on `2200.01.01`. The user looked at the starbase window and didn't unpause |
| Empire | Oracularity of Noerm, the `EMPIRE_DESIGN_tankbound` premade, with the `psionic_01` ship culture |
| Logs | `error.log`: 6,636 entries. 5,717 resources not installed, 849 override notices and 70 problems: 49 from loading and game start, 21 from the game's Life-Seeded check, none from play |

The log's clock is one hour ahead of the file times, as before.

## Compared with earlier runs

The last run had Starbase Extended and shrimpAI switched off.

| Group | Ascension Worlds back | This run |
|---|---:|---:|
| Problems while loading and at game start | 43 | 49 |
| The game's Life-Seeded check | 21 | 21 |
| Problems during play | 1 (4 minutes, 2 years) | 0 (paused at the start) |
| Override notices | 281 | 849 |

**The problems, by group:**

| Group | Ascension Worlds back | This run | Change |
|---|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None. Starbase Extended's `v4.**.*` is one of the 4 descriptor lines again |
| The game's own | 1 | 1 | None: the missing `trait_organic` |
| More Events Mod | 1 | 1 | The Lost Emperor's failure to place its system isn't in this log. In its place, an empire switched to More Events Mod's `mem_ancient_01` ship set, a notice seen in run 3 |
| Starbase Extended 3.0 | off | 6 | **+6**, against 47 when it was last on. See [Starbase Extended](#starbase-extended-7) |
| **Total** | **43** | **49** | |

**The override notices: 568 more, from Starbase Extended and the patch.**

| Kind | Ascension Worlds back | This run | Change |
|---|---:|---:|---|
| Duplicate objects | 210 | 303 | +93: 50 objects of Starbase Extended's that replace the game's, 42 of the patch's copies, and shrimpAI's Hyper Relay |
| Duplicate entities | 30 | 480 | +450: the starbase models in the patch's 20 model files, which fix 31 writes at Starbase Extended's paths and in its attach point file |
| Duplicate section templates | 0 | 23 | +23: Starbase Extended's copies of the game's starbase and orbital ring sections |
| Duplicate events | 28 | 30 | +2: fix 26's `mem_under_blanket.1` and `.2`, naming More Events Mod's file, as [Check in game](../patches/cold-steel-mix.md#check-in-game) expects |
| Duplicate variables | 12 | 12 | None |
| Real Space's initializer | 1 | 1 | None |
| **Total** | **281** | **849** | **+568** |

## The patch's fixes

**None of the names the fixes removed are in the log.** The raw log has none
of the names earlier reports checked, from `build_block_radius` to
`can_terraform_planet`, and none of Starbase Extended's: `MEDIUM_GUN_01`,
`nsc.requires.asteroid`, `mining_manager`, `assembly_line_manufacturing`,
`open_planet`, `design_name`, `amb_aquatic_starbase`, `amb_toxoid_starbase`,
`toxoid_01_ship_light_effect`, `.anim`, `animated mesh`, `attach point`,
`SHIELD_ORBITAL_RING` or `ARMOR_ORBITAL_RING`. Its one `ion_core_effect` is a
duplicate entity notice, and its one `solar_system` is fix 17's initializer
notice.

**The game uses every copy the patch ships.** When two files define one
object, the game logs which one it uses. Each of these names the patch's
file:

| Fix | Objects | Notices naming the patch |
|---|---|---:|
| 28 | shrimpAI's Hyper Relay | 1 |
| 29 | Asteroid Mining, Space Foundry, Space Factory | 3 |
| 32 | 7 modules and 10 buildings | 17 |
| 34 | 21 starbase sizes | 21 |

| Fix | In game |
|---|---|
| 2, 3, 7 | Starbase Extended's names are gone from the log |
| 29 | The 5 missing buildings are gone from the log |
| 30 | **Seen.** Every slot shows, Upgrade is away from Dismantle, and nothing looked wrong. The log has no `open_planet` or `design_name` |
| 31 | No attach point entries from 21 Starports in 12 cultures: avian, mammalian, lithoid, synthetics, infernal, psionic, arthropoid, fungoid, aquatic, reptilian, molluscoid and toxoid. Ten of them have a Starport mesh that lacks some of `part4`–`part7`, which fix 31 adds. Earlier runs logged Starbase Extended's attach points at game start. No sound, particle or animation entries, with 3 synthetic and 1 each of aquatic and toxoid Starports in the galaxy. No starbase was destroyed, so the explosions weren't seen |
| 32 | The copies are used. The 6 duplicate-block warnings stay, from Starbase Extended's own file. No arkship or bio-ship hangar bay was looked at |
| 33 | The 2 missing section entries are gone |
| 34 | The copies are used. Map icons and the Ion Cannon weren't looked at |
| 26 | Its two duplicate event notices name More Events Mod's file, so the patch's copies win |
| 18, 27 | Traits log no notice, so the log can't show which copy won |

## Loading

**49 entries.** 43 match the last run group for group, and 6 are Starbase
Extended's.

### Starbase Extended (7)

- **Its descriptor's `supported_version="v4.**.*"`** (1, counted with the
  descriptors). Harmless, as in every run.
- **Six `Duplicate trigger` entries**, at lines 101, 144 and 433 of
  `sbx_3_0_orbital_ring_modules.txt` and 183, 238 and 290 of
  `sbx_3_0_starbase_modules.txt`. They're the six modules with two
  `potential` blocks. The game reads Starbase Extended's files and logs the
  duplicates as it parses them, then uses fix 32's merged copies, as its
  notices show. **Harmless.** Shipping the two files whole, at Starbase
  Extended's paths, would silence them: see [What to do next](#what-to-do-next).

The other 40 of its 47 old problems are gone: the missing buildings, the
`category` trigger, the orbital ring sections, the starbase window items,
the sounds and particles, the animations and the attach points.

## The game's Life-Seeded check (21)

Unchanged: `is_individual_machine` asks the Fallen Empire for
`founder_species`, which it has none of. The game's own, as the
[UNE five years report](2026-10-09-cold-steel-mix-une-five-years.md) explains.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 35 | Starbase Extended's two module files still log 6 `Duplicate trigger` warnings, though fix 32's copies replace the six modules | **Done** on 10 October: fix 32 now ships both module files whole, at their own paths, and its buildings file too, so it works one way ([decision 49](../decisions.md)). Not yet checked in game. Was: change fix 32 to ship the two module files whole, as fix 31 does for the model files. Optional: the warnings are harmless |
| 1 | Still unchecked in play | Starbase Extended's: a starbase's explosion and the aquatic and toxoid sounds (31), sections on the new attach points on a Starport (31), a bio-ship empire's hangar bay upkeep and an arkship's buildings (32), the ring shield and armour sections (33), the map icons and Ion Cannon (34), the Asteroid Mining and factory bonuses (29). Earlier: 11 and 12 firing, 15's upkeep, 16's fauna, 17's jump, 19's crater bonus and terraforming, 10's tooltip, 1's megastructures, 18's Unemployment Benefits, 27's AI choice, 28's Nomad Hyper Relay |
| — | Fixes 29–34 aren't committed | Commit them, with this report |
| — | The Workshop page | At the next upload, add Starbase Extended 3.0 and UI Overhaul Dynamic to its **Required items**, and ask their authors' permission for fixes 29–34 |

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../src/stellaris_patcher/paradox/error_log.py), and
  split it into resources not installed, override notices and problems, as
  the last report did.
- Split the entries by time. The galaxy was made at 10:45:54 (`game.log`).
  The game start entries end at 10:45:58. Nothing came after.
- Read `dlc_load.json` for what the game loaded, and the build record for
  its 27 mods and the files each one gives.
- Compared the patch's 67 files in the built mod with the patch folder byte
  for byte.
- Searched the raw log for each name the fixes removed.
- Read the game's `Object with key … already exists, using the one at`
  notices for every object the patch copies.
- Grouped the override notices by kind, and matched the duplicate entities
  against the names in Starbase Extended's and the patch's model files.
- Unpacked the `2200.01.01` save into a scratch folder and read it with
  [script.py](../../src/stellaris_patcher/paradox/script.py): the player's
  empire and ship culture, the galaxy settings, and each Starport's station
  and its ship culture.

## Limits

- **No play.** The game stayed paused at the start. The entries that come
  in play, or when a starbase is upgraded, built or destroyed, weren't
  reached. Run 3 logged Starbase Extended's attach points at game start and
  during play.
- **What happened on screen.** The user looked at the starbase window only.
  Visual problems don't reach the logs.
- **Attach points on a Citadel or orbital ring** weren't tested: the galaxy
  starts with Starports.
