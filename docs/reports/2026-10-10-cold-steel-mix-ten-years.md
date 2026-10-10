# Game report: Cold Steel Mix, ten years with Starbase Extended, 10 October 2026

**A new galaxy as a Life-Seeded theocracy, played for ten years, to
2210.03.02. It's the first run with fix 32 shipping Starbase Extended's
files whole (item 35 of the last report), and the longest play with
Starbase Extended 3.0 on. The patch held. Starbase Extended logged only its
descriptor's version: its six `Duplicate trigger` warnings are gone, and the
five Starports built in play logged no attach point, sound or animation
entry. Play logged 3
entries, all one More Events Mod description seen in earlier runs. The user
saw nothing unusual.**

- **Fix 32's whole files work.** The log has no `Duplicate trigger`, and 17 fewer
  override notices: the merged copies that clashed with Starbase Extended's
  own modules and buildings are gone. See [The patch's fixes](#the-patchs-fixes).
- **Ten years of play logged 3 entries**, all at once: a More Events Mod
  specimen description, `mem_holo_projector_desc_short`, names a planet
  through `[From.From.GetName]`, which has nothing to point at outside its
  event. An AI empire found the specimen. Text only. See
  [During play](#during-play-3).
- **Every copy the patch ships is the one the game uses.** Its 68 files in
  the build match our source byte for byte.
- **One small text fix is proposed.** Six More Events Mod specimen
  descriptions show a blank planet name in the Grand Archive. The name can't
  be recovered, so item 36 rewords the six lines without it. See
  [What to do next](#what-to-do-next).

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.10`, with fix 32's whole files in a build for the first time. Its 68 files in the build match our source folder byte for byte |
| Built | The Cold Steel build at 13:25 on the log's clock. The build record has no mismatches |
| Session | Started 13:26:09. New galaxy, seed 1065954418, made at 13:27:27: medium, `spiral_3`, 18 empires, one Fallen Empire, one Marauder, late scaling. Played to `2210.03.02`, saved at 15:03. About 1½ hours of play |
| Empire | Divine Elven Order, a custom empire: fanatic spiritualist and militarist, imperial, Ascensionists and Chosen, Life-Seeded origin, `humanoid_01` ship culture |
| Logs | `error.log`: 6,598 entries. 5,717 resources not installed, 832 override notices and 49 problems: 42 from loading, 4 from the game's Life-Seeded check in the empire designer, 3 from play |

The log's clock is one hour ahead of the file times, as before. The last
entry is at 14:34:07. The half hour of play after it logged nothing.

## Compared with earlier runs

The last run was paused at the start, with fixes 29–34 new.

| Group | Starbase Extended back | This run |
|---|---:|---:|
| Problems while loading and at game start | 49 | 42 |
| The game's Life-Seeded check | 21 | 4 |
| Problems during play | 0 (paused at the start) | 3 (ten years) |
| Override notices | 849 | 832 |

**The problems, by group:**

| Group | Starbase Extended back | This run | Change |
|---|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| The game's own | 1 | 1 | None: the missing `trait_organic` |
| More Events Mod | 1 | 3 | The last run's ship set notice isn't here. Play logged the holo projector's text, 3 entries |
| Starbase Extended 3.0 | 6 | 0 | **−6**: fix 32's whole files silenced the `Duplicate trigger` warnings |
| The game's Life-Seeded check | 21 | 4 | Only the designer's 4. The 18 at galaxy creation come only when Divine Elven Order is saved but not played. This time it was played |
| **Total** | **70** | **49** | |

**The override notices: 17 fewer, from fix 32's whole files.**

| Kind | Starbase Extended back | This run | Change |
|---|---:|---:|---|
| Duplicate objects | 303 | 286 | −17: fix 32's merged copies of 7 modules and 10 buildings are gone |
| Duplicate entities | 480 | 480 | None |
| Duplicate section templates | 23 | 23 | None |
| Duplicate events | 30 | 30 | None |
| Duplicate variables | 12 | 12 | None |
| Real Space's initializer | 1 | 1 | None |
| **Total** | **849** | **832** | **−17** |

## The patch's fixes

**None of the names the fixes removed are in the log.** The raw log has none
of `build_block_radius`, `can_terraform_planet`, `GetAdministratorPluralWithIcon`,
`Malformed token`, `rules_leader_cannot_get_normal_trait`, `MEDIUM_GUN_01`,
`nsc.requires.asteroid`, `mining_manager`, `assembly_line_manufacturing`,
`open_planet`, `design_name`, `amb_aquatic_starbase`, `amb_toxoid_starbase`,
`toxoid_01_ship_light_effect`, `.anim`, `animated mesh`, `attach point`,
`SHIELD_ORBITAL_RING`, `ARMOR_ORBITAL_RING` or `Duplicate trigger`. Its one
`ion_core_effect` is a duplicate entity notice, and its one `solar_system`
is fix 17's initializer notice.

**The game uses every copy the patch ships.** 35 duplicate object notices
name the patch's files:

| Fix | Objects | Notices naming the patch |
|---|---|---:|
| 28 | shrimpAI's Hyper Relay | 1 |
| 29 | Asteroid Mining, Space Foundry, Space Factory | 3 |
| 32 | 2 modules and 8 buildings, from the patch's whole copies of Starbase Extended's files | 10 |
| 34 | 21 starbase sizes | 21 |

The 10 for fix 32 are Starbase Extended's own replacements for the
game's objects. They named Starbase Extended's files before, and name the
patch's copies of those files now. Starbase Extended's notices fell from 50
to 40 for that reason. Two of the 10 are for `disruption_field`, which
Starbase Extended defines twice in its buildings file, at lines 304 and 361.
The two are the same, so it doesn't matter which one wins.

| Fix | In game |
|---|---|
| 32 | **The whole files work.** No `Duplicate trigger`, and the 17 notices of the merged copies are gone |
| 31 | No attach point, sound, particle or animation entries in ten years. The galaxy went from 21 Starports to 26, so five were built in play. No starbase went past Starport, and none was destroyed |
| 11, 12, 26 | The duplicate event notices for `mem_scfe_ziaskehorn.1`, `mem_stuck_in_glacier.22` and `mem_under_blanket.1` and `.2` name More Events Mod's files, so the patch's copies win |
| 17 | The initializer notice names Real Space's file, so the patch's copy wins |
| 18, 19, 27 | Traits log no notice, so the log can't show which copy won |

## Loading (42)

The same 42 as the last run, group for group, less Starbase Extended's six.
Details of each group are in
[run 3](2026-10-03-cold-steel-mix-errors-run-3.md#whats-left-by-mod).

## The game's Life-Seeded check (4)

Four `Invalid context switch [founder_species]` entries at 13:27:09–13:27:15,
before the galaxy was made. They name the player's empire, Divine Elven
Order. The Life-Seeded origin's check at line 2393 of the game's
`00_origins.txt` calls `is_individual_machine`, which asks for
`founder_species`. An empire in the designer has none yet. The game's own,
as the [UNE five years report](2026-10-09-cold-steel-mix-une-five-years.md)
explains. The 18 that usually follow at galaxy creation didn't come. They
come only when Divine Elven Order is a saved design but not the empire
being played, and this time it was played, as in the
[three mods off](2026-10-09-cold-steel-mix-three-mods-off.md) run.

## During play (3)

**More Events Mod's holo projector description.** At 14:34:07, three
entries: `Unknown promotion From` for `From.From.GetName]` and `From.GetName]`,
and `Unknown property GetName` for `GetName]`. The text after them is
"among many others of its kind", the end of `mem_holo_projector_desc_short`
in `mem_specimens_l_english.yml`:

> A holographic projection unit found in orbit of [From.From.GetName] among many others of its kind

The 2210 save has one holo projector, found on 2205.09.02 through
`mem_disguised_planet.3`. An AI empire holds it, in its Grand Archive. The
[new-galaxy report](2026-10-05-cold-steel-mix-new-galaxy.md) logged the same
for `mem_laser_rifle_desc_details`, and the
[long session](2026-10-04-cold-steel-mix-long-session.md) both.

**The planet's name is blank wherever the archive shows it, for every
empire.** A specimen keeps one target, which its text reads as
`EVENT_TARGET_0`. More Events Mod gives its specimens with the event's
`specimen = …` line, and that line keeps the event's own scope, the science
ship. The planet, `FROM.FROM` in the anomaly, isn't kept. The save shows
this: the holo projector keeps object 84, the AI's science ship, whose
scientist belongs to the specimen's owner. The planet it found is planet
3402, now `pc_shielded` with More Events Mod's modifier. The game's own
specimens all read `EVENT_TARGET_0`, never `From`.

**Six of More Events Mod's specimens have this problem.** Five read
`[From.From.GetName]`: the laser rifle, mecha, psionic debris, lichen sample
and holo projector. The datacore reads `[From.From.From.GetName]`. The
military reports read a global event target, which stays set, so they're
fine.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 36 | Six More Events Mod specimen descriptions show a blank planet name in the Grand Archive, and log 3 lines when one is shown. The name can't be recovered from the archive (see [During play](#during-play-3)) | **Done** on 10 October as fix 36 ([decision 52](../decisions.md)). Not yet checked in game. Was: add the six lines to the patch's English `localisation/replace` file, reworded without the name: the holo projector "found in orbit of a disguised planet", the lichen "found on a living asteroid", and so on. Works in existing saves. Rejected: copying the 8 events to give each specimen with `give_specimen = { … targets = { fromfrom } }`, which would keep the name. That's 8 event copies in 5 files to keep in step with More Events Mod, only for specimens found after the change, and untested: dropping the event's `specimen` line may lose its card in the event window |
| 1 | Still unchecked in play | Starbase Extended's: a Citadel's starbase window and its attach points, a starbase's explosion, the aquatic and toxoid sounds (31), a bio-ship empire's hangar bay upkeep and an arkship's buildings (32), the ring shield and armour sections (33), the map icons and Ion Cannon (34), the Asteroid Mining and factory bonuses (29). Earlier: 11 and 12 firing, 15's upkeep, 16's fauna, 17's jump, 19's crater bonus and terraforming, 10's tooltip, 1's megastructures, 18's Unemployment Benefits, 27's AI choice, 28's Nomad Hyper Relay |
| — | This report isn't committed | Commit it |
| — | The Workshop page | At the next upload, add Starbase Extended 3.0 and UI Overhaul Dynamic to its **Required items**, and ask their authors' permission for fixes 29–34 |

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../src/stellaris_patcher/paradox/error_log.py), and
  split it into resources not installed, override notices and problems, as
  the last report did.
- Split the entries by time. The galaxy was made at 13:27:27 (`game.log`).
  Loading ends at 13:26:59 and the designer's entries at 13:27:15. Nothing
  came at game start. The only play entries are at 14:34:07.
- Read `dlc_load.json` for what the game loaded, and the build record for
  its 27 mods and the files each one gives.
- Compared the patch's 68 files in the built mod with the patch folder byte
  for byte.
- Searched the raw log for each name the fixes removed.
- Grouped the duplicate object notices by the mod whose file the game uses.
- Matched the play entries' text against the build's localisation.
- Unpacked the `2200.02.02` and `2210.03.02` saves into a scratch folder and
  read them: the player's empire and galaxy settings, the starbases by level
  in each, and the holo projector's owner and date.

## Limits

- **What happened on screen.** The user saw nothing unusual, but didn't say
  which windows they opened. Visual problems don't reach the logs.
- **No starbase past Starport** was built, and none was destroyed. Attach
  points on a Starhold, Star Fortress, Citadel or orbital ring weren't
  reached.
- **One galaxy, one empire.** The bio-ship, arkship, Nomad, Megacorp and
  lithoid cases the fixes cover didn't come up.
