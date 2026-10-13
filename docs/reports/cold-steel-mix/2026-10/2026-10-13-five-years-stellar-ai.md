# Game report: Cold Steel Mix, five years with Stellar AI 0.12 and fix 41, 13 October 2026

**A new galaxy as the United Nations of Earth, played for five years, to
2205.02.10, in about twelve minutes. It's the first run with Stellar AI 0.12
and with fix 41 in the build. The patch held, and play logged one entry, the
game's own. The user saw nothing unusual. No fix is proposed.**

- **Fix 41 is in the build and wins, but wasn't reached.** The game uses the
  patch's four Gaia Seeders. No empire in this galaxy has Idyllic Bloom, the
  only civic that builds them. See [The patch's fixes](#the-patchs-fixes).
- **Stellar AI 0.12 shows in the override notices as expected: 10 more.**
  Its new war goals add 7, fix 41 adds 4, and the defensive pact Stellar AI
  dropped is the game's again, one fewer.
- **One AI empire defaulted on food in July 2201**, eighteen months in. It's
  the earliest default yet, and not a vassal. Item 24 watches these. One
  isn't enough to reopen it. See
  [An AI empire defaulting](#not-an-error-an-ai-empire-defaulting).
- **The one play entry is the game's timeline text.** One of its tooltips
  names a system it can't find. No mod changes the timeline.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, with fix 41 in a build for the first time. Its 73 files in the build match our patch folder byte for byte |
| Built | The Cold Steel build at 19:08 on the log's clock, seven seconds before the game started. The build record has no mismatches. Its 88 Stellar AI files match the installed 0.12, with its new `~stellarai_war_goals.txt` |
| Session | Started 19:08:41. New galaxy, seed 100068023, made at 19:09:48. Played to `2205.02.10`, saved at 19:21:50. Autosaves every half year from 2203.01.01. About twelve minutes of play |
| Empire | United Nations of Earth. The user's Divine Elven Order was made as an AI empire in this galaxy |
| Logs | `error.log`: 6,631 entries. 5,717 resources not installed, 848 override notices and 66 problems: 44 from loading and game start, 21 from the game's Life-Seeded check, 1 from play. `game.log`: event picks, the lost colony line, and one AI default |

The log's clock is one hour ahead of the file times, as before.

## Compared with earlier runs

The last new galaxy was the [quick check](2026-10-10-quick-check.md). The last
run was the [sixty years](2026-10-11-sixty-years.md) save.

| Group | Quick check | Sixty years | This run | Change from sixty years |
|---|---:|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | 7 | +1: "Could not find files for mod" for Stellar AI. See below |
| The game's own, while loading | 1 | 1 | 1 | None: the missing `trait_organic` |
| The game's own, loading the save | 0 | 1 | 0 | A new galaxy |
| The game's Life-Seeded check | 21 | 0 | 21 | A new galaxy: 3 in the designer and 18 at galaxy creation, as in the quick check |
| More Events Mod, at game start | 2 | 0 | 1 | The `mem_ancient_01` ship set notice. The Lost Emperor's system was placed this time |
| The game's own, in play | 0 | 38 | 1 | The timeline text. See below |
| More Events Mod, in play | 0 | 1 | 0 | The pilgrimage check didn't come back |
| **Total** | **65** | **82** | **66** | |

Twelve minutes of play, against 2¾ hours last run.

**The override notices: 10 more, all from Stellar AI 0.12 and fix 41.**

| Kind | Sixty years | This run | Change |
|---|---:|---:|---|
| Duplicate objects | 291 | 301 | +7: Stellar AI's war goals in `~stellarai_war_goals.txt`. +4: fix 41's Gaia Seeders. −1: `action_form_defensive_pact`, which Stellar AI 0.12 no longer replaces |
| Duplicate entities | 480 | 480 | None |
| Duplicate section templates | 23 | 23 | None |
| Duplicate events | 31 | 31 | None |
| Duplicate variables | 12 | 12 | None |
| Real Space's initializer | 1 | 1 | None |
| **Total** | **838** | **848** | **+10** |

**"Could not find files for mod" names Stellar AI's Workshop folder again.**
It's the first entry, at 19:08:41. The folder is there with 0.12's files.
Its `mod/ugc_3610149307.mod` still says version 0.11 but has the right path.
Steam's record shows no change to it at this time, unlike the
[seventeen years](2026-10-10-seventeen-years.md#stellar-ais-update) run.
The game loads only the build, which has Stellar AI's files. Harmless. Cause
not found.

## The patch's fixes

**The game uses every copy the patch ships.** 40 duplicate object notices
name the patch's files: last run's 36, and fix 41's four. Each of fix 41's
comes after Planetary Diversity's notice for the same Gaia Seeder, so the
patch's copy is the one in use. The duplicate event notices for fixes 11,
12, 26 and 40, and fix 17's initializer notice, name the mods' own files, as
before.

**None of the names the fixes removed are in the log**, the same list as the
[sixty years](2026-10-11-sixty-years.md#the-patchs-fixes) run. Its one
`ion_core_effect` is a duplicate entity notice, its one `solar_system` is fix
17's initializer notice, and its two `hyper_relay` lines are the shrimpAI and
patch notices.

| Fix | In game |
|---|---|
| 41 | **In the build and wins, not reachable here.** No empire in the 2205 save has `civic_idyllic_bloom`, and no planet has a Gaia Seeder |
| 40 | Not reached. Astral Tales didn't run |
| 38 | Not reached. No `mem_ancestors_grudge.45` in `game.log` |
| 37 | Not reached. Too early for an Archeotech Preserve |
| 36 | Not reached: no `Unknown promotion From` |

## Loading and game start (44)

The same 42 as the sixty years run, group for group, with Stellar AI's
"Could not find files" (above). Details of each group are in
[run 3](2026-10-03-errors-run-3.md#whats-left-by-mod). At game start, More
Events Mod's `Changing from GfxCulture '' to 'mem_ancient_01'` notice: an
empire took its ship set, as in the [quick check](2026-10-10-quick-check.md).

## The game's Life-Seeded check (21)

The same 21 as the quick check: 3 in the empire designer and 18 at galaxy
creation, from `is_individual_machine`
(`common/scripted_triggers/02_scripted_triggers_machine_age.txt` line 64) on
Divine Elven Order. The [UNE five years](2026-10-09-une-five-years.md#the-games-life-seeded-check-21)
report explains them. The game's own, and harmless.

## During play (1)

**``Unknown promotion `System` ``** at 19:19:04, in the text
`[…System.GetName] system on §L[GetDate]§!`. That's the end of 14 of the
game's timeline tooltips in `localisation/english/main_2_l_english.yml`,
such as `TIMELINE_EVENT_FIRST_WORMHOLE_TOOLTIP`. Each names the system of
one of its targets. No mod in the build has these texts or the timeline's
definitions. The save's timeline has 2 first arc sites and 1 first wormhole,
and all three planets still exist, so which one failed isn't known. The
game's own, and harmless: at worst one tooltip lacks a system name.

## Not an error: an AI empire defaulting

`game.log` has one AI default, on 2201.07.01, from the food deficit's last
event, `deficit.145` (`events/situation_deficit_events.txt` line 440). The
log line has no names.

The 2205 save has `country_defaulted` on one empire only, the Deepling
Regime (country 16777222). It's a game-made military dictatorship with
Scorched Earth and Beastmasters, militarist and xenophobe, with one planet.
It's no one's vassal. Its food stock is back to 1,057.

This is the earliest default yet. The earlier ones were the Gundersen
Research Society in the [UNE five years](2026-10-09-une-five-years.md) run,
and three energy defaults, two by one vassal, in the
[sixty years](2026-10-11-sixty-years.md#not-errors-ai-empires-defaulting)
run. Stellar AI 0.12 changed its budgets and strategy. Whether that played a
part can't be told from one default. Item 24 stays closed, and this one is
noted for it.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 41 | Fix 41 isn't checked in game | Wait for an AI Idyllic Bloom empire. The log and build already fit |
| 24 | One non-subject AI empire defaulted on food at 2201.07, the earliest yet | No fix. Keep it closed, and count it. Reopen if more non-subject defaults come early, now that Stellar AI 0.12 is in |
| 40, 38, 37, 36 | Not checked in game | As in the [sixty years](2026-10-11-sixty-years.md#what-to-do-next) report |
| — | This report, fix 41 and the update report aren't committed | Commit them |

The timeline text and Stellar AI's "Could not find files" are harmless, and
no fix is proposed.

## How this was worked out

- `error.log` read with
  [error_log.py](../../../../src/stellaris_patcher/paradox/error_log.py), and
  split by time: loading to 19:09:48, game start to 19:10:10, play after.
- Override notices counted by kind, and duplicate objects by file, against
  the sixty years report.
- The build record, `builds/d8f5e037….json`, compared with our patch folder
  and with Stellar AI's installed files. The patch's 73 files compared byte
  for byte with the build folder.
- The timeline texts found in the game's localisation, and the build
  searched for them.
- The 2205.02.10 save unpacked and searched for its timeline, Idyllic Bloom,
  Gaia Seeders and `country_defaulted`.
- `appworkshop_281990.acf` and `mod/ugc_3610149307.mod` read for Stellar AI.

## Limits

- **Twelve minutes of play.** Stellar AI 0.12's new AI rules, and fix 41,
  only show over a longer game.
- **The timeline tooltip** can't be traced to one entry.
- **The default's cause.** The save shows the empire, not why its food ran
  out.
