# Game report: Cold Steel Mix quick check with fix 36, 10 October 2026

**A new galaxy as the Sathyrel, played for three years, to 2203.01.25, as a
quick check of the rebuilt patch. It's the first run with fix 36 in the
build. The patch held, and play logged nothing. The log matches the
[ten years](2026-10-10-cold-steel-mix-ten-years.md) run, apart from three
entries that depend on the galaxy and on who's played. All three were seen
before. The user saw nothing unusual. Nothing new to fix.**

- **Fix 36 is in the build but wasn't reached.** The save has no specimens
  yet, so no More Events Mod specimen text was shown. Its check is still to
  do. See [The patch's fixes](#the-patchs-fixes).
- **The 18 Life-Seeded checks at galaxy creation are back,** because the
  user played a premade, not their saved Divine Elven Order design. The
  [UNE five years report](2026-10-09-cold-steel-mix-une-five-years.md)
  found that pattern.
- **More Events Mod's two galaxy-dependent entries are back**: the Lost
  Emperor's system couldn't be placed (item 20, left to its author), and an
  empire switched to its `mem_ancient_01` ship set.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.10`, with fix 36 in a build for the first time. Its 69 files in the build match our source folder byte for byte |
| Built | The Cold Steel build at 15:34 on the log's clock. The build record has no mismatches |
| Session | Started 15:34:57. New galaxy, seed 1362168225, made at 15:36:02: medium, `spiral_3`, 18 empires, one Fallen Empire, one Marauder, late scaling. Played to `2203.01.25`, saved at 15:41. About six minutes of play |
| Empire | Sathyrelian Bliss, the `EMPIRE_DESIGN_sathyrel` premade, Ocean Paradise origin |
| Logs | `error.log`: 6,614 entries. 5,717 resources not installed, 832 override notices and 65 problems: 44 from loading and game start, 21 from the game's Life-Seeded check, none from play |

The log's clock is one hour ahead of the file times, as before. The last
entry is at 15:36:17, at game start.

## Compared with the ten years run

| Group | Ten years | This run | Change |
|---|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| The game's own | 1 | 1 | None: the missing `trait_organic` |
| More Events Mod, at game start | 0 | 2 | The Lost Emperor spawn and the ship set notice. Both depend on the galaxy |
| More Events Mod, in play | 3 | 0 | The holo projector's text. No specimen was shown this run |
| Starbase Extended 3.0 | 0 | 0 | None |
| The game's Life-Seeded check | 4 | 21 | +17: 3 in the designer and 18 at galaxy creation, as Divine Elven Order wasn't played |
| **Total** | **49** | **65** | |

The override notices are the same 832, kind for kind: 286 duplicate objects,
480 entities, 23 section templates, 30 events, 12 variables and Real Space's
initializer.

## The patch's fixes

**None of the names the fixes removed are in the log**, the same list as the
[ten years](2026-10-10-cold-steel-mix-ten-years.md#the-patchs-fixes) run.
Its one `ion_core_effect` is a duplicate entity notice, and its one
`solar_system` is fix 17's initializer notice.

**The game uses every copy the patch ships.** 35 duplicate object notices
name the patch's files, as last run. The duplicate event notices for fixes
11, 12 and 26, and fix 17's initializer notice, name the mods' own files, so
the patch's copies win.

| Fix | In game |
|---|---|
| 36 | **Not reached.** Its `replace/` file is in the build. The save has no specimens yet, so no specimen text was shown. The log has no `Unknown promotion` |
| 32 | No `Duplicate trigger`, as last run |
| 31 | No attach point, sound, particle or animation entries |

## Loading and game start (44)

The same 42 as the last run, group for group, and More Events Mod's two at
game start:

- **The Lost Emperor's system couldn't be placed** (15:36:17).
  `test_spawn_neochadamus` at line 28 of
  `mem_descended_scripted_effects.txt` asks for a system that connects 4 to 8
  jumps from home, and there wasn't one. The story is lost in this galaxy.
  More Events Mod's own code, item 20, left to its author
  ([decision 41](../decisions.md)). The
  [pre-upload report](2026-10-07-cold-steel-mix-pre-upload.md#more-events-mod-2)
  traced it.
- **An empire switched to More Events Mod's `mem_ancient_01` ship set**
  (15:36:05). A notice, not an error. Seen in run 3 and later.

## The game's Life-Seeded check (21)

3 at 15:35:48, in the empire designer, and 18 at 15:36:02, as the galaxy was
made. All name the user's saved Divine Elven Order design, a Life-Seeded
empire, which isn't in this galaxy. The game's own. The 18 come when that
design is saved but not played, as the
[UNE five years report](2026-10-09-cold-steel-mix-une-five-years.md) found.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 36 | Fix 36 isn't checked in game | Open the Grand Archive on a More Events Mod specimen when one turns up: it should say where it was found, with no blank, and the log should have no `Unknown promotion From`. The specimens are rare |
| 1 | Still unchecked in play | As in the [ten years](2026-10-10-cold-steel-mix-ten-years.md#what-to-do-next) report |
| — | This report, the ten years report and fix 36 aren't committed | Commit them |

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../src/stellaris_patcher/paradox/error_log.py), and
  grouped it as the last report did.
- Split the entries by time. The galaxy was made at 15:36:02 (`game.log`).
  The last entry is at 15:36:17.
- Read the build record, and compared the patch's 69 files in the built mod
  with the patch folder byte for byte.
- Searched the raw log for each name the fixes removed, and read the
  duplicate object, event and initializer notices for the patch's copies.
- Unpacked the `2203.01.25` save into a scratch folder: the player's empire,
  the empires' origins, the galaxy settings, and the Grand Archive's
  specimens (none).

## Limits

- **Six minutes of play.** Most of what the fixes cover, from starbase
  upgrades to specimens, wasn't reached.
- **What happened on screen.** The user saw nothing unusual. Visual problems
  don't reach the logs.
