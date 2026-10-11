# Error log report: Cold Steel Mix build, 3 October 2026

**One mod causes almost all the real errors: Ariphaos Unofficial Patch (4.2).**
It was made for Stellaris 4.2.4, and the game is 4.5.1. It replaces 220 of the
game's own files with its 4.2 copies, so the newer content in those files is
gone. That one mod accounts for 5,361 of the 11,463 log entries. Remove it and
rebuild.

Most of the other entries are harmless:

- 4,754 come from Universal Resource Patch listing resources from mods you
  don't have. This is how it's meant to work.
- 839 are override notices ("this mod replaced that object").

About 500 entries are left after those three groups. A few small,
mod-specific problems are listed under [Other mods](#other-mods).

The merge itself caused no errors. Every error traces back to a file that
exists in one of the 28 source mods or in the game.

Cold Steel marked Ariphaos as outdated in the Supported column. But its
stronger "old copies" warning, which exists for exactly this, stayed silent,
because it doesn't check a mod against the game's own files. Its error reader
also can't attribute a build's errors to the right mods. Both are fixable;
see [What Cold Steel should change](#what-cold-steel-should-change).

## The run

| | |
|---|---|
| Game | Stellaris 4.5.1 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (built 2026-10-03) |
| Built from | The 28-mod playset "Cold Steel Mix" |
| Log | `logs/error.log`, 15,929 lines, 11,463 entries |
| Session | Started 10:41, three galaxies generated, played to 10:56 |

## Where the errors come from

| Cause | Entries | Share | Harmful? |
|---|---:|---:|---|
| Ariphaos Unofficial Patch: errors in its own files | 2,422 | 21% | Yes |
| Ariphaos Unofficial Patch: other files hit by what it removed | 2,939 | 26% | Yes |
| Universal Resource Patch: resources not installed | 4,754 | 41% | No |
| Override notices | 839 | 7% | No |
| Other mods (see below) | 135 | 1% | Mostly minor |
| The game's own noise, or not traced | 374 | 3% | Mostly no |
| **Total** | **11,463** | | |

"Other files hit" means the error is logged against a vanilla file, but the
cause is something Ariphaos deleted. For example, vanilla's
`08_scripted_triggers_shroud.txt` asks for the starbase building
`aura_emitter`. Ariphaos's copy of the starbase buildings file no longer loads
it, so the game logs the error against the shroud triggers file. These were
traced by looking up where vanilla 4.5.1 defines each missing name and checking
which mod's file the game read instead.

## Ariphaos Unofficial Patch (4.2)

### What's wrong

- **Its descriptor says `supported_version="v4.2.4"`.** The game is 4.5.1.
- **It ships 284 files, 255 of them copies of vanilla files.** Nothing later in
  the load order replaces 220 of those copies, so the game reads Ariphaos's 4.2
  version instead of the 4.5 one.
- **Those copies are missing 292 things that 4.5 defines**: 60 scripted
  triggers, 42 events, 35 script values, 33 game rules, 29 scripted effects, 19
  scripted variables, 12 buildings, civics, policies, ascension perks and more.
- **13 of its files use `any_system_colony`, which 4.5 renamed to
  `any_system_planet_colony`.** On the old name, the parser loses its place and
  throws away the rest of the block. Sometimes that's the rest of the file.

### How it breaks, by error count

| What happens | Entries |
|---|---:|
| Six event files stop parsing after an `any_system_colony` ("Corrupt Event Table Entry") | 1,104 |
| Arkship designs can't fit any combat computer, reactor or thruster | 1,005 |
| 18 starbase buildings never load (parse breaks at line 1,926 of its `00_starbase_buildings.txt`) | 544 |
| Everything else that 4.5 added and Ariphaos's copies lack | 2,708 |

The six event files: `machine_age_crisis_events.txt` (259 entries),
`origin_events_3.txt` (252), `pre_ftl_awareness_events.txt` (186),
`on_action_events_1.txt` (162), `origin_events_paragon.txt` (132),
`first_contact_dlc_events.txt` (112).

Arkships fail because vanilla 4.5's `00_utilities_roles.txt`,
`00_utilities_reactors.txt` and `00_utilities_thrusters.txt` mention Arkships
22, 8 and 35 times. Ariphaos's copies mention them zero times.

### What you'd notice in game

These are the parts of the game that are missing or broken while Ariphaos is
loaded:

- **Advanced starts.** `game_start.100`, `.105`, `.110`, `.130` and `.135`
  don't exist. These set up AI empires that get advanced starts.
- **Starbase buildings.** Command Center, Ice Mining Station, Aura Emitter,
  Dark Matter Detector, Dark Matter Listening Post, Mercenary Garrison,
  Dimensional Shrine, Reloading Bay, Gravitational Centrifuge, Storm
  Attraction/Repelling Computers, Dragon Hatchery and six more can't be built.
- **Nomads (4.5).** Arkships can't fit core components. The cruise passenger
  pop category, the cruise citizenship types, the waystation and arkship
  economy categories, nomad policies and nomad ascension perks are missing.
- **Psionic auras (Shroud).** Every check for an aura emitter fails.
- **Civics added after 4.2.** Void Reavers, Star Seekers, Hired Guns and Deep
  Sleep don't exist. Real Space's prescripted species that use Star Seekers
  fail to spawn properly.
- **Origins and crises.** Events for Remnants, Paragon origins, the Machine Age
  crisis, First Contact and pre-FTL awareness are partly lost. 29 on_action
  hooks point to events that no longer exist. 32 vanilla events are fired on
  the wrong scope (4.5 split "planet" and "colony" into separate scopes;
  Ariphaos's events still use the old one).
- **Game rules.** 33 rules the engine asks for, such as `has_borders` and
  `can_nomad_settle`, are missing or empty. The engine falls back to defaults.

### What to do

**Take Ariphaos Unofficial Patch (4.2) out of Cold Steel Mix and rebuild.**
Its fixes are for 4.2. Many of those bugs are fixed in 4.5 anyway, and any it
still fixes are worth far less than what it removes. If the author publishes a
4.5 version, that would be safe to try.

That removes about 5,400 entries, nearly half the log. With Universal Resource
Patch's list and the override notices set aside, a few hundred entries are
left.

## Universal Resource Patch

All 4,754 entries are `Failed to read key reference X from database`, from five
files in `interface/resource_groups/`. Each file lists about 950 resources from
many mods (Star Trek, Kyber crystals, Dilithium and so on), so that any you
have show in the top bar. Each one you don't have logs one line. They were all
logged in the same minute at startup.

**Keep it.** These entries are harmless and mean nothing is wrong.

## Other mods

None of these block play. In order of how much they matter:

| Mod | Entries | What's wrong | Matters? |
|---|---:|---|---|
| Planetary Diversity | 55 + 4 | Event `pddomebases.200` is a `colony_event`, but the game ran it on a planet 55 times. 4.5 split those scopes. Its `trigger` only lets it run for the Interplanetary Settlers origin | Only with that origin |
| Planetary Diversity, PD Ascension Worlds, More Events Mod | 4 + 16 + 2 | Decisions refer to `ice_mining_station` (lost via Ariphaos), and start systems refer to `sol_neighbor_t1`/`t2`. Real Space 4.0 renames those Sol neighbours to real stars (Alpha Centauri, Sirius…) in its `sol_initializers.txt` | The first goes away with Ariphaos. The second matters only for PD's habitat start and More Events Mod's Eden Protocol |
| Planetary Diversity - Unique Worlds | 14 | Two button shaders use `pow(vec3, float)`. DirectX accepts that, but Linux OpenGL doesn't, so the shaders don't compile | Cosmetic: some biosynth buttons render plain. Worth reporting to the author |
| Starbase Extended 3.0 | 21 | Uses `@build_block_radius_starbase` and `@starbase_formation_priority`, which 4.5 now defines only inside vanilla's ship size files. Two GUI elements its starbase view expects are gone in 4.5. Three missing `.anim` files | Minor. Some starbase sizes may use default values |
| Diverse Rooms (All in One) | 28 | Portrait room picker names ethics, civics and authorities from other mods (`ethic_dark_side`) and some that 4.5 renamed | No. Those rooms are just never picked |
| Real Space 4.0 | 3 | Distant Stars anomaly categories and `orbital_ring_ruined` it refers to are lost via Ariphaos | Goes away with Ariphaos |
| Just Star Names (Continued) | 1 | Format error near line 5,852 of `09random_names_l_english.yml` | No. At most a few names are skipped |
| Five `.mod` descriptors | 5 | `Invalid supported_version`. The game reads every `.mod` file, loaded or not | No |

Several mods are marked for an older game version (UI Overhaul Dynamic -
Extended Topbar and Dark UI say 4.4), but they logged no errors. As
decision 63 says, an old version number alone isn't a
problem.

## The game's own noise

About 374 entries name no mod and don't trace to Ariphaos. These are mostly
what a vanilla 4.5.1 run logs anyway: "generates modifiers that is never
used" for economic categories, missing localisation keys, missing sound
effects and textures for aquatic and toxoid starbases, and crisis events
without a mean time to happen. A few more Nomads gaps (`nomad_total_war`,
`megastructures_arkships`) are probably also from Ariphaos but weren't traced
far enough to be sure.

## Did the merge cause anything?

**No sign of it.** The checks:

- Every error that names a file maps to a file in a source mod or in the game.
  None names a file that only exists in the build.
- 232 parse errors quote both a token and a line number. In all 232, that
  line of the source file holds that token: 204 in Ariphaos, 4 in Starbase
  Extended and 24 in the game. So the game read the exact file that load order
  says it should, byte for byte.
- Nothing in the log points at the build's own descriptor or thumbnail.

The same playset loaded mod by mod would give the same errors.

## What Cold Steel should change

These are suggestions, not decisions. Each would become a row in
decisions.md if taken up.

1. **Run the "old copies" check against the game's files too.**
   `find_old_copies` in `old_copies.py`
   skips the game layer on purpose (`if layer != GAME`). Ariphaos passes both
   tests in decision 63: it's made for 4.2 while the game is 4.5, and 292
   things its replaced files define are then defined nowhere. With the game
   included, Cold Steel would have shown this warning before the build. This
   is the most valuable change.

2. **Trace a build's errors back to its source mods.** The error reader
   (`errors.py`) matches errors against
   the mods in `dlc_load.json`. With a build there's only one, so every error
   would be blamed on "Cold Steel build: Cold Steel Mix". The build record
   (`builds/<playset id>.json`) already says which mod each file came from
   (`BuiltFile.layer`), so the reader can use it.

3. **Read three more ways the log names files.**
   `error_log.py` misses or
   misreads these shapes, which leaves about 1,900 entries with no mod:
   - `in events/x.txtline: 6838`, with no space before "line" (all 1,104
     "Corrupt Event Table" entries).
   - `file: common/x.txt:747(inline_script) common/inline_scripts/y.txt line: 14`.
     The pattern takes everything up to "line" as one path. The first path
     (`common/x.txt`) is the one to match.
   - Chains like `common/a.txt:12 @ in scripted trigger t at file: b.txt`.
     The first path is where the problem is.

4. **Fold Universal Resource Patch's entries out of the count, as overrides
   are.** `strategic_resources_gui_group.cpp` errors only mean a top-bar
   resource isn't installed. Hiding them under a tick box would have taken the
   count from 11,463 to about 5,900. It's keyed on the game's source file, not
   on mod names, so it isn't the name list that decision 65 turned down.

5. **Explain "lost after a parse break" in the Errors view.** When a file
   stops parsing, everything after that point is gone, and the errors show up
   in other files. When the view finds an unexpected-token error, it could
   name the objects defined after that line, as this report does for the
   starbase buildings.

## How this was worked out

- Parsed `error.log` with Cold Steel's own `parse_error_log`.
- Took the load order from the launcher database's "Cold Steel Mix" playset
  (28 mods). Indexed every file in each Workshop folder (zips included) and in
  the game folder.
- Matched each error to the last mod in load order that has the file it names,
  as the game does. Errors naming a vanilla file were then checked against
  vanilla 4.5.1: where is the missing name defined, and whose copy of that file
  did the game read?
- Compared Ariphaos's copies with vanilla's, name by name.

**Limits.** The build folder (`~/.local/share/cold-steel/builds/`) isn't
mounted in the dev container, so the build and its record weren't opened. The
report assumes the build used the same load order as the launcher playset
(Cold Steel pushes playsets to the launcher). The small groups were sorted by
hand from the first file each error names. A few dozen entries there could
belong to a neighbouring row.
