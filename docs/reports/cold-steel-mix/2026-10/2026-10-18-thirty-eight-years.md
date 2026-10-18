# Game report: Cold Steel Mix, the Divine Elven Order galaxy from 2215 to 2253, 18 October 2026

**A galaxy started on 17 October, loaded from its 2215.01.04 save and
played to 2253.01.01. That's 38 years in about 5½ hours. It's the first run
with Stellar AI 0.14. The patch held, and the user saw nothing unusual. Play
logged 72 entries. 45 are the game's own, 23 More Events Mod's, 2 Stellar
AI's and 2 Real Space 4.0's. None is worth a patch fix. Our own log reader
misread one path, and is now fixed (item 42).**

- **Stellar AI 0.14 is in the build and changes no override notice.** It's
  848, kind for kind, as on 13 October. Its one play entry pair is a colony
  type check on a planet with no owner. It's harmless, and the check has been
  there since 0.11. See [Stellar AI](#stellar-ai-2).
- **No AI empire defaulted in 38 years.** `game.log` has no deficit line, and
  the 2253 save has no `country_defaulted`. The update check asked to watch
  this with 0.14.
- **14 Starholds and the galaxy's first military arkship logged nothing.**
  The galaxy went from 0 to 14 Starholds and 29 to 54 Starports, so fix 31
  fits the log. Fix 32's arkship errors didn't come back.
- **Two new More Events Mod and Real Space entries are cosmetic.** More
  Events Mod's Rebel Yell boss makes a robot species with no name. Real
  Space 4.0's microquasar meshes name a texture one folder too deep.
- **Our log reader misfiles paths with `~`.** Stellar AI's entry came back
  with its file name and its inline script run together. Item 42 fixed it.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`. Its 73 files in the build match our patch folder byte for byte |
| Built | The Cold Steel build at 11:53 on the log's clock, seconds before the game started. The build record has no mismatches. Its 88 Stellar AI files match the installed 0.14 byte for byte |
| Session | Started 11:53:25. Loaded `2215.01.04` at 11:57:54. Saved `2228.12.18` at 14:29, `2237.07.08` at 15:24 and `2253.01.01` at 17:29. Autosaves every half year from 2251.01.01. About 5½ hours of play |
| Empire | Divine Elven Order, the user's custom Life-Seeded empire. A small galaxy with 12 empires, 1 Fallen Empire, 1 marauder and 1 nomad empire, started on 17 October at 22:22. The run on 17 October, from 2200 to 2215, has no report, and its log is gone |
| Logs | `error.log`: 6,681 entries. 5,717 resources not installed, 848 override notices and 116 problems: 43 from loading, 1 from loading the save, 72 from play. `game.log`: event picks, three AI rebellions and one More Events Mod log line |

The log's clock is one hour ahead of the file times, as before.

## Compared with earlier runs

The last run was the [five years](2026-10-13-five-years-stellar-ai.md) run, in a
new galaxy. The last run from a save was the [sixty years](2026-10-11-sixty-years.md) run.

| Group | Sixty years | Five years | This run | Change from five years |
|---|---:|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 7 | 7 | None. Stellar AI's "Could not find files for mod" is back again |
| The game's own, while loading | 1 | 1 | 1 | None: the missing `trait_organic` |
| The game's own, loading the save | 1 | 0 | 1 | Three deposits with no type. See below |
| The game's Life-Seeded check | 0 | 21 | 0 | A save, not a new galaxy |
| More Events Mod, at game start | 0 | 1 | 0 | A save |
| The game's own, in play | 38 | 1 | 45 | See [The game's own](#the-games-own-45) |
| More Events Mod, in play | 1 | 0 | 23 | 22 from one dig site, 1 from Rebel Yell |
| Stellar AI, in play | 0 | 0 | 2 | A colony type check |
| Real Space 4.0, in play | 0 | 0 | 2 | A microquasar texture |
| **Total** | **82** | **66** | **116** | |

5½ hours of play, against 12 minutes last run and 2¾ hours in the sixty
years run.

**The override notices didn't change: 848**, kind for kind: 301 duplicate
objects, 480 entities, 23 section templates, 31 events, 12 variables and
Real Space's initializer. Stellar AI 0.14 changed only files and names no
other mod has, as the [update check](2026-10-18-4.5.2-update.md) found.

## The patch's fixes

**The game uses every copy the patch ships.** 40 duplicate object notices
name the patch's files, the same as last run. The duplicate event notices for
fixes 11, 12, 26 and 40, and fix 17's initializer notice, name the mods' own
files, so the patch's copies win.

**None of the names the fixes removed are in the log**, the same list as the
[sixty years](2026-10-11-sixty-years.md#the-patchs-fixes) run. Its one
`ion_core_effect` is a duplicate entity notice, and its two `hyper_relay`
lines are the shrimpAI and patch notices. One of its two `solar_system` lines
is fix 17's initializer notice. The other is the game's BioGenesis event
(below). Its five `ORBITAL_RING_SECTION` lines are duplicate section
templates, not missing sections.

| Fix | In game |
|---|---|
| 31 | **The log fits at 14 Starholds.** The galaxy went from 29 Starports and no Starholds to 54 and 14. No attach point, sound, particle or animation entries |
| 32 | **The log fits with an arkship.** The 2253 save has the galaxy's first `starbase_level_military_arkship_champions_forge`. None of Starbase Extended's building checks logged an error. The 7 observatory entries come from the game's own building (below) |
| 41 | Not reached. No empire in the 2253 save has `civic_idyllic_bloom`, and no planet has a Gaia Seeder |
| 40 | Not reached, but still can be. The 2253 save has no `mem_astral_tales_fired`, so Astral Tales hasn't run in this galaxy |
| 38 | Not reached. No `mem_ancestors_grudge.45` in `game.log`, and no Grudge empire in the galaxy |
| 37 | Not reached. The 2253 save has no Archaeostudies Faculty and no Archeotech Preserve zone |
| 36 | Not reached: no `Unknown promotion From` |
| 28 | Not reached. No Hyper Relays |

## Loading (43)

The same 43 as the five years run, group for group, less More Events Mod's
game start notice. Details of each group are in
[run 3](2026-10-03-errors-run-3.md#whats-left-by-mod).

## Loading the save (1)

**`Repaired savegame, cleared 3 invalid deposits!`** at 11:57:54. The 2215
save has 3 deposits with no `type`, on the star Magnus, the barren world
Secunda and the Planetary Diversity wet gaia world Cidar. The galaxy's
2200.01.01 save already had 4. The 2237 save has none. As in the
[thirty-two years](2026-10-11-thirty-two-years.md#loading-the-save-1) run,
the cause isn't found. The game's own repair, and harmless.

## During play (72)

### More Events Mod (23)

**The giant sphere dig site again (22).** At 14:13:26–27 the Skanurian High
Kingdom's science ship SHKM Fearless Hatchling reached `mem_asp.81`
(`events/mem_asp_scfe_events.txt`). `game.log` records option 1, option b,
which deletes the site. The event's `after` block then reads the deleted site
at lines 1486 and 1493 (3 entries), and `destroy_archaeological_site` at line
1502 finds no site (1). The game's own `default_site_visible_trigger` checks
every empire's view of the site again: 1 `intel_level` entry and 17 context
switches. It's the same story as in the
[thirty-two years](2026-10-11-thirty-two-years.md#the-giant-sphere-site-23)
run. Harmless, and left to More Events Mod.

**The Rebel Yell boss species has no name (1).** At 16:32:45 More Events
Mod's `mem_rebel_yell.4` opened the wormhole to its boss system, on
2244.03.17. In the same second the game logged
``Missing species names for species class "Mechanical"``. The boss system,
`mem_rebel_yell_system_2` in
`common/solar_system_initializers/mem_rebel_yell_systems.txt`, makes its
Resistance country with `create_species = { class = ROBOT … }` and no
`name`. The game has no species name list for robots, which it shows as
"Mechanical". The 2253 save's species 115, the Resistance's, has
`name_list="MACHINE1"` and no name at all. So the species name is blank
wherever it shows, such as on the Custodian leaders. Cosmetic, and only in
that story.

### Stellar AI (2)

**A colony type check on a planet with no owner.** At 15:49:20, about 2240,
the game checked the City designation, `col_city`, for Al-Fawaris III. Stellar
AI's copy in `common/colony_types/~stellarai_colony_types.txt` line 21 calls
its inline script `stellarai/invalid_urban_colony_type_potential`. Its lines
2 and 5 read `owner = { is_ai = … }`. Al-Fawaris III, an alpine world, had no
owner, so both logged `Invalid context switch [owner]`. The user's empire
colonised it in 2245.

The game's own `col_city` reads `owner_or_space_owner?`, which works without
an owner. Stellar AI's check just fails, which rules out City for a planet
that has no designation anyway. The script is in every Stellar AI version
since 0.11. Harmless.

### Real Space 4.0 (2)

**A microquasar's texture, one folder too deep.** At 13:38:57 the game
couldn't find `gfx/models/planets/planets/nospec.dds`. Real Space 4.0's
three microquasar meshes in `gfx/models/planets/` name `planets\nospec.dds`,
which the game reads from the mesh's own folder. That's the "Failed to find
texture" entry at loading, now logged when a microquasar was drawn.
`nospec.dds` is a blank "no shine" texture, so nothing on screen changes.
Real Space's own, and harmless.

### The game's own (45)

| Time | Entries | Cause |
|---|---:|---|
| 13:09:59 | 15 | `Undefined event target: refugee_pop`: the game's Expel Population decision and its `refugee_pop_effect`, as in the [sixty years](2026-10-11-sixty-years.md#the-games-own-38) run. It checked the Klenn Protectorate and the Rethellian State as places to flee to. One use of the decision |
| 13:50:40 | 1 | `Unable to add trait … leader_class_does_not_match`: the game's `espionage.1017` (`events/nemesis_espionage_events.txt` line 882), which the user picked. It gives the spy network's leader Meticulous, a scientist trait, "purely flavour" by its own comment |
| 14:11:54 | 1 | `CShipAura::GetToolTipString`: a tooltip in the game's program, as in the [thirty-two years](2026-10-11-thirty-two-years.md) run |
| 14:30:38 | 1 | ``Unknown promotion `System` ``: the game's timeline tooltip, as in the [five years](2026-10-13-five-years-stellar-ai.md#during-play-1) run |
| 15:06:25–57 | 8 | The game's BioGenesis `bio.3105` (`events/biogenesis_events.txt`), which the user picked. It spawns a Fallen Empire's Experimental Ship in the system of the user's strongest fleet. That fleet, Alpha Defence Force, had no system at that moment (line 7301), probably as it was between systems. So `target_system` wasn't set: 4 text entries naming it, the ship placed nowhere (lines 7413 and 7422), and the game sent it home as MIA. Neither the ship nor its country is in the 2251 save |
| 15:07:19 | 1 | `Missing sound effect: arthropoid_01_greetings_ascended`: the game's arthropoid portrait has no psionic greeting |
| 15:17:34 | 2 | ``Unknown property `GetAdjective` `` and `` `GetSpeciesName` ``: the game's Grand Archive specimen text `memorial_to_homeworld_desc_details`, read without its targets |
| 15:20:34 | 2 | `Invalid context switch [event_target:wenkwort_truin]`: the game's Wenkwort caretaker patrol (`common/scripted_effects/federations_event_effects.txt` line 1634) picked Truin, an asteroid that's gone. The game's Grand Archive hid its Cutholoids in it in this galaxy (`pc_cutholoid` in 2215), and planet 3672 is gone by 2237. The caretaker stops its patrol. Real Space 4.0's copy of the Wenkwort system saves the same target as the game's |
| 15:28:52 | 1 | `Invalid context switch [owner] from Beta Zunari IVa`: the game's `timeline_events.txt` line 2732 on a planet with no owner, as in the [long session](2026-10-04-long-session.md) |
| 16:10:57 | 1 | `set_mia effect: fleet 'Mendoc Mining Station' cannot go MIA`: the game's Final Layer arc site, `ancrel.11020` (`events/ancient_relics_arcsite_events_2.txt` line 7862), turned an AI empire's system into a black hole. `destroy_star_system` sends arkship fleets home, and this one couldn't go |
| 16:51:07 | 2 | `Wrong scope for effect 'set_planet_flag'` and `Failed to get leader from scope`: the game's Treasure Hunters origin, `grand_archive.8120` (`events/origin_events_grand_archive.txt` lines 3435 and 3441), after a failed Black Needle base hack. Its `fromfrom` is a country, not a planet, and the ship had no leader to kill. An AI empire's |
| 16:54:19 | 1 | `Unexpected class for CLeaderLocation`: the game's program. No file |
| 17:02:53 | 7 | `Invalid context switch [star]` in the game's observatory output values (`common/starbase_buildings/00_starbase_buildings.txt` lines 613–630), on a starbase with no star and a name the game couldn't format, as in the [long session](2026-10-04-long-session.md). An arkship's starbase has no star, and the galaxy has one |
| 17:09:33 | 1 | `Invalid context switch [FROM] from Baron Vyctor Jariden [leader]`: the game's admiral trait check (`common/traits/00_admiral_traits.txt` line 1201), as in the [sixty years](2026-10-11-sixty-years.md#the-games-own-38) run |
| 17:12:22 | 1 | `Failed to add building Luxury Residences to planet Law'rah`: an AI may finish one only while its planet has fewer than 500 spare amenities, as in the [seventeen years](2026-10-10-seventeen-years.md) run |

Each file is the game's own in the build record, except Real Space 4.0's
Wenkwort system, which has the same target.

## Not errors: AI rebellions and a long war

**No AI empire defaulted.** See the summary.

**Three AI rebellions**, from the game's `events/unrest_events.txt`: the
Pyrrag'Thul Planet Forgers on Embron in 2223, and the Mollarnock Grand Duchy
on Bhumidevi IV in 2232 and on Unur IV in 2242.

**The 2223 revolt is still at war in 2253.** It's the War of Revolt over
Pyrrag'Thul, with independence against overlordship. Both sides' war
exhaustion rises slowly: 0.38 in 2237, 0.70 in 2251 and 0.75 to 0.79 in 2253.
At that pace it reaches 100%, and the game ends it, around 2260. Two other
wars are on: one since 2232 and the user's own since 2242. Long wars can be
the game's own. One isn't enough to call it Stellar AI's.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 42 | Our [error_log.py](../../../../src/stellaris_patcher/paradox/error_log.py) didn't count `~` as part of a path. So Stellar AI's entry came back with `~stellarai_colony_types.txt:21(inline_script)` and its inline script run together as its file, not as `common/colony_types/~stellarai_colony_types.txt` line 21 | **Done.** `~` is now a path character, with tests from this entry. On this run's log only Stellar AI's two entries change: each now names line 21 of `~stellarai_colony_types.txt`. Our tool, not the patch |
| 43 | More Events Mod's Rebel Yell boss species has no name | No patch fix. It's cosmetic, in one story, and this galaxy's boss system is already made. Leave it to More Events Mod |
| 24 | AI defaults | None in 38 years with Stellar AI 0.14. Keep it closed |
| 40 | Fix 40 isn't checked in game | Astral Tales hasn't run in this galaxy, so it still can. The log and build already fit |
| 41, 38, 37 | Not checked in game | As in the [five years](2026-10-13-five-years-stellar-ai.md#what-to-do-next) and [sixty years](2026-10-11-sixty-years.md#what-to-do-next) reports |
| — | This report isn't committed | Commit it |

The other entries are harmless, and no patch fix is proposed.

## How this was worked out

- `error.log` read with
  [error_log.py](../../../../src/stellaris_patcher/paradox/error_log.py), and
  split by time: loading to 11:54:05, the save at 11:57:54 (`time.log`),
  play from 13:09:59 to 17:12:22.
- Override notices counted by kind against the five years report.
- The build record, `builds/d8f5e037….json`, compared with our patch folder
  and with Stellar AI's installed 0.14. The patch's 73 files and Stellar AI's
  88 compared byte for byte with the build folder.
- The raw log searched for each name the fixes removed. Notices naming the
  patch's files counted.
- Each play entry's file traced in the build record, and the code at its line
  read: More Events Mod's dig site event and Rebel Yell system, Stellar AI's
  colony types and inline script, Real Space's microquasar meshes and
  Wenkwort system, and the game's files in the table.
- The `2200.01.01`, `2215.01.04`, `2237.07.08`, `2251.01.01` and
  `2253.01.01` saves unpacked into a scratch folder: deposits with no type,
  Al-Fawaris III, the Truin asteroid and Wenkwort targets, the Experimental
  Ship, the robot species, starbases by level, wars and their exhaustion,
  defaults, and each unchecked fix's buildings, civics and flags.

## Limits

- **What happened on screen.** The user saw nothing unusual but didn't say
  which windows they opened. Visual problems don't reach the logs.
- **The first fifteen years.** The 17 October run from 2200 to 2215 has no
  report, and its log is gone.
- **Game dates in play** are estimated from the save times, except where the
  log gives one.
- **Why Alpha Defence Force had no system**, and what happened to the
  Experimental Ship. The saves before and after are years apart.
- **Who used Expel Population.** The entries name only the places to flee to.
