# Error log report: Cold Steel Mix build, second run, 3 October 2026

**The build is now clean of the errors that break play.** The log has 5,674
entries, down from 11,463 this morning. Set aside the two harmless groups
(Universal Resource Patch's list and override notices) and 153 entries are
left, down from about 5,900.

None of the errors from Ariphaos Unofficial Patch (4.2) is back. The game read
4.5's own copies of the files Ariphaos used to replace. Starbases, Arkships,
advanced starts and the Shroud's aura emitters all load.

What's left is small and comes from five mods:

- **Starbase Extended 3.0** (56 entries) is the largest group. It replaces the
  citadel's gun layout, so the game's Starlit Starbase design loses four guns.
  A few of its bonuses point at buildings that don't exist.
- **Planetary Diversity - Unique Worlds** (23): two button shaders don't
  compile on Linux. Cosmetic.
- **Diverse Rooms** (28): names ethics and governments from other mods.
  Harmless.
- **Real Space family** (16). One new finding: Real Space - System Scale ships
  an old copy of a game graphics file. Starlit systems and Voidspawn storms
  lose their visual effect.
- **Planetary Diversity and More Events Mod** (8): start systems and one
  compatibility check refer to names that no longer exist.

The merge itself caused no errors. Nothing was logged in seven minutes of
play.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.1 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`) |
| Log | `logs/error.log`, 6,386 lines, 5,674 entries |
| Session | Started 11:37 (local time), one galaxy generated at 11:39, played to 11:46 |
| When the errors came | 5,621 while loading (11:37), 38 at 11:38, 15 at galaxy start (11:39). None after 11:39:36 |

## Compared with this morning

| Group | This morning | Now | Change |
|---|---:|---:|---|
| Ariphaos Unofficial Patch (its files and what it removed) | 5,361 | 0 | Gone |
| Universal Resource Patch: resources not installed | 4,754 | 4,754 | Same (harmless) |
| Override notices | 839 | 767 | 72 fewer: Ariphaos's own duplicates |
| Everything else | 509 | 153 | See below |
| **Total** | **11,463** | **5,674** | **−51%** |

"Everything else" fell for two reasons. The entries Ariphaos caused in other
mods (such as `ice_mining_station`) went with it. And this run made one galaxy
instead of three, so origin-specific errors didn't fire. Planetary Diversity's
55 `pddomebases.200` errors, for example, only happen with the Interplanetary
Settlers origin.

## Is Ariphaos really out?

**Its files aren't in what the game read.** The launcher's "Cold Steel Mix"
playset still lists it at position 0. But the build wasn't loaded through
that playset: `dlc_load.json` names only the build, and the build's record
isn't mounted in the dev container. So the check was made against the log:

- Every Ariphaos signature from this morning is at zero: "Corrupt Event Table
  Entry", "Unexpected token", Arkship component errors, `aura_emitter`,
  `any_system_colony` and the missing `game_start` events.
- 13 override notices name files Ariphaos has, but vanilla has them too. Each
  notice gives a line number. In 12 of the 13, that line opens the named event
  or effect in **vanilla's** copy. In Ariphaos's copy it's a `}` or the middle
  of another block. The 13th falls on an event opening in both copies. So the
  game read vanilla's files.
- No entry names a file that only Ariphaos has.

Either Ariphaos was removed from Cold Steel's playset before the rebuild, or
its old copies were left out. Both give this result.

**The launcher playset is out of date.** It still has Ariphaos, and was last
changed at 10:01 (local time), before the rebuild. If you start "Cold Steel
Mix" from the Paradox launcher rather than from Cold Steel, Ariphaos comes
back with all its errors. Run **File › Sync launcher** to bring it up to
date.

## What's left, by mod

| Mod | Entries | Matters? |
|---|---:|---|
| Starbase Extended 3.0 | 56 | A little: a few bonuses don't apply, one game design loses guns |
| Diverse Rooms (All in One) | 28 | No |
| Planetary Diversity - Unique Worlds | 23 | Cosmetic |
| Real Space 4.0, System Scale, Ships in Scaling | 16 | Cosmetic, plus 3 deposits without names |
| Planetary Diversity, More Events Mod | 8 | Only with certain starts |
| The game's own | 15 | No |
| Descriptors, Just Star Names, Apocryphos | 7 | No |
| **Total** | **153** | |

### Starbase Extended 3.0 (56)

This is the largest group, and it's bigger than this morning's report said.
Many of its entries name no file, so they had been put under "the game's own
noise". Searching every mod for the names in them shows they're all Starbase
Extended's.

| What's wrong | Entries | Effect |
|---|---:|---|
| Aquatic and toxoid starbase models ask for 8 hum sounds and 3 particle effects that don't exist | 19 | Those starbases are silent and lose a glow |
| Synthetic starbase models ask for an idle animation they don't have. A humanoid starport model asks for attach point `part4`. Three fallen-empire citadels ask for `.anim` files that don't exist | 11 | They just don't animate |
| Its citadel section (`CITADEL_STARBASE_SECTION`) has gun slots only up to `MEDIUM_GUN_09`. The game's Starlit Starbase design (Biogenesis hatchery) uses slots 010–013 | 4 | That design loses four guns |
| `SHIELD_ORBITAL_RING_SECTION` and `ARMOR_ORBITAL_RING_SECTION` are used but never defined | 2 | Those orbital ring designs are missing a section |
| `nsc_starbases.txt` uses `@build_block_radius_starbase` and `@starbase_formation_priority`. The game defines these only inside `15_starbases_megacorp.txt`, and other files can't see them | 4 | Two starbase sizes use default values |
| Six modules have two `potential` blocks | 6 | The game keeps one |
| Bonuses check for buildings `mining_manager` and `assembly_line_manufacturing`, which neither the mod nor the game defines | 5 | Those bonuses never apply |
| A building's `potential` uses `category = starbase_buildings`, which isn't a trigger | 2 | That check is broken. The building at line 1,145 may show when it shouldn't |
| Missing text key `nsc.requires.asteroid` | 1 | A tooltip shows the raw key |
| Its starbase view expects GUI elements `open_planet` and `design_name`, which 4.5 removed | 2 | Two items missing from the starbase window |

`nsc_` files are compatibility code for NSC, which isn't loaded
(decision 65 covers why we don't try to tell that apart).
Its descriptor says `v4.**.*`, which the game can't read (see
[Small things](#small-things)).

**Keep it.** Nothing here blocks play. The citadel gun slots and the two
undefined buildings are worth reporting to the author.

### Diverse Rooms (All in One) (28)

Same as this morning. Its portrait room picker
(`zzzz_room_textures.txt`) names ethics, civics, origins and authorities from
other mods (`ethic_dark_side`, `auth_cloning_*`, `gov_transcendent_*`) and one
missing trigger (`primary_species`). Those rooms are never picked. **Harmless.**

### Planetary Diversity - Unique Worlds (23)

- 22 entries: shaders `buttonstate_rendertarget_pd_biosynth.shader` and
  `…_holo.shader` use `pow(vec3, float)`. DirectX accepts that, but OpenGL on
  Linux doesn't. Some biosynth buttons render plain. Worth reporting to the
  author: the fix is `pow(x, vec3(y))`.
- 1 entry: two origins exclude species class `CRYO`, which the game doesn't
  define. Harmless.

### Real Space family (16)

| Mod | Entries | What's wrong |
|---|---:|---|
| Real Space - System Scale | 9 | **Ships an old copy of `gfx/models/effects/_system_effects_entities.asset`.** It has 10 entities. The game's 4.5 file has 21. The five it drops are all from Biogenesis: `starlit_core_entity`, `starlit_core_2_entity`, `starlit_core_stars_entity`, `starlit_effect_entity` and `voidspawn_storm_entity`. Starlit systems and Voidspawn storms fall back to a plain effect (2 entries). Also asks for 6 infernal ring world textures that don't exist, and changes system zoom steps without matching planet scales (1 entry) |
| Real Space 4.0 | 5 | Three dark matter deposits (`rs_d_dark_matter_deposit_1`–`3`) have no name text. Two `nospec.dds` texture mix-ups |
| Real Space - Ships in Scaling | 2 | Modifiers `fire_rate_reduction` and `hp_increased` have no text |

The System Scale finding is new. It's the same kind of problem as Ariphaos,
only much smaller: an old copy of a game file hides what the new version
added. Cold Steel's "old copies" check can't catch it, for two reasons. The
mod says `v4.5.*`, so it isn't older than the game. And the check reads
definitions in script files, not entity names in `.asset` files. See
[What Cold Steel could change](#what-cold-steel-could-change).

**Keep them.** The missing Starlit and Voidspawn effects are cosmetic. They'd
come back if System Scale's copy were left out of the build. That can't be
done today without editing the mod.

### Planetary Diversity and More Events Mod (8)

- 6 entries: start systems in PD's `!vanilla_sol_initializers_ow.txt` and
  `pd_habitat_start.txt`, and in More Events Mod's
  `mem_eden_protocol_initializers.txt`, refer to `sol_neighbor_t1`/`t2`. The
  game defines those in `sol_initializers.txt`, but Real Space 4.0 replaces
  that file and renames the Sol neighbours to real stars. These matter only
  for PD's habitat start and More Events Mod's Eden Protocol.
- 2 entries: More Events Mod's compatibility code for Planetary Diversity
  (`mem_asp_scfe_triggers.txt` line 171) calls `is_pd_planet_for_aqua_trait`.
  PD no longer defines it. One anomaly's aquatic check fails on PD ocean
  worlds.

### The game's own (15)

These name only vanilla files and trace to no mod:

- 8: message titles (`MESSAGE_RESOLUTION_VETOED_TITLE`, an Astral Rift message)
  are checked at start without the scopes they need. Vanilla text.
- 6: `is_individual_machine` asks for `founder_species` on a fallen empire
  ("Elven Divine Order"), which has none. Vanilla script in
  `02_scripted_triggers_machine_age.txt`.
- 1: an empire design's species was missing `trait_organic`.

### Small things

- 5 `.mod` descriptors with `supported_version` values the game can't read
  (Universal Resource Patch, Starbase Extended, Just Star Names, Cinematic
  Camera and one more). The game reads every `.mod` file, loaded or not.
- Just Star Names (Continued): format error at line 5,852 of
  `09random_names_l_english.yml`. At most a few names are skipped.
- Apocryphos: one track isn't 44.1 kHz. A performance note, not an error.

## Did the merge cause anything?

**No sign of it.** Every entry that names a file maps to a file in one of the
source mods or in the game. None names a file that only exists in the build.
The line-number check above shows the game read the expected copy byte for
byte.

## What to do

1. **Run File › Sync launcher**, so the launcher's "Cold Steel Mix" matches
   Cold Steel's and no longer has Ariphaos.
2. **Nothing else is needed to play.**
3. Optional: report Starbase Extended's citadel gun slots and undefined
   buildings, and PD Unique Worlds' Linux shaders, to their authors.

## What Cold Steel could change

These are suggestions, not decisions. Each would become a row in
decisions.md if taken up.

1. **Warn when the launcher's copy of a playset differs from Cold Steel's.**
   Here the launcher still had a mod that broke the game, and nothing said so.
   A note on the playset ("the launcher's copy differs. Sync?") would have
   caught it. Decision 67 already makes syncing possible.

2. **Run the "old copies" missing-definitions test on `gfx/**/*.asset`
   entity names too.** The System Scale copy drops 5 game entities. Its
   version (`v4.5.*`) means the version test in
   decision 63 would still keep it quiet. So this only
   helps if a mod that replaces game files and leaves game entities defined
   nowhere is worth a softer note, whatever its version. That's a real change
   to decision 63, so it needs weighing against the false alarms that
   decision was made to avoid.

3. **Attribute errors that name no file, by searching for the name they
   quote.** 75 of the 153 entries name no file ("Missing sound effect: x",
   "Failed to get section template for key: x"). This report found the owner
   of all of them by searching the build's files for the quoted name. The
   build record knows which mod each file came from, so the Errors view could
   do the same, at least for sounds, textures, entities and section
   templates. Most of the "Game / unknown" group would go.

## How this was worked out

- Parsed `error.log` with Cold Steel's own `parse_error_log`, and set aside
  overrides and missing resources with `is_override` and
  `is_missing_resource`.
- Indexed every file in the 28 source mods' Workshop folders (zips included)
  and in the game folder. Matched each entry to the last mod in load order
  that has the file it names.
- For entries naming no file, searched every mod and the game for the name
  quoted in the entry.
- Compared the line numbers in the 13 override notices against vanilla's and
  Ariphaos's copies.
- Compared Real Space - System Scale's `_system_effects_entities.asset` with
  vanilla's, entity by entity.

**Limits.** The build folder and Cold Steel's own playsets
(`~/.local/share/cold-steel/`) aren't mounted in the dev container. So the
build's file list and its record weren't opened, and how Ariphaos came out of
the build is inferred from the log, not seen. The load order used for tracing
is the launcher playset's. That matches the build everywhere except Ariphaos,
judging by the log. This run made one galaxy and played seven minutes, so
errors that need a particular origin, crisis or event chain may not have
fired.
