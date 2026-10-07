# Game report: Cold Steel Mix build, first run on 4.5.2, 7 October 2026

**A new Sol start, played for about four minutes, to 26 January 2201. The
patch was in the game and held. Play logged nothing, and the user saw
nothing wrong.** This is the first run on 4.5.2 and the first with fixes 11
and 12. The report also checks the 4.5, 4.5.1 and 4.5.2 patch notes against
the 24 mods that haven't updated since 4.5.2.

- **The patch was rebuilt and was loaded.** It was relinked at 17:18 and
  Cold Steel rebuilt the playset at 17:20, after this afternoon's
  [update check](2026-10-07-cold-steel-mix-4.5.2-update.md) found it
  missing. The build lists it last, and its 12 files match our source byte
  for byte. See [The run](#the-run).
- **Fixes 11 and 12 win.** The game logged both duplicate event ids against
  More Events Mod's file. That means the patch's copies were read first and
  are the ones in use. See [The patch's fixes](#the-patchs-fixes).
- **One new patch candidate, from 4.5.2: More Events Mod's three Progenitor
  shields lose their upkeep.** 4.5.2 renamed the game's shield upkeep
  variables. More Events Mod still uses the old names, which nothing defines
  now. See [More Events Mod](#more-events-mod-6-new).
- **Everything else in loading matches the 5 October run exactly**, group
  for group. See [Loading](#loading).
- **The patch notes show six more places where an older mod copy undoes a
  game fix. None of them logs an error.** The two that matter most: Ships in
  Scaling's Large Mega Bombard still has a range of 2, and Planetary
  Diversity's trait copies bring back a 4.5.2 bug that made two modifiers
  stack once per trait. See
  [The patch notes against older mods](#the-patch-notes-against-older-mods).

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, with fixes 1–7 and 10–12. Its 12 files in the build match our source folder byte for byte |
| Built | Our patch at 17:18 local time, the Cold Steel build at 17:20. The build record has no mismatches. Cold Steel's own conflict choices are still empty, so the build has no Cold Steel patch mod |
| Session | Started 17:20. New galaxy, seed 1548261237, made at 17:21:46. Played to `2201.01.26`, about four minutes. Saved at 17:26. No sign of a crash |
| Empire | United Nations of Earth, a Sol start |
| Logs | `error.log`: 6,588 entries. 5,717 resources not installed and 754 override notices. 117 problems: 96 from loading and game start, 21 from the game's Life-Seeded check, none from play. `game.log`: event picks only |

The log's clock is local time, one hour ahead of the file times. The error
log's last entry is at 17:22:03, 17 seconds after the galaxy was made.
`game.log` runs to 17:25:48.

The override notices are run 5's 752 plus the two duplicate events from
fixes 11 and 12.

## Compared with earlier runs

| Group | Run 4 | Run 5 (new galaxy) | This run |
|---|---:|---:|---:|
| Problems while loading and at game start | 96 | 89 | 96 |
| The game's Life-Seeded check | 4 | 36 | 21 |
| Problems during play | 0 (3 minutes) | 24 (3.5 hours, 25 years) | 0 (4 minutes, 26 days) |

Run 4 counted its 4 Life-Seeded entries with loading. Run 5 counted them
under the empire designer.

## The patch's fixes

**None of the names the fixes removed are in the log.** The raw log has no
`MEDIUM_GUN_01*`, `build_block_radius`, `starbase_formation_priority`,
`sol_neighbor`, `is_pd_planet_for_aqua_trait`, `starlit`, `voidspawn`,
`rs_d_dark_matter`, `fire_rate_reduction`, `hp_increased`, `nsc.requires`,
`PLANET_SCALE_SYSTEM`, `ZOOM_STEPS`, `GetAdministratorPluralWithIcon` or
`mod_planet_bureaucrats`. No entry names a patch file.

**Fixes 11 and 12 are in force.** The game logged:

```
an event with id [mem_scfe_ziaskehorn.1] already exists!  file: events/mem_asp_scfe_events.txt line: 12016
an event with id [mem_stuck_in_glacier.22] already exists!  file: events/mem_stuck_in_glacier.txt line: 480
```

Both lines name More Events Mod's copy, at the line where each event starts.
The game keeps the first copy it reads and skips the later one. So the
patch's `!!_` files were read first, and their events are the ones in use.
These two notices are expected, and will be in every run.
[cold-steel-mix.md](../patches/cold-steel-mix.md#check-in-game) says the log
should have no new entry about the duplicate ids. That line is wrong, and
item 2 below corrects it.

Not yet tested in play:

- **Fixes 11 and 12 firing.** The Ziaskehorn roll needs year 20. The save
  has no `discovered_ziaskehorn` flag.
- **Fix 5's systems.** This was a Sol start, but the plain one: the game
  made Sol with `sol_system_initializer` and Real Space's own neighbours
  (`alpha_centauri_mediumsector_no_col`, `sirius_mediumsector_no_col`,
  `procyon_mediumsector`, `tau_ceti_mediumsector`). Only Planetary
  Diversity's and More Events Mod's special starts use the patch's
  `sol_neighbor_*` copies. The load is clean, as in run 4.
- **Fixes 1, 4 and 10**, for the same reasons as in run 5.

## Loading

**96 entries. 89 match run 5 group for group. The other 7 are More Events
Mod's.**

| Group | Run 5 | This run | Change |
|---|---:|---:|---|
| Starbase Extended 3.0 | 47 | 47 | None. 3 of them come at game start, as before |
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| The game's own | 1 | 1 | The missing `trait_organic` |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| More Events Mod | 0 | 7 | **+6 new** from 4.5.2, and 1 notice that depends on the galaxy |
| **Total** | **89** | **96** | |

### More Events Mod (6 new)

**More Events Mod's three Progenitor shields have no upkeep the game can
read.** `common/component_templates/mem_lex_utilities.txt` (lines 334–335,
366–367 and 398–399) sets the upkeep of `mem_PROGENITOR_SHIELD_L`, `_M` and
`_S` with `@shield_l_t7_upkeep_energy`, `@shield_l_t7_upkeep_alloys` and the
same for `m` and `s`. Nothing defines those six names. The game logs each as
a "Malformed token" and can't read the value, so most likely those shields
cost nothing to run.

The cause is 4.5.2. Its notes say: "Shield upkeep scripted variables are
renamed to the shared `@defense_<size>_t<N>_upkeep_*` family." The game's
`02_scripted_variables_component_cost.txt` changed on 6 October, and its own
psi shield uses the new names. More Events Mod's file hasn't changed since
August, and run 5 on 4.5.1 logged none of this.

The update check listed the same six as variables nothing defines. It
couldn't call them removed names, because its baseline was already 4.5.2.

It matters only once an empire researches `tech_mem_lex_shield`. The game's
values are:

| Size | Energy | Alloys |
|---|---:|---:|
| Large (`@defense_l_t7_…`) | 1.52 | 0.456 |
| Medium (`@defense_m_t7_…`) | 0.76 | 0.228 |
| Small (`@defense_s_t7_…`) | 0.38 | 0.114 |

### The one notice

An empire switched to More Events Mod's ship set `mem_ancient_01` at game
start, which resets its ship designs. Run 3 had the same notice. It isn't an
error.

## The game's Life-Seeded check (21)

**All 21 are the same line of the game's own script, as in run 5.** The
game's Life-Seeded origin, now at line 2393 of
`common/governments/civics/00_origins.txt` after 4.5.2 moved it from 2383,
checks `is_individual_machine`, which asks for `founder_species`. 3 came in
the empire designer at 17:21:41. 18 came as the galaxy was made, one per
empire. No mod replaces either file. Harmless.

## During play

**Nothing.** Play ran from 17:22:03 to about 17:26 and logged no entries.
Four minutes is too short to say more. Run 5 averaged about one entry per
game year.

## The patch notes against older mods

**24 of the 26 mods last updated before 4.5.2. Each was checked against the
notes of every release since its own update.** No mod uses a name the notes
removed, except More Events Mod's shield variables above. Six mod copies
undo a fix the notes describe. None of them logs an error.

| Last updated | Mods | Checked against |
|---|---|---|
| Before 4.5 (22 September) | Universal Resource Patch, both UI Overhaul Dynamic add-ons, Starbase Extended 3.0, Just Star Names, Cinematic Camera, The Galaxy Is Flat, Realistic Asteroids, Extended Soundtrack | 4.5, 4.5.1, 4.5.2 |
| 4.5 to 4.5.1 | The 7 Planetary Diversity mods, More Events Mod, shrimpAI | 4.5.1, 4.5.2 |
| 4.5.1 to 4.5.2 | Real Space 4.0, Ships in Scaling, System Scale, Diverse Rooms, Apocryphos, Kammarheit | 4.5.2 |

Only Stellar AI and UI Overhaul Dynamic updated for 4.5.2. The dates are
Steam's update times. Some mods' file times are later than that, because
Steam rewrote their files without a new version.

### Mod copies that undo a fix

| # | Mod | What it undoes | Note it undoes | Effect |
|---|---|---|---|---|
| A | Real Space - Ships in Scaling | Its whole copy of `mutation_weapon_components.csv`, from 25 September, gives `MEGA_BOMBARD_LARGE` a range of 2. Ships in Scaling divides ranges by about 6. The game's row is now 100, so it should be 17, as its Giga Bombard Large is | 4.5.2: "The Large Mega Bombard mutation now has the correct range and fires in combat" | Space fauna with that mutation most likely still can't hit anything |
| B | Planetary Diversity, Ascension Worlds, More Events Mod | 12 of the game's traits, copied by Planetary Diversity and Ascension Worlds, put their resources under `planet_pops`, not 4.5.2's hidden `planet_pops_traits`. They include `trait_organic`, `trait_lithoid`, `trait_mechanical` and `trait_machine_unit`, so almost every species has one. More Events Mod's six own Ancestors' Grudge traits do the same | 4.5.2: "The Shroud-Warped leader trait and the Unemployment Benefits modifier no longer scale with the number of traits a species has" | An `_add` modifier on `planet_pops` applies once per trait table again. Two in the game: Unemployment Benefits (+2 consumer goods per unemployed pop, Megacorp) and Shroud-Warped's psionic unity (+0.5 or +0.25). Each is doubled or more |
| C | Real Space 4.0 | Its whole copy of `special_system_initializers.txt` still gives the Surveillance Supercomputer system the `sealed_system` flag | 4.5.2: "Fleets with a jump drive can now enter the Surveillance Supercomputer system" | Jump drive fleets still can't enter it |
| D | Planetary Diversity - Ascension Worlds | Its `trait_lithoid_budding` lacks `divide_over_pop_groups = no` on the Massive Crater bonus | 4.5.2: "Crystallization now gives its full bonus on a Massive Crater" | The crater's budding bonus is split over the planet's pop groups again |
| E | Planetary Diversity - Ascension Worlds | Its `can_terraform_planet` rule lacks the game's checks for a consecrated world and for a Knights detox in progress. It drops the legendary leader check on purpose, and says so in a comment | 4.5: Consecrate World. 4.5.2: Knights of the Toxic God can detoxify worlds | A consecrated world, or one being detoxified, can be terraformed |
| F | Starbase Extended 3.0 | Its `starbase_view` window, from July, replaces UI Overhaul Dynamic's 4.5 copy. It has no `open_planet` button, no `design_name` or `retrofit`, no `macro_builder_tab`, and two lists have no scrollbar. The first two are already in the log | 4.5: "Restored the button that brings you from an Orbital Ring back to its planet", "Restored the missing scrollbar in the starbase Shipyard, Army Hub, Defenses, and Critters lists" | Interface only. Run 3's item 9 already lists `open_planet` and `design_name` |

### Smaller or unclear

- **shrimpAI's Hyper Relay** has no clause for building it at your own
  waystation, which the game has. 4.5.2 says "Fixed Gateways, Hyper-Relays
  and the Grand Archive not being buildable by Nomadic empires in some
  cases". It matters only to Nomad empires.
- **Planetary Diversity's `trait_aquatic`** lacks one 4.5.2 AI change: "The
  AI now values the Aquatic trait on species that use the Wet Climate Mods
  planet preference." The player rule that goes with it isn't in the copy,
  so players aren't affected.
- **UI Overhaul Dynamic - Extended Topbar** replaces UI Overhaul Dynamic's
  whole `maingui` window with its June copy. That's how the add-on works, but
  anything UI Overhaul Dynamic added to that window since June is lost. No
  note names a topbar change except 4.5's research dropdown border.
- **Starbase Extended's orbital ring hangar bay** still charges energy
  upkeep for bio-ship empires, where the game's charges food. Its starbase
  size icons expect 18 frames. The game's sheet has 15.
- **Dark UI** has no dark versions of 4.5.2's new icons, such as the fleet
  deselect button and Ritualistic Implants. Interface only.

Other differences in these copies are the mods' own choices, such as
Planetary Diversity's planet classes in the World Forgers civics.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 15 | More Events Mod's three Progenitor shields use `@shield_*_t7_upkeep_*`, which 4.5.2 renamed to `@defense_*_t7_upkeep_*` | **Done** on 7 October ([patch](../patches/cold-steel-mix.md#what-each-fix-does)). Not yet checked in game. Was: Ship a `common/scripted_variables/` file that defines the six old names with the game's values for the new ones. Read the values from the game's file at build time ([decision 14](../decisions.md)). Leave the fix out if More Events Mod stops using the old names, or the game defines them again. Low value: three late-game components |
| 16 | Ships in Scaling's Large Mega Bombard has a range of 2 (row A) | **Done** on 7 October ([patch](../patches/cold-steel-mix.md#what-each-fix-does), [decision 31](../decisions.md)). Not yet checked in game. Was: Ship Ships in Scaling's `mutation_weapon_components.csv` with that one range set to the game's range divided as Ships in Scaling divides the Giga Bombard's (17 today). A `.csv` is replaced only as a whole file, so this ships another author's file. Leave the fix out once Ships in Scaling's row is no longer 2 |
| 17 | Real Space 4.0 seals the Surveillance Supercomputer system (row C) | **Done** on 7 October ([patch](../patches/cold-steel-mix.md#what-each-fix-does)). Not yet checked in game. Was: Ship Real Space's `surveillance_supercomputer_system` in a file that sorts first, without `sealed_system`. Initializers go to the first file by name, as events do for fixes 11 and 12. Leave the fix out once Real Space's copy drops the flag |
| 18 | Trait resources on `planet_pops` stack two modifiers per trait (row B) | **Left to the authors** on 7 October, and listed on the patch's Workshop page ([decision 33](../decisions.md)). Was: Tell Planetary Diversity's and More Events Mod's authors first: the fix is one word per trait, and their next update will likely carry it. A patch would have to copy 18 traits from three mods. It matters only with Unemployment Benefits or a Shroud-Warped governor over psionic pops |
| 19 | Ascension Worlds' Lithoid Budding and terraforming rule (rows D and E) | **Done** on 7 October ([patch](../patches/cold-steel-mix.md#what-each-fix-does), [decision 32](../decisions.md)). Not yet checked in game. Was: Copy the two objects with the game's missing lines added. Keep Ascension Worlds' own choice on legendary leader planets |
| 9 | Orbital ring sections, starbase window items, sounds, animations and attach points | Open, from run 3. Cosmetic. Row F adds what Starbase Extended's starbase window lacks against UI Overhaul Dynamic's 4.5 copy. Both are left to Starbase Extended's author and listed on the patch's Workshop page ([decision 33](../decisions.md)) |
| — | [cold-steel-mix.md](../patches/cold-steel-mix.md#check-in-game) expects no log entry about fixes 11 and 12's duplicate ids | **Done** on 7 October. Was: Say instead that the log has one notice for each, naming More Events Mod's file, and that this is the check that the patch wins |
| — | Accept the update check | Done at 16:18, before this run, and again after this report. Its 224 older copies and 9 undefined variables are now marked as reviewed, so the next check skips them until one changes. If item 15 is agreed, accept again once it's built |
| 8 | Starbase Extended's duplicate `potential` blocks, the `category` trigger, two missing buildings | Open, from [run 3](2026-10-03-cold-steel-mix-errors-run-3.md#what-a-patch-mod-could-fix). Left to Starbase Extended's author and listed on the patch's Workshop page ([decision 33](../decisions.md)) |

Still to check in game: fixes 11 and 12 firing, fix 10's tooltip, fix 1's
megastructures and storms, and whether the solid background came back.

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../src/stellaris_patcher/paradox/error_log.py).
- Split the entries by time. Loading lasted until the galaxy was made at
  17:21:46 (`game.log`). Game start lasted to 17:22:03. Play came after
  that. Grouped them by the source in the game's code, then by mod, the same
  way as run 5.
- Checked the new build record lists the patch last, and compared its 12
  files with our source folder byte for byte. Read `dlc_load.json` and the
  game's mod folder for what the game loaded.
- Searched the raw log for each name the fixes removed, and for the patch's
  two events.
- Read More Events Mod's `mem_lex_utilities.txt` at the logged lines, and
  searched the game's and every Workshop mod's files for the six variables.
  Only More Events Mod uses them, and nothing defines them.
- Unpacked the `2201.01.26` save into a scratch folder. Listed the system
  initializers around Sol and searched for the Ziaskehorn flag.
- For the patch notes: fetched Steam's announcements in full with
  [notes.py](../../src/stellaris_patcher/update/notes.py). Read the 4.5
  release notes (Dev Diary #433 and the release post), 4.5.1 and 4.5.2.
- Took each mod's last update time from Steam's
  `appworkshop_281990.acf`. The game file times give the release that last
  changed each game file: 22 September for 4.5, 24 September for 4.5.1,
  6 October for 4.5.2.
- Searched every older mod for each name the notes' Modding sections remove
  or rename.
- Listed every object an older mod defines that wins over the game's, where
  the game's file changed after the mod's last update. That gave 156 objects,
  not counting `on_actions` (merged) and text. Diffed each against the
  game's, or against UI Overhaul Dynamic's where that was the copy replaced.
  Kept the differences that match a note. Whole-file copies were checked the
  same way.
- The update check now does these last two steps itself, as "Older mod
  copies" and "Names the patch notes removed that older mods still use"
  ([update-check.md](../update-check.md)). Run on this playset, it finds all
  six rows among 224 copies to read.

## Limits

- **Four minutes of play.** Nothing about play can be compared yet.
- **What happened on screen.** The user saw nothing wrong. Visual problems,
  like the solid background, don't reach the logs.
- **Steam's 4.5 notes are cut short.** The bug fix, AI and interface
  sections end with "visit the Paradox forums for the full notes". The forum
  page couldn't be read: it asks for a browser check. A fix only in the
  forum's notes, undone by a mod copy, would show in the object diffs but
  couldn't be matched to a note.
- **File times are per file, not per object.** A game file changed in 4.5.2
  may have changed other objects than the one a mod copies. Each candidate
  was diffed for this reason, but a mod's own change and a missing game
  change look the same in a diff. Only the ones a note names are listed.
- **Effects are read from the files.** None of rows A to F was seen in game.
- **The shields' upkeep in game.** That the shields cost nothing comes from
  the log and the files. Nobody looked at the component in game.
