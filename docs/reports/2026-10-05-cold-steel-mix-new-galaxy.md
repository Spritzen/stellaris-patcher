# Game report: Cold Steel Mix build, new galaxy, 5 October 2026

**A new galaxy, played for three and a half hours from 2200 to 2225. The patch
held. Nothing in the log came from it, and nothing stopped play.** This is the
first run with fix 10. Play logged 24 entries, about one per game year.

- **The fixes held.** None of the names fixes 1–7 and 10 removed are in the
  log, and no entry names a patch file. Fix 10 can't be called confirmed:
  its text may never have been shown. Fixes 1 and 5 weren't exercised. See
  [The patch's fixes](#the-patchs-fixes).
- **Loading logged 89 problems, against 96 in run 4. Every one has a cause
  already known.** See [Loading](#loading).
- **The empire designer logged 36 more, all the game's own.** Renaming the
  empire re-checks an origin's machine test on an empire with no species yet.
  See [The empire designer](#the-empire-designer-36).
- **One new patch candidate: More Events Mod loses the Ziaskehorn dig site.**
  Its event sends the discovery before saving the planet. So the site is
  never made, and a flag stops it coming back. It happened in this game. See
  [More Events Mod](#more-events-mod-8).
- **One smaller candidate.** A More Events Mod leader is created with a
  commander trait on an official, and gets no trait.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.1 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.05`, with fixes 1–7 and 10. Its 11 files in the build match our source folder byte for byte. The Workshop copy (`workshop:3812655652`) isn't in the playset or on disk |
| Built | 19:21 local time on 5 October, seconds before the game started. The build record has no mismatches |
| Session | Started 19:21. New galaxy, seed 891620046, made at 19:25. Played from `2200.01.01` to `2225.02.03`, saved and quit at 22:47. No crash |
| Empire | Divine Elven Order |
| Logs | `error.log`: 6,618 entries. 5,717 resources not installed and 752 override notices, as before. 149 problems: 89 from loading and game start, 36 from the empire designer, 24 from play. `game.log`: event picks and one AI default |

The log's clock is local time, one hour ahead of the file times.

## Compared with earlier runs

Run 4 also made a new galaxy. The long session loaded a save.

| Group | Run 4 | Long session | This run |
|---|---:|---:|---:|
| Problems while loading and at game start | 96 | 108 | 89 |
| The empire designer | — | — | 36 |
| Problems during play | 0 (3 minutes) | 95 (10.5 hours, 38 years) | 24 (3.5 hours, 25 years) |

Run 4's 96 included 4 `founder_species` entries. This run has the same
entry, but counted on its own, since the designer logged 36.

## The patch's fixes

**None of the names the fixes removed are in the log.** Searched the raw log
as in run 4: no `MEDIUM_GUN_01*`, `build_block_radius`,
`starbase_formation_priority`, `sol_neighbor`, `is_pd_planet_for_aqua_trait`,
`starlit`, `voidspawn`, `rs_d_dark_matter`, `fire_rate_reduction`,
`hp_increased`, `nsc.requires`, `PLANET_SCALE_SYSTEM`, `ZOOM_STEPS`,
`GetAdministratorPluralWithIcon` or `mod_planet_bureaucrats`. No entry names a
patch file.

Three fixes weren't really tested:

- **Fix 10**: the long session logged its error once in 10.5 hours, when the
  tooltip was shown. A clean log here doesn't prove the tooltip was shown.
- **Fix 1**: the 2225 save has no Dyson sphere, quantum catapult, Starlit
  system or cosmic storm.
- **Fix 5**: no empire started at Sol, so no Sol neighbour systems were made.
  Run 4 checked it.

## Loading

**89 entries, all with causes known from
[run 3](2026-10-03-cold-steel-mix-errors-run-3.md#whats-left-by-mod).**

| Group | Run 4 | This run | Change |
|---|---:|---:|---|
| Starbase Extended 3.0 | 47 | 47 | None |
| Diverse Rooms (All in One) | 28 | 27 | −1: the `primary_species` entry is gone. The mod's file no longer names it |
| Real Space family, with Cinematic Camera | 9 | 8 | −1: the zoom mismatch, removed by fix 4. Left: System Scale's 6 infernal ring world textures, Real Space 4.0's two `nospec.dds` |
| The game's own | 5 | 1 | The missing `trait_organic`. Run 4's 4 `founder_species` entries are under [the empire designer](#the-empire-designer-36) |
| Descriptors, Just Star Names, Apocryphos | 7 | 6 | −1: ASB Ironman's `.mod` file isn't logged any more |
| **Total** | **96** | **89** | |

Starbase Extended's 47 includes 3 from game start: two missing starbase window
items and the humanoid starport's attach point `part4`.

## The empire designer (36)

**All 36 are the same line of the game's own script.** The game's Life-Seeded
origin (line 2383 of `common/governments/civics/00_origins.txt`) checks
`is_individual_machine`, which asks for `founder_species`. An empire still in
the designer has none.

- **30** came between 19:22:58 and 19:24:32, before the galaxy was made. The
  empire's name in them changes letter by letter ("Divine  Order",
  "Divine ElveOrder"), so the designer re-checks on each change.
- **6** came at 19:33. The game saved `2200.01.01` at 19:32 and recalculated
  its state at 19:33:28, as it does when a save loads. So the save was most
  likely reloaded.

No mod replaces either file. Harmless.

## During play

**24 entries over 25 game years. None stopped play.**

| Source | Entries | Matters? |
|---|---:|---|
| Starbase Extended 3.0 | 9 | Cosmetic |
| More Events Mod | 8 | Yes: 4 of them lose the Ziaskehorn dig site for the whole game |
| The game's own | 7 | No |
| **Total** | **24** | |

### More Events Mod (8)

- **4: the Ziaskehorn dig site is never made.** `mem_scfe_ziaskehorn.1`
  (line 12,016 of `events/mem_asp_scfe_events.txt`) runs when a ship surveys
  a molten or volcanic planet after year 20. On a 10% roll it does three
  things in this order:
  1. fires `mem_scfe_ziaskehorn.2`,
  2. sets the global flag `discovered_ziaskehorn`,
  3. saves the planet as `mem_ziaskehorn_planet`.

  Event `.2` runs straight away, before step 3. Its lines 12,069 and 12,091
  find no planet, so `prevent_anomaly` and `create_archaeological_site` both
  fail. The flag is already set, so `.1` never fires again. That line is the
  only place the site is made, so this galaxy will never have it. The 2225
  save has the flag and no site. It fired at 22:23 on the ship "CSY Salty
  Squid", which is no longer in the save.

  This is More Events Mod's own bug, not a clash. It happens in every game
  where the roll comes up.
- **1: a trait the leader can't have.** `mem_stuck_in_glacier.22` (line 536
  of `events/mem_stuck_in_glacier.txt`) creates an AI leader on one of four
  rolls. One roll makes an official with `leader_trait_iron_fist`. In 4.5,
  Iron Fist is a commander trait, so the official gets no trait.
- **3: a specimen description**, `mem_laser_rifle_desc_details`, uses
  `[From.From.GetName]`, which has nothing to point at when shown. Text only.
  The long session logged the same while loading.

### Starbase Extended 3.0 (9)

**Starports ask for attach points `part4`–`part7` that their models don't
have.** Humanoid `part5` (1), aquatic `part4`–`part7` (4), reptilian
`part4`–`part7` (4). Whatever the game attaches there doesn't show. The same
cause as run 3's animations row, now seen on two more
styles.

### The game's own (7)

None of these are in files a mod replaces, unless noted.

| What | Entries | Where |
|---|---:|---|
| Nemesis intel text for a moon names `known_planet`, with nothing to point at | 2 | `PlanetBio*Moon` in `localisation/english/nemesis_intel_l_english.yml` |
| A Toxoids story title names `questing_knight_1`, with nothing to point at | 2 | `toxoids.7011` in `localisation/english/toxoids_l_english.yml` |
| Luxury Residences couldn't be added to "Queptilium Primum". The building's AI limit fails: the AI owner has enough amenities | 1 | `building_luxury_residence` in `common/buildings/07_amenity_buildings.txt` |
| A ship aura tooltip got a scope that wasn't a ship | 1 | The game program (`ship_aura.cpp`). No script file named |
| A machine empire's Lost Colony parent can't get its research zone | 1 | Real Space 4.0's copy of `federations_initializers.txt`, line 1179. The game's own file has the same code, as the [long session](2026-10-04-cold-steel-mix-long-session.md#the-games-own-80) found |

## Not errors: AI empires defaulting

**One AI empire defaulted on its debts, in 2210.** The long session had 12 in
38 years. One galaxy and 25 years is too little to compare.

## What to do next

| # | Problem | Status |
|---|---|---|
| 11 | More Events Mod's `mem_scfe_ziaskehorn.1` fires the discovery before saving the planet, so the Ziaskehorn dig site is never made | **Done** on 5 October ([patch](../patches/cold-steel-mix.md#what-each-fix-does)). Not yet checked in game. Was: Ship a copy of `mem_scfe_ziaskehorn.1` with the `from = { save_event_target_as = … }` block moved above the `ship_event` call. Events go to the first file by name ([merge_rules.json](../../src/stellaris_patcher/data/merge_rules.json)), so the patch's file must sort before `mem_asp_scfe_events.txt` and declare the `mem_scfe_ziaskehorn` namespace. Check in game that More Events Mod's copy is then ignored |
| 12 | More Events Mod's `mem_stuck_in_glacier.22` gives an official the commander trait Iron Fist | **Done** on 5 October, as a commander that keeps Iron Fist ([decision 24](../decisions.md)). Not yet checked in game. Was: Low value: one leader, one roll in four, no trait instead of one. Same method as 11, with an official trait in its place |
| 8 | Starbase Extended's duplicate `potential` blocks, the `category` trigger, two missing buildings | Open, from [run 3](2026-10-03-cold-steel-mix-errors-run-3.md#what-a-patch-mod-could-fix) |
| 9 | Orbital ring sections, starbase window items, sounds, animations and attach points | Open, from run 3. Cosmetic. This run adds the aquatic and reptilian starports' `part4`–`part7` |

Still to check in game: fix 10's tooltip, fix 1's megastructures and storms,
and whether the solid background came back.

## How this was worked out

- Ran Cold Steel's error reader (`ErrorReader`) read-only, from its mounted
  source, with its cache in a scratch folder, as in the earlier runs.
- Split the entries by time: loading up to 19:22:27, the designer before the
  galaxy was made at 19:25:08 (`game.log`), game start to 19:25:26, and play.
- Moved entries from "Game / unknown" to the mods their files or text belong
  to: three `.anim` files to Starbase Extended, `nospec.dds` to Real Space
  4.0, the track to Apocryphos, three text lines to More Events Mod. Moved
  `federations_initializers.txt` the other way, to the game, as in the long
  session.
- Checked the build record lists the patch last, and compared its 11 files
  with our source folder byte for byte.
- Searched the raw log for each name the fixes removed.
- For each play entry, looked up which mod the named file came from in the
  build record, and read the code at that line. Looked up the three leader
  traits' classes in the game's files.
- Unpacked the 2225 save into a scratch folder. Searched it for the
  Ziaskehorn flag and site, the ship, megastructures, storms and Sol
  neighbour systems.

**Limits.** One galaxy, 25 years. Fixes 1, 5 and 10 weren't exercised, as
far as the log and save show. Visual problems, like the solid background,
don't reach the logs.
