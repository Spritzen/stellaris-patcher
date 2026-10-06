# Error log report: Cold Steel Mix build, third run, 3 October 2026

**121 entries point at real problems, down from 153 in run 2. None of them
stops play.** The log has 6,590 entries. 5,717 are Universal Resource Patch
listing resources you don't have, and 752 are override notices. Both groups
are harmless.

What's left comes from five places, and most of it can be fixed by a patch
mod:

- **Starbase Extended 3.0** (56 entries) is still the largest group. Two of
  its problems change play. The game's Starlit Starbase design loses four
  guns, because Starbase Extended renamed the citadel's gun slots. And two of
  its starbase sizes lose their build-block radius and formation priority.
- **Diverse Rooms** (28) names ethics and governments from mods you don't
  have. Harmless.
- **Real Space family** (16). New this run: **Cinematic Camera and Real Space -
  System Scale disagree on the system zoom steps**, so planets may be drawn
  at the wrong size at some zoom levels.
- **Planetary Diversity and More Events Mod** (9) ask for things under names
  that other mods have since changed.
- **The game's own script** (5).

Two findings come from the files, not the log. A 5-minute run can't trigger
them:

- **Real Space - System Scale's old copies drop 116 of the game's graphics
  entities**: 87 Dyson sphere models, 24 quantum catapult models, and 5
  Starlit and Voidspawn effects. Only the last two showed up in this log.
  The rest appear once someone builds one of those megastructures.
- **The merge caused nothing.** The build record was saved seconds before this
  run and matches it. Every entry that names a file traces back to a source
  mod or to the game.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.1 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`) |
| Built | 13:11 local time, from the 26-mod playset, just before the game started |
| Log | `logs/error.log`, 6,618 lines, 6,590 entries |
| Session | Started 13:12, one galaxy generated at 13:13, played to 13:17 |

The playset has 26 mods. Since run 2, **Planetary Diversity - Unique
Worlds** has been removed, and its 23 shader errors went with it. The
launcher's copy of Cold Steel Mix now matches Cold Steel's exactly, the same
mods in the same order. So run 2's warning about an out-of-date launcher
playset is resolved.

## Compared with run 2

| Group | Run 2 | Run 3 | Change |
|---|---:|---:|---|
| Universal Resource Patch: resources not installed | 4,754 | 5,717 | One more file read (see below) |
| Override notices | 767 | 752 | About the same |
| Problems | 153 | 121 | −32 |
| **Total** | **5,674** | **6,590** | |

The problems fell because Unique Worlds left the playset (−23), and because
this run's galaxy didn't fire the game's message-title errors (−8).

Universal Resource Patch rose by one file of about 950 lines. It ships six
resource lists. One of them, `tp_compact_ui_others_group_2 .txt`, has a space
in its name, and this run read it. Still harmless: each line is a resource
from a mod you don't have.

## What's left, by mod

| Mod | Entries | Matters? |
|---|---:|---|
| Starbase Extended 3.0 | 56 | A little: one game design loses four guns; two starbase sizes and a few bonuses don't work as meant |
| Diverse Rooms (All in One) | 28 | No |
| Real Space family, with Cinematic Camera | 16 | Cosmetic |
| Planetary Diversity, More Events Mod | 9 | Only with certain starts, plus one anomaly check |
| The game's own | 5 | No |
| Descriptors, Just Star Names, Apocryphos | 7 | No |
| **Total** | **121** | |

Cold Steel's error reader put 18 entries under "Game / unknown". 13 of them
belong to mods, by the files or names they mention, and are counted under
those mods here.

### Starbase Extended 3.0 (56)

| What's wrong | Entries | Effect | Cause, checked in the files |
|---|---:|---|---|
| The game's Starlit Starbase design asks for slots `MEDIUM_GUN_010`–`013` | 4 | That design loses four guns | 4.5 names the citadel's extra slots with three digits (`MEDIUM_GUN_010`). Starbase Extended replaces `CITADEL_STARBASE_SECTION` and names them `MEDIUM_GUN_10`–`20` |
| `nsc_starbases.txt` uses `@build_block_radius_starbase` and `@starbase_formation_priority` | 4 | Two starbase sizes have no build-block radius or formation priority | The game defines these at the top of each of its own ship-size files (`= 20` and `= 1`). A variable is only seen inside its own file |
| `SHIELD_ORBITAL_RING_SECTION` and `ARMOR_ORBITAL_RING_SECTION` are used but never defined | 2 | Two orbital ring modules have no section | Neither the mod nor the game defines them |
| Six modules have two `potential` blocks | 6 | The game keeps one, so a condition is lost | Lines 101, 144, 433 of `sbx_3_0_orbital_ring_modules.txt`, and 183, 238, 290 of `sbx_3_0_starbase_modules.txt` |
| Bonuses check for buildings `mining_manager` and `assembly_line_manufacturing` | 5 | Those bonuses never apply | Neither the mod nor the game defines either building |
| A building's `potential` uses `category = starbase_buildings` | 2 | The check is broken, so the building may show where it shouldn't | `category` isn't a trigger. Line 1,145 of `sbx_3_0_starbase_buildings.txt` |
| Missing text key `nsc.requires.asteroid` | 1 | A tooltip shows the raw key | No mod in the playset defines it |
| Its starbase view expects `open_planet` and `design_name` | 2 | Two items missing from the starbase window | The game's and UI Overhaul's `starbase_view.gui` have them. Starbase Extended's `zzz_sbx_3_0_starbase_view.gui` replaces those windows without them |
| Aquatic and toxoid starbases ask for 8 hum sounds and 3 particle effects that don't exist | 19 | Those starbases are silent and lose a glow | The names (`amb_aquatic_starbase_hum_01`…) exist nowhere in the game |
| Synthetic starbases ask for an idle animation they don't have; a starport asks for attach point `part4`; three fallen-empire citadels ask for `.anim` files that don't exist | 11 | They just don't animate | |
| Its descriptor says `v4.**.*` | 1 | None | The game can't read that version |

### Diverse Rooms (All in One) (28)

Same as run 2. The portrait room picker (`zzzz_room_textures.txt`) names
ethics, civics, origins and governments from other mods (`ethic_dark_side`,
`auth_cloning_*`, `gov_transcendent_*`), and one trigger that doesn't exist
(`primary_species`). Those rooms are never picked. **Harmless.**

### Real Space family, with Cinematic Camera (16)

| Mod | Entries | What's wrong |
|---|---:|---|
| Real Space - System Scale | 8 | Six infernal ring world textures it asks for don't exist. Starlit systems and Voidspawn storms fall back to a plain effect, because its old copy of `_system_effects_entities.asset` drops them (2 entries; see [below](#found-in-the-files-real-space---system-scales-old-copies)) |
| System Scale **and** Cinematic Camera | 1 | **New.** `PLANET_SCALE_SYSTEM does not match in size with ZOOM_STEPS_SYSTEM`. System Scale sets 8 zoom steps and 8 matching planet scales. Cinematic Camera loads later and sets 13 zoom steps, but no planet scales. So the 13 steps meet System Scale's 8 scales, and planets may be drawn at the wrong size at some zoom levels. The two mods also both set 17 other camera values, and Cinematic Camera's win |
| Real Space 4.0 | 5 | Three dark matter deposits (`rs_d_dark_matter_deposit_1`–`3`) have no name text. Two `nospec.dds` texture mix-ups |
| Real Space - Ships in Scaling | 2 | Modifiers `fire_rate_reduction` and `hp_increased` have no text |

### Planetary Diversity and More Events Mod (9)

- **Sol neighbours (6 entries).** Planetary Diversity's
  `!vanilla_sol_initializers_ow.txt` and `pd_habitat_start.txt`, and More
  Events Mod's `mem_eden_protocol_initializers.txt`, ask for the game's
  `sol_neighbor_t1`, `sol_neighbor_t2` and
  `sol_neighbor_t1_no_guaranteed_colony`. Real Space 4.0 replaces the game's
  `sol_initializers.txt` and renames them after real stars
  (`alpha_centauri_mediumsector`, `sirius_mediumsector`, `bernards_star_mediumsector`…).
  It matters only for Sol starts that use those neighbours.
- **A renamed trigger (2 entries).** More Events Mod's compatibility code for
  Planetary Diversity (`mem_asp_scfe_triggers.txt` line 171) calls
  `is_pd_planet_for_aqua_trait`. Planetary Diversity now calls it
  `pd_is_planet_for_aqua_trait`. One anomaly's aquatic check fails on PD
  ocean worlds.
- **One graphics note (1 entry).** An empire switched to More Events Mod's
  ship set `mem_ancient_01`, which resets its ship designs. This is a
  notice, not an error.

### The game's own (5)

- 4: `is_individual_machine` asks for `founder_species` on a fallen empire
  ("Elven Divine Order"), which has none. Vanilla script, in
  `02_scripted_triggers_machine_age.txt` line 64.
- 1: an empire design's species was missing `trait_organic`.

### Small things (7)

- 5 `.mod` descriptors with `supported_version` values the game can't read:
  Universal Resource Patch, Starbase Extended, Just Star Names, Cinematic
  Camera, and ASB Ironman (not in the playset; the game reads every `.mod`
  file). Harmless.
- Just Star Names: line 5,852 of `09random_names_l_english.yml` is
  `Siyāvash:0"Siyāvash"`. A key can't hold `ā`, so the game skips that one
  name.
- Apocryphos: one track isn't 44.1 kHz. A performance note.

## Found in the files: Real Space - System Scale's old copies

**System Scale replaces seven of the game's graphics files, and three of
them are old copies that drop 116 of the game's entities.** It says it's made
for `v4.5.*`, so its version gives no warning. Cold Steel's "old copies"
check finds it, with a softer note, and finds nothing else in the playset.

| File | Game's entities | System Scale's | Dropped |
|---|---:|---:|---|
| `gfx/models/ships/megastructures/dyson_sphere/_dyson_sphere_entities.asset` | 224 | 137 | 87: the newer styles' Dyson spheres (Biogenesis, Cybernetics, Synthetics, Psionic, Infernal, Toxoid, Mindwarden) |
| `gfx/models/ships/megastructures/quantum_catapult/quantum_catapult_01.asset` | 70 | 46 | 24: the same seven styles' catapult stages |
| `gfx/models/effects/_system_effects_entities.asset` | 9 | 4 | 5: four Starlit effects, `voidspawn_storm_entity` |

The other four files (`_nebula_entities`, `_cosmic_storms_effects_entities`,
`_planetary_entities` and `dyson_swarm`) keep every game entity. Each copy's
only change is scale: a fixed number becomes a variable defined at the top of
the file, such as `scale = 20` → `scale = @entity_scale_20`, with
`@entity_scale_20 = 120`.

So a megastructure in one of the newer styles is built with no model, or a
fallback one. In this log it showed up only as the two Starlit and Voidspawn
entries, because no one built one in five minutes.

## Did the merge cause anything?

**No.** Cold Steel traced each entry through the build's record, and the
record was saved seconds before the game started, so it matches this run.
Every entry that names a file maps to a file in one of the 26 source mods or
in the game.

## What a patch mod could fix

These go into the plan for the Cold Steel Mix patch mod. "Sure" means the
cause is confirmed in the files and the fix only touches that cause.

| # | Problem | Fix in the patch mod | Sure? | Worth it? |
|---|---|---|---|---|
| 1 | System Scale drops 116 entities | Ship the game's 4.5 copies of the three files, with System Scale's scale variables applied | Yes | **Yes**: three kinds of megastructure have models again |
| 2 | Starlit Starbase loses four guns | Add `MEDIUM_GUN_010`–`013` to Starbase Extended's citadel section, or point the design at its `_10`–`_13` | Yes | Yes |
| 3 | Two starbase sizes lose two values | Ship `nsc_starbases.txt` with the two variables defined at the top | Yes | Yes |
| 4 | Zoom steps and planet scales disagree | Set `PLANET_SCALE_SYSTEM` to 13 values matching Cinematic Camera's steps, or keep System Scale's 8 steps | Needs a choice | Yes, if planets look wrong in game |
| 5 | Sol neighbours renamed | Define the game's three old names again as copies of Real Space's matching systems | Yes | Only for those starts |
| 6 | MEM's renamed PD trigger | Define `is_pd_planet_for_aqua_trait` to call `pd_is_planet_for_aqua_trait` | Yes | Small |
| 7 | Missing text: 3 deposits, 2 modifiers, `nsc.requires.asteroid` | Add the six keys in one localisation file | Yes | Small |
| 8 | Duplicate `potential` blocks, the `category` trigger, two missing buildings | Ship fixed copies of the affected modules and building | Needs reading what the author meant | Small |
| 9 | Missing orbital ring sections, starbase window items, sounds, animations | Define or point at existing ones | Needs more work | Cosmetic |
| — | Diverse Rooms, descriptors, Just Star Names, the game's own | Leave alone | | No |

## How this was worked out

- Ran Cold Steel's own error reader (`ErrorReader`) read-only, from its
  mounted source, with its cache in a scratch folder. It reads `error.log`,
  traces each entry through the build record to its source mod, and finds
  the owner of names quoted in entries that name no file. It also sets
  aside overrides and missing resources.
- Moved 13 entries from "Game / unknown" to the mods their files or names
  belong to: the three `.anim` files and the four citadel slots to Starbase
  Extended, the two entities and the zoom mismatch to System Scale, and so on.
- Ran Cold Steel's index, conflict finder and old-copies check over the
  playset, read-only, the same way. It found 631 mod-against-mod conflicts
  and one old copy.
- Checked each cause by hand in the mods' and the game's files: gun slot
  names, where the variables are defined, the zoom arrays in the three
  defines files, the Sol initializer names, PD's trigger name, the
  `.asset` entity lists.
- Compared the launcher's playset with Cold Steel's, mod by mod.

**Limits.** One galaxy and five minutes of play, so errors that need a
particular origin, crisis or megastructure may not have fired. Whether the
zoom mismatch makes planets look wrong was not checked in game.
