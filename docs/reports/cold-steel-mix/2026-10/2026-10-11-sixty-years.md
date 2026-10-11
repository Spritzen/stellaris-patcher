# Game report: Cold Steel Mix, the seventeen years save continued to 2260, 11 October 2026

**The [seventeen years](2026-10-10-seventeen-years.md) game again, loaded
from the 2243.01.02 save the [forty-three years](2026-10-11-forty-three-years.md)
run ended on and played to 2260.11.03. That's almost eighteen more years in
2¾ hours. It's the first run with fix 40 in the build. The patch held, and
the user saw nothing unusual. Play logged 39 entries. 38 are the game's own
and one is More Events Mod's. None is worth a fix, and no fix is proposed.**

- **The galaxy's first Hyper Relays log nothing.** Two AI hive minds built
  3, and the game uses fix 28's copy. There were no megastructure entries.
  See [The patch's fixes](#the-patchs-fixes).
- **17 more Starholds log nothing.** The galaxy has 22 now, in five ship
  cultures, 5 of them aquatic. There were no attach point, sound, particle
  or animation entries. So fix 31 fits the log across five cultures.
- **Three AI defaults on energy debts, the first in this galaxy.** The
  Thembolon Mandate defaulted twice, in 2252 and 2258, and is in deficit
  again. It's a vassal that pays its overlord 30% of its income, under the
  game's own harshest AI vassal terms. The United Ofoxxer Confederation
  defaulted in 2250. The game lets the AI pick only "do nothing" in a
  deficit. These are the game's own rules, not a mod's. See
  [AI empires defaulting](#not-errors-ai-empires-defaulting).
- **Fix 40 is in the build and wins, but this galaxy can't reach it.**
  Astral Tales runs once a game, and it ran here last run.
- **The 39 play entries are spread thin.** 14 come from one use of the
  game's Expel Population decision. The rest are the game's own, in ones and
  small groups. More Events Mod logged once, in its pilgrimage story.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.11`. Its 72 files in the build match our patch folder byte for byte, fix 40's `!!_stellaris_patcher_cold_steel_mix_astral_tales.txt` among them |
| Built | The Cold Steel build at 13:46 on the log's clock, 25 minutes after fix 40 was committed. The build record has no mismatches |
| Session | Started 13:51:13. Loaded `2243.01.02` at 13:52:37. Played to `2260.11.03`, saved at 16:36. Autosaves every half year from 2258.07.01. About 2¾ hours of play |
| Empire | Divine Elven Order, the user's custom Life-Seeded empire, a theocratic monarchy (imperial authority), in the seventeen years galaxy (seed 2111005531) |
| Logs | `error.log`: 6,637 entries. 5,717 resources not installed, 838 override notices and 82 problems: 42 from loading, 1 from loading the save, 39 from play. `game.log`: event picks, three AI defaults and one More Events Mod log line |

The log's clock is one hour ahead of the file times, as before. The last
entry is at 16:32:07. The last `game.log` line is at 16:36:04, just before
the last save.

## Compared with earlier runs

| Group | Forty-three years | This run | Change |
|---|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| The game's own, while loading | 1 | 1 | None: the missing `trait_organic` |
| The game's own, loading the save | 2 | 1 | A specimen's text, not two fleets |
| The game's own, in play | 6 | 38 | 14 from one Expel Population. See [The game's own](#the-games-own-38) |
| No source, in play | 1 | 0 | The empty portrait selector didn't come back |
| Stellar AI, in play | 3 | 0 | The rebel empire's first month is past |
| More Events Mod, in play | 3 | 1 | The pilgrimage |
| **Total** | **57** | **82** | |

The 38 game entries come in 12 groups. The largest is one decision's 14.
Play lasted 2¾ hours, against 1⅔ last run, and covered 18 years, against 11.

**The override notices: 1 more, from fix 40.**

| Kind | Forty-three years | This run | Change |
|---|---:|---:|---|
| Duplicate objects | 291 | 291 | None |
| Duplicate entities | 480 | 480 | None |
| Duplicate section templates | 23 | 23 | None |
| Duplicate events | 30 | 31 | +1: `mem_astral_tales.8` |
| Duplicate variables | 12 | 12 | None |
| Real Space's initializer | 1 | 1 | None |
| **Total** | **837** | **838** | **+1** |

## The patch's fixes

**The game uses every copy the patch ships.** 36 duplicate object notices
name the patch's files, the same as last run. One is fix 28's Hyper Relay,
`zzzz_stellaris_patcher_cold_steel_mix_hyper_relay.txt`, which comes after
shrimpAI's. The duplicate event notices for fixes 11, 12, 26 and now 40,
and fix 17's initializer notice, name the mods' own files, so the patch's
copies win.

**None of the names the fixes removed are in the log**, the same list as the
[forty-three years](2026-10-11-forty-three-years.md#the-patchs-fixes) run.
`rules_leader_cannot_get_normal_trait` is gone too: last run's one was Astral
Tales'. Its one `ion_core_effect` is a duplicate entity notice, and its one
`solar_system` is fix 17's initializer notice.

| Fix | In game |
|---|---|
| 40 | **In the build and wins, not reachable here.** More Events Mod logs a duplicate event notice for `mem_astral_tales.8` at its own `events/mem_astral_tales.txt` line 424, so the patch's copy is the one in use. The story sets the global flag `mem_astral_tales_fired` when it starts and never runs again. Both saves have it, from last run |
| 28 | **The log fits.** The galaxy went from no Hyper Relays to 3: 1 from the Bhenn'Thell Unity and 2 from the Tumbator Collective, both AI hive minds. The game uses the patch's copy (above). There were no megastructure or relay entries. Neither builder is Nomadic, so the waystation clause the fix adds wasn't tested |
| 31 | **The log fits at Starhold, across five cultures.** The galaxy went from 66 Starports and 5 Starholds to 84 and 22. The Starholds are 11 `humanoid_01`, 5 `aquatic_01`, 3 `fungoid_01`, 2 `synthetics_01` and 1 `biogenesis_02`. No attach point, sound, particle or animation entries. The 5 Citadels are still the Fallen Empire's |
| 38 | Not reached. `game.log` has no `mem_ancestors_grudge.45`, and no leader in the 2260 save has a `relicowner` trait |
| 37 | Not reached. The 2260 save still has 2 faculties and no planet with `zone_pd_archeotech_preserve` |
| 36 | Not reached: no `Unknown promotion` |

## Loading (42)

The same 42 as the forty-three years run, group for group. Details of each
group are in [run 3](2026-10-03-errors-run-3.md#whats-left-by-mod).

## Loading the save (1)

**``Unknown property `GetAdjective` ``** at 13:52:36, in the text of the
Intergalactic Projectile specimen. It's the same entry the last run logged
in play, from the game's Glancing Hit anomaly `anomaly.655` and its
specimen. No mod has either. The game read the text while loading the save
this time. The game's own, and harmless.

## During play (39)

### More Events Mod (1)

**The pilgrimage check found a capital with no position.** At 14:47:07,
More Events Mod's monthly check `mem_spiritualists_pilgrimage.999`
(`events/mem_spiritualists_pilgrimage.txt`) asked for the system closest to
an empire's capital, at line 45, and the game logged
`could not get a coordinate from scope`. The check runs every month after
year 35, so it has run since 2235 without this entry. The trigger fails
for that empire, which isn't marked as a possible pilgrim for that month.
Logged once. More Events Mod's own, and harmless.

### The game's own (38)

| Time | Entries | Cause |
|---|---:|---|
| 13:53:42 | 1 | ``Failed to find valid target solar system for can_access_system``: the game's Nomads contract check, `common/scripted_triggers/09_scripted_triggers_nomads.txt` line 824, as last run |
| 14:51:21 | 6 | `Wrong scope for trigger 'has_ethic'` and `'has_valid_civic'`: the game's `GetPreFTLLower` text (`common/scripted_loc/07_scripted_loc_first_contact_dlc.txt` lines 414–441) was read from a situation, not a country. The game's own pre-FTL situation texts use it. It falls back to "pre-FTL" |
| 15:03:32 | 1 | `begin_event_chain … the country already has an ongoing event chain of the same type`: the game's Fruitful Partnership war event `origin.7600` (`events/origin_events_5.txt` line 1134) started a second war for an empire whose chain was still running |
| 15:03:39 | 1 | ``Variable } is not set`` in the game's `pop_group_add_ethic_effect`, from its Nomads event `nomads.2075` (`events/nomads_origin_events.txt` line 924) |
| 15:03:43 | 1 | `Attempting to use start_colony effect on a planet owned by another empire`: the game's Fruitful seed pods, `origin.7320` (`events/origin_events_5.txt` line 742) |
| 15:22:42 | 1 | `Event ancrel.9126 has no valid options`: the game's arc site stage 3 (`events/ancient_relics_arcsite_events_2.txt`), a hidden event that only picks the next one |
| 16:04:01 | 14 | `Undefined event target: refugee_pop`, with `Invalid context switch` and `Could not get dynamic flag 'valid_refugee_destination_for_'`: the game's Expel Population decision (`common/decisions/01_political_decisions.txt` line 324) and its `refugee_pop_effect` (`common/scripted_effects/refugee_effects.txt`). The target it saves isn't seen where the effect checks the Neboritan Collective and Stellar Fersergeran as places to flee to. One use of the decision |
| 16:12:35 | 1 | `Fleet U'Ruusu Star Flock is in interstellar space without MIA; sending MIA return home`: a fleet named from the game's avian name list. The game's own repair |
| 16:25:27 | 2 | `Invalid context switch [owner] from Fihir Va [planet]` and `'event_target:ship_owner' is invalid`: the game's Planetary Projection follow-up, `anomaly.191` (`events/anomaly_events_1.txt` lines 2714 and 2721). The event asks for the owner of an unowned planet, so its story event isn't sent and the survey isn't credited |
| 16:25:58 | 5 | `Invalid context switch [species]` and `[owner] from [leader]`: the game's portrait files drew leader 184, who has no species or owner. In 2243 that was the user's scientist on the science ship Hyginus, the ship `anomaly.191` names. The leader is gone from the 2259 and 2260 saves |
| 16:31:17 | 4 | `Invalid context switch [from.target]`: the game's BioGenesis espionage event `bio.910` (`events/biogenesis_events.txt` lines 6552–6903), for the Sacrosanct Mireesh Principality. The operation's target wasn't there |
| 16:32:07 | 1 | `Invalid context switch [FROM] from Gia'Zumon [leader]`: the game's admiral trait check (`common/traits/00_admiral_traits.txt` line 1201) ran without a country |

Each file is the game's own in the build record, and no mod has a copy.

## Not errors: AI empires defaulting

**Three AI defaults on energy debts, the first in this galaxy.** `game.log`
has the game's deficit line three times, each from the energy deficit's
last event, `deficit.110` (`events/situation_deficit_events.txt` line 125):

| Date | Empire | What the saves show |
|---|---|---|
| 2250.08.01 | United Ofoxxer Confederation | A Void Dweller democracy with one habitat. At war until May 2258. Its energy was positive in mid 2258. The default's modifier ran out in August 2260 |
| 2252.05.01 | Thembolon Mandate | A Fruitful dictatorship with three planets, the vassal of the Traveling Jaazijan Wayfarers since 2233 |
| 2258.11.01 | Thembolon Mandate | The same empire again. In 2260 it is in a third energy deficit, at 30% and rising 5% a month |

**The Mandate pays its overlord 30% of its income.** Its terms are the
game's own `preset_vassal_mean_03`, from
`common/agreement_presets/01_agreement_presets_ai_vassal.txt`. No mod changes
that preset. Stellar AI's one preset is a tax-free vassal preset.
In mid 2258 the Mandate's energy came to 290 a month and its costs to 359.
91 of those costs were the subject tax. Without it the Mandate would have
been 22 a month in credit.

**The game lets the AI pick only "do nothing" in a deficit.** In the game's
`common/situations/02_deficit_situations.txt`, "do nothing" has AI weight 1
and every other approach has 0. No mod has the file. So an AI empire in
deficit always rides it out to the default, and the vassal tax keeps the
Mandate in deficit.

Item 24 was closed in the [seventeen years](2026-10-10-seventeen-years.md)
report: "Reopen if a long run shows several." This run shows three, but two
are one vassal taxed by the game's own terms. That's the game's design, not
Stellar AI's or another mod's. The Ofoxxer default wasn't traced: the
saves before and after are eight years apart.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 24 | Three AI defaults in 18 years, two of them the same vassal (see [AI empires defaulting](#not-errors-ai-empires-defaulting)) | No fix, and keep it closed. The vassal's tax and the "do nothing" deficit choice are the game's own. Reopen if non-subject AI empires default often in a long run |
| 40 | Fix 40 isn't checked in game | It can't be in this galaxy: Astral Tales has run. Check it in a new galaxy as an autocracy, if Astral Tales comes up. The log and build already fit |
| 38 | Fix 38 isn't checked in game | Wait for a Grudge empire to use a relic. The log and build already fit |
| 37 | Fix 37 isn't checked in game | As in the [thirty-two years](2026-10-11-thirty-two-years.md#what-to-do-next) report. This galaxy still has no Archeotech Preserve zone |
| 1 | Still unchecked in play | As in the [ten years](2026-10-10-ten-years.md#what-to-do-next) report, less what the log can show: 22 Starholds and 3 Hyper Relays logged nothing. A Starhold, Citadel or Hyper Relay on screen, and a Nomadic empire building a relay at its waystation, are still to see |
| — | This report isn't committed | Commit it |

The pilgrimage check and the game's own entries are harmless, and no fix is
proposed.

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../../../src/stellaris_patcher/paradox/error_log.py), and
  grouped it as the last report did.
- Split the entries by time. Loading ends at 13:52:00, the save loads at
  13:52:37 (`time.log`), and play entries run from 13:53:42 to 16:32:07.
- Read the build record, and compared the patch's 72 files in the built mod
  with the patch folder byte for byte.
- Ran `check-update`. No game file or mod changed since the 10 October
  baseline, all 29 fixes build, nothing is left unreviewed, and nothing
  changed after the build. It wasn't accepted, as it had nothing new.
- Searched the raw log for each name the fixes removed, and counted the
  duplicate object and event notices naming the patch's files.
- Traced each play entry's file in the build record and read the code at
  its line: More Events Mod's pilgrimage event, and the game's pre-FTL text,
  Fruitful and Nomads origin events, arc site event, Expel Population
  decision and refugee effect, Planetary Projection anomaly, BioGenesis
  espionage event, admiral traits and deficit situations.
- Unpacked the `2243.01.02`, `2258.07.01`, `2259.01.01` and `2260.11.03`
  saves into a scratch folder: the defaulted empires, their modifiers,
  budgets and subject terms, deficit situations, the starbases by level with
  their ship cultures, Hyper Relays and their owners, relic traits,
  faculties and Archeotech Preserve zones, leader 184, and the Astral Tales
  flag.

## Limits

- **What happened on screen.** The user saw nothing unusual, but didn't say
  which windows they opened. Visual problems don't reach the logs. No
  Starhold or Hyper Relay was looked at.
- **Which capital the pilgrimage check couldn't place.** The entry names no
  empire.
- **Why the Ofoxxer Confederation defaulted.** The nearest saves are from
  2243 and 2258, and its war in that time isn't recorded.
- **Fix 40's tooltip, fix 37's bonuses and fix 38's relic pick** didn't come
  up.
