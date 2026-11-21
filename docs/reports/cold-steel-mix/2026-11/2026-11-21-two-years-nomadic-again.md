# Two years as a Nomadic empire, again: Cold Steel Mix, 21 November 2026

**A second two-year run as the same Nomadic empire, in a new galaxy,
logged the same 1,708 ACoT entries as the first, because it still had fix
44's first version.** Fix 44's change, which takes ACoT's sizes out, was
made after the first run but not written: the patch's trigger file is still
the 20:58 one. Cold Steel rebuilt the playset at 21:25 from that patch. The
other 45 problems are the same as the first run's, less More Events Mod's
game start notice. Play logged nothing. No new fix is proposed. Write the
patch and rebuild, and the next run should show the 1,708 gone.

- **The 1,708 are the first run's.** 61 for each of ACoT's 28 sizes, from
  the patch's `zzzz_stellaris_patcher_cold_steel_mix_starbase_components.txt`,
  lines 32 to 58 and 60, as in the
  [first run](2026-11-21-two-years-nomadic.md#acots-ship-sizes-1708).
- **Fix 44 still holds.** Every one of the 105 default tier-3 arkship
  designs in the save has `COMBAT_COMPUTER_ARKSHIP` and a juggernaut
  reactor. The player's arkship is again the tier-1 science arkship.
- **The patch held.** The build's 75 patch files match our folder byte for
  byte. 41 duplicate object notices name the patch's files, as in the first
  run. None of the names the fixes removed are in the log.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.4 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last |
| Patch | The local copy, written at 20:58 with all 32 fixes and fix 44's first version. Its 75 files in the build match our patch folder byte for byte |
| Built | The Cold Steel build at 21:25, from the 20:58 patch. The build record has no mismatches |
| Session | Started 21:25:24. The galaxy was made at 21:26:35, with a new seed. The ironman save reached 2202.02.08 at 21:30:08 |
| Empire | Gundersen Research Society again: Lost Colony, Nomadic, one tier-1 science arkship |
| Logs | `error.log`: 8,311 entries. 5,724 resources not installed, 834 override notices and 1,753 problems, all from loading and the empire designer. None from game start or play |

## Compared with the first run

| Group | [First run](2026-11-21-two-years-nomadic.md) | This run | Change |
|---|---:|---:|---|
| Starbase Extended 1.3.6's ACoT sizes, while loading | 1,708 | 1,708 | None: fix 44's change isn't written yet |
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| The game's own, while loading | 1 | 1 | None: the missing `trait_organic` |
| The game's `founder_species` check, in the empire designer | 3 | 3 | None |
| More Events Mod, at game start | 1 | 0 | Its ancient empire's culture notice didn't log. A different galaxy |
| In play | 0 | 0 | None |
| **Total** | **1,754** | **1,753** | |

Override notices are the first run's, group for group: 288 duplicate
objects, 480 entities, 23 section templates, 31 events and 12 variables.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 48 | ACoT's 1,708 load entries | Already fixed in the code. **Write the patch**: close the game and the Paradox launcher, run `cold-steel-mix --write`, then rebuild Cold Steel Mix in Cold Steel. The next run's log should have no `acot_` entry |
| — | A tier-3 arkship in play | Not reached, as in the first run |

## How it was worked out

- As for the [first run](2026-11-21-two-years-nomadic.md#how-it-was-worked-out):
  `error.log` read with our
  [error_log.py](../../../../src/stellaris_patcher/paradox/error_log.py),
  split by time with `game.log`, and grouped by source and text. The last
  entry is at 21:26:18, before the galaxy was made.
- The patch folder's trigger file time, 20:58, was compared with the
  change to fix 44, and the build record's time, 21:25.
- The build's patch files were compared with our folder, and the
  duplicate object notices matched to the patch's files.
- The ironman save was unpacked to a scratch folder, and its arkship
  designs and the player's arkship read.

## Limits

- **It doesn't test fix 44's change.** The patch it played is the one
  before it.
- **About four minutes of play** for two years. Little happened beyond
  first contacts.
