# Twelve years as the Divine Elven Order: Cold Steel Mix, 28 November 2026

**Twelve years of a new game, which the user will keep playing, logged 74
problems, 24 of them in play, and nothing looked wrong. All are harmless,
and no fix is proposed.** Against the [last run](2026-11-25-two-years-4.6.0-uiod.md),
two kinds of entry are new, and both are the game's own:

- **8 of the game's message titles logged at the main menu.** Four
  notification titles, for the galactic council and the Nomads' Astral
  Rift, name a country or system, and nothing was there to name. It came a
  second after loading ended and before the galaxy was made. No earlier log
  has it.
- **The Mindwarden enclave sold Zro to itself once.** The game's
  `shroud.4250` ran with the enclave as `root`, so its `add_trust` on
  itself was refused. The player wasn't involved.

Also:

- **The patch held.** The build's 69 patch files match our folder byte for
  byte, and a fresh build from the code matches them too. The patch loads
  last. No playset mod has updated since 25 November.
- **The game went quiet after 12:32.** The last entry is 42 minutes before
  the save at 13:14, which reached 2212.01.14.

## The run

| | |
|---|---|
| Game | Stellaris 4.6.0 (Corona Borealis), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 26 mods with `Cold Steel Mix patch` last |
| Patch | The local copy with all 35 fixes, written on 25 November at 18:40. Its 69 files in the build match our patch folder byte for byte |
| Built | Cold Steel rebuilt it at 12:00, with the same mods as the build of 25 November. The build record has no mismatches |
| Session | Started 12:00:55. The galaxy was made at 12:03:10, with a new seed: medium, `spiral_3`, 18 empires, one Fallen Empire. The ironman save reached 2212.01.14 at 13:14 |
| Empire | Divine Elven Order: a theocratic monarchy with the Life-Seeded origin, Ascensionists and Chosen. The Caravaneers are off (`caravaneers_enabled=no`) |
| What the user saw | Nothing out of place. The user will continue this game |
| Logs | `error.log`: 6,690 entries. 5,724 resources not installed, 892 override notices and 74 problems. 42 while loading, 8 at the main menu, 24 in play |

## Compared with the last run

| Group | [Last run](2026-11-25-two-years-4.6.0-uiod.md) | This run | Change |
|---|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 7 | 6 | −1: UI Overhaul Dynamic's "Could not find files for mod" is gone. It comes only after its updates, and it hasn't updated since |
| The game's own, while loading | 1 | 1 | None: the missing `trait_organic` |
| **The game's message titles, at the main menu** | 0 | **8** | New. See [Message titles at the main menu](#message-titles-at-the-main-menu) |
| More Events Mod's graphical culture, at game start | 1 | 0 | Its ancient empire culture notice didn't come. A different galaxy |
| Overlord holdings, in play | 21 | 21 | None: 19 in the game's `15_overlord_holdings.txt`, 1 in Ascension Worlds' and 1 in More Events Mod's, all at 12:14:21 |
| The game's policies, in play | 0 | 1 | `capital_scope` for the pre-FTL Voldareen Civilization, as in two runs on 24 November |
| The game's `Planet.GetName` text, in play | 1 | 1 | None |
| **The Mindwarden enclave's Zro sale, in play** | 0 | **1** | New. See [The Mindwarden enclave](#the-mindwarden-enclave) |
| **Total** | **66** | **74** | |

Override notices: 892, as last run. 342 duplicate objects, 484 entities,
31 events, 23 section templates and 12 variables.

## Message titles at the main menu

All 8 entries are at 12:01:40. `time.log` puts the end of loading at
12:01:39, and the galaxy came at 12:03:10. They are 4 titles from the
game's `localisation/english/`:

| Key | Text | Entries |
|---|---|---:|
| `MESSAGE_RESOLUTION_VETOED_TITLE` | `[global_event_country.GetGalCouncilOrImpCouncil] Veto called` | 1 |
| `MESSAGE_COUNCIL_ELECTION_RESULT_TITLE` | `… Elections Concluded` | 1 |
| `MESSAGE_RESOLUTION_EMERGENCY_MEASURE_TITLE` | `… Emergency Measure Declared` | 1 |
| `MESSAGE_ASTRAL_RIFT_STAGE_FINISHED_NOMAD_PERMISSION_TITLE` | `The [owner.GetName] Nomads have explored the $ASTRAL_RIFT$ in [fromfrom.solar_system.GetName]…` | 5 |

Each is a notification title in the game's `common/message_types/00_message_types.txt`.
No mod in the build ships any of these keys. Its six message type files,
from More Events Mod, Planetary Diversity and Ascension Worlds, add their
own types only.
The titles name a country or a system, and at the main menu there's none,
so the game logs each name it can't fill. Nothing in the logs says what
showed them. A screen listing the message types, such as the
notification settings, would. Neither earlier log kept in `logs/`, nor any
report, has them.

## The Mindwarden enclave

One entry, at 12:32:15:

```
add_trust: trying to add trust on oneself at file: events/shroud_events.txt line: 10138
```

The file is the game's own: the build has no `events/shroud_events.txt`,
and no mod names `shroud.4199`, `shroud.4200` or `shroud.4250`. Line 10138
is in `shroud.4250`'s option c, which sells Zro to the Mindwarden enclave:
`event_target:mindwarden_enclave_country` adds trust to `root`. The save
shows `root` was the enclave itself. The enclave's country has the flags
that option sets, `mindwarden_zro_cooldown` and `mindwarden_zro_timer`,
and `closed_mindwarden_diplomacy`. The player's country has none of them.

So the enclave ran its own Zro dialog once. The game refused the trust on
itself, and the enclave traded Zro for energy with itself. The
Shroudwalkers' trust in it dropped by the option's usual amount. The
option has a 3,600-day cooldown, so this can come at most once in ten
years. The game guards against the same thing in `shroud.4199`, with
`NOT = { is_same_value = prev }`, but not here. Harmless.

## The patch's fixes

| Fix | In this run |
|---|---|
| 47, 48 | `mega_shipyard_init_01`, `wenkwort_initializer` and Stewart's Resolve are in the save. No duplicate system or `Unexpected token` |
| 46 | No shader error. No Unbidden came |
| 1 | No Inquisitor-style country: the save has no `crusader_01`. Its 4 `crusader_01` log lines are duplicate entity notices |
| 43, 44, 45 | No `sc_quaternary_1`, `acot_` size or `has_megacorp` logged. The 30 `acot_` lines are Universal Resource Patch's missing resources |
| All others | Nothing logged against them. 48 override notices name the patch's files |

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 62 | 8 of the game's message titles logged at the main menu | None. The game's own text, with nothing to name yet. Watch whether more runs log them |
| 63 | The Mindwarden enclave's `add_trust` on itself | None. The game's own `shroud.4250`, and harmless. A fix could ship a copy of that one event with an `is_same_value` check ([decision 23](../../../decisions.md)), but the copy would hide the game's own changes to the event, for one refused trust change every ten years at most |
| 60 | 21 overlord holding errors in play | None, as before. The game's own 4.6 files |
| — | This game | The user will continue it. Read the log again after the next session, when the galaxy is further on: more AI federations, the galactic council, perhaps the Unbidden for fix 46 |
| — | Fix 1's left-out Inquisitor phase-3 entity, fix 45 | As before: an Inquisitor-style ring world, and a galaxy with the Caravaneers on |

## How it was worked out

- `error.log` read with our
  [error_log.py](../../../../src/stellaris_patcher/paradox/error_log.py),
  split by time with `game.log` and `time.log`, and grouped as in the last
  run. Resource and override notices were counted apart.
- The build record of 12:00 was read: the patch is last, its 69 files
  match our folder, and there are no mismatches. A fresh plan from the
  code gives the same 69 files byte for byte.
- Steam's `appworkshop_281990.acf` was read for each mod's update time.
  The newest is UI Overhaul Dynamic's, on 25 November.
- Each new entry's file was looked up in the build record, and the game's
  copy read at its line. The four message title keys were searched for in
  the game and in the build.
- The raw log was searched for the names the fixes removed.
- The ironman save was unpacked to a scratch folder and read with
  [script.py](../../../../src/stellaris_patcher/paradox/script.py), for the
  player's and the enclaves' countries and flags, the galaxy setup,
  `crusader_01` and the system initializers.

## Limits

- **What showed the message titles isn't known.** Only that it was at
  the main menu and the text is the game's.
- **The Mindwarden enclave's path to its own dialog wasn't traced.** The
  save shows it happened. It doesn't show which country's action led there.
- **Nothing on screen was checked on purpose.** The user saw nothing out
  of place.
