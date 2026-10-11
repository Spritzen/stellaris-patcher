# Game report: Cold Steel Mix, the seventeen years save continued to 2243, 11 October 2026

**The [seventeen years](2026-10-10-seventeen-years.md) game again, loaded
from the 2232.02.02 save the [thirty-two years](2026-10-11-thirty-two-years.md)
run ended on and played to 2243.01.02. That's about eleven more years in
1⅔ hours. It's the first run with fix 38 in the build. The galaxy was made
two patch builds ago, before fixes 37 and 38. The patch held, and the user
saw nothing unusual. Play logged 13 entries, down from 32. None is
worth a fix. One was added anyway at the user's request, as fix 40.**

- **Starbase Extended's Starholds log nothing.** The galaxy's first five
  starbases past Starport were built in play, two of them aquatic. There
  were no attach point, sound, particle or animation entries. So fix 31
  fits the log at Starhold too. See [The patch's fixes](#the-patchs-fixes).
- **More Events Mod's Astral Tales tried to give the user's ruler a trait
  the game won't give them.** The user took "It's all just a game?!". Its
  33% roll for Substance Abuser came up, but the Divine Elven Order is an
  autocracy, and the game's rule refuses its ruler a normal trait. The ruler
  got nothing, which spares them a negative trait. It's fix 26's and fix
  38's mistake again, but here it only makes the tooltip wrong. Fix 40 now
  mends it anyway, at the user's request. See [Astral Tales](#astral-tales-2).
- **Fix 38 is in the build but wasn't reached.** The Grudge's relic event
  didn't run.
- **Stellar AI's new rebel empire check (3).** A rebellion made the
  Evandarian Star Mandate in 2238. In its first month it had no society or
  engineering research, so Stellar AI's monthly check read two unset
  variables. Harmless. See [Stellar AI](#stellar-ai-3).
- **The game repaired the save on load again.** Two fleets were saved mid
  combat with ships that had disengaged. See
  [Loading the save](#loading-the-save-2).
- **No AI empire defaulted in 43 years.** `game.log` has no default line,
  and the save has no `country_defaulted` flag.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.11`, the source of the 10:41 Workshop upload. Its 71 files in the build match our source folder byte for byte, fix 38's `random_leader.txt` among them |
| Built | The Cold Steel build at 10:39 on the log's clock, two minutes after fix 38 was committed. The build record has no mismatches |
| Session | Started 11:05:33. Loaded `2232.02.02` at 11:12:05. Played to `2243.01.02`, saved at 12:52. A save at 2241.01.03 on the way. About 1⅔ hours of play |
| Empire | Divine Elven Order, the user's custom Life-Seeded empire, a theocratic monarchy (imperial authority), in the seventeen years galaxy (seed 2111005531) |
| Logs | `error.log`: 6,611 entries. 5,717 resources not installed, 837 override notices and 57 problems: 42 from loading, 2 from loading the save, 13 from play |

The log's clock is one hour ahead of the file times, as before. The last
entry is at 12:34:22. The last `game.log` line is at 12:51:58, just before
the last save.

## Compared with earlier runs

| Group | Thirty-two years | This run | Change |
|---|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | None |
| The game's own, while loading | 1 | 1 | None: the missing `trait_organic` |
| The game's own, loading the save | 1 | 2 | Two fleets returned from combat, not two deposits |
| The game's own, in play | 4 | 6 | Different ones. See [The game's own](#the-games-own-6) |
| No source, in play | 0 | 1 | An unnamed portrait selector |
| Stellar AI, in play | 0 | 3 | The new rebel empire |
| More Events Mod, in play | 28 | 3 | The Grudge, Astral Tales |
| **Total** | **75** | **57** | |

**The override notices didn't change: 837**, kind for kind. Fix 38 replaces
an inline script, which logs no notice.

## The patch's fixes

**The game uses every copy the patch ships.** 36 duplicate object notices
name the patch's files, the same as last run. Fix 37's faculty is still the
third and last. The duplicate event notices for fixes 11, 12 and 26, and fix
17's initializer notice, name the mods' own files, so the patch's copies
win.

**None of the names the fixes removed are in the log**, the same list as the
[ten years](2026-10-10-ten-years.md#the-patchs-fixes) run, with fix 36's
`Unknown promotion` and fix 38's `leader_forge_leader`. Its one
`ion_core_effect` is a duplicate entity notice, and its one `solar_system`
is fix 17's initializer notice. Its one `rules_leader_cannot_get_normal_trait`
is Astral Tales', not fix 26's or fix 38's stories (below).

| Fix | In game |
|---|---|
| 38 | **In the build, not reached.** The build record gives the patch's copy of `common/inline_scripts/mem_ancestors_grudge/random_leader.txt`. An inline script is replaced as a whole file, so it's the one in use. `game.log` has no `mem_ancestors_grudge.45`, the relic event that picks the leader. No leader in the 2243 save has a `relicowner` trait |
| 31 | **The log fits at Starhold.** The galaxy went from 56 Starports to 66 and its first 5 Starholds: 1 from the Sacrosanct Mireesh Principality and 2 from the Nation of Suth-Kasa, both `humanoid_01`, and 2 from Thamesian Prime, `aquatic_01`. No attach point, sound, particle or animation entries. The 5 Citadels are still the Ebusian Watchers' Fallen Empire's, from before 2232 |
| 37 | Not reached. The 2243 save still has 2 faculties and no planet with `zone_pd_archeotech_preserve` |
| 36 | Not reached: no `Unknown promotion` |
| 28 | Not reached: no Hyper Relay was built |

## Loading (42)

The same 42 as the thirty-two years run, group for group. Details of each
group are in [run 3](2026-10-03-errors-run-3.md#whats-left-by-mod).

## Loading the save (2)

**`Load Error: Fleet … cannot leave combat but has disengaged ships,
returning them`** at 11:12:05, for the Tactical Response Fleet and the
Strategic Readiness Fleet. Both names come from the game's own `HUM2` name
list. The 2232 save was written while they were in combat with ships that
had disengaged. The game put the ships back in their fleets. The game's own
repair, and harmless.

## During play (13)

### Astral Tales (2)

**The user's ruler was picked for a trait the game won't give them.** At
12:34:22 the user took option a, "It's all just a game?!", of More Events
Mod's `mem_astral_tales.8` (`events/mem_astral_tales.txt`). It's the story
where the mod's author speaks to the player. The option gives the ruler a
33% chance of Substance Abuser, a negative trait. The roll came up, and
`add_trait` failed at line 466 with `rules_leader_cannot_get_normal_trait`.

The game's `can_leader_get_normal_trait_trigger` refuses an autocracy's
ruler once the game has started. The Divine Elven Order has imperial
authority, so its ruler can never take the trait. The option's `limit` only
checks that the ruler doesn't have it already. The ruler in the 2243 save
has no Substance Abuser.

**So the option's tooltip offers a risk that can't happen** to an
autocracy's ruler. The outcome is the better one for the player, and the
story runs once a game. It's the mistake fix 26 mends in Under the Blanket
and fix 38 in the Grudge, but those cost a leader a trait they should get.
This one costs nothing, so the report proposed no fix. Fix 40 now adds
`can_leader_get_normal_trait_trigger = yes` to the ruler's `limit`, in a
copy of the one event, as fix 26 does. That corrects the tooltip.

**`Unmatched "$" in string mem_astral_tales.8.desc_01` (1)**, at 12:33:08.
The author's message says "we got around 20$". The game reads `$` as the
start of a variable. More Events Mod's own text, and harmless.

### Ancestors' Grudge (1)

**A relic added twice.** At 12:11:55 the Neboritan Collective finished its
Grudge dig site. The last stage, `mem_ancestors_grudge.335` (line 3352),
adds the Modern Art relic with no check. The empire already had it from the
Grudge situation's event `.415`, which does check. More Events Mod's own,
and harmless, like the Aevum relic last run.

### Stellar AI (3)

**A new empire's first monthly check.** At 11:50:56 the Hathraadan
Commonwealth lost Albali I to a rebellion, on 2238.09.01. The rebels became
the Evandarian Star Mandate, an AI empire with the separatists origin.
Stellar AI's `stellarai_commitment.901`
(`events/111_stellarai_commitment_events.txt`) saves each AI empire's
research income in three variables each month, then compares them (lines
922 and 925). The new empire had no society or engineering income yet, so
those two variables weren't set. The game reads an unset variable as 0,
which is the true income. So the comparison gives the right answer. Stellar
AI's own, and harmless.

### The game's own (6)

| Time | Entry | Cause |
|---|---|---|
| 11:31:14 | `Failed to find uplifted portrait for portrait 'pre_lith5'` | The game's pre-sapient lithoid has no uplifted portrait |
| 11:44:06 | `Failed to find uplifted portrait for portrait 'pre_mol3'` | The game's pre-sapient molluscoid, the same |
| 12:15:44 | ``Unknown property `GetAdjective` `` in the Intergalactic Projectile specimen's text | The game's Glancing Hit anomaly `anomaly.655` and its specimen. No mod has either |
| 12:17:05 | `Invalid Target Location: 'event_target:contract_system'`, and `Mission type has location but the mission has no location set` (2) | The game's Nomads espionage contract, `common/scripted_effects/nomads_effects.txt` line 5818. The target empire had no colonised system inside its borders to place it in. No mod has the file |
| 12:17:46 | `Failed to find valid target solar system for can_access_system` | The game's Nomads contract check, `common/scripted_triggers/09_scripted_triggers_nomads.txt` line 824. No mod has the file |

### No source (1)

**`Failed to find portrait selector`** at 12:24:47, with an empty name. It
names no file, selector or portrait, so it can't be traced. The nearest
`game.log` line is the game's own `distar.85` three seconds earlier, which
has no portrait. Logged once.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 40 | More Events Mod's Astral Tales offers an autocracy's ruler a 33% chance of Substance Abuser, which the game refuses (see [Astral Tales](#astral-tales-2)) | **Done** on 11 October as fix 40, at the user's request ([decision 59](../../../decisions.md)). Not yet checked in game. Was: no fix proposed, as only the tooltip is wrong, the player gains from it, and the story runs once a game. If wanted: ship a copy of `mem_astral_tales.8` with `can_leader_get_normal_trait_trigger = yes` in the ruler's `limit`, as fix 26 does. It ships More Events Mod's lines, so needs its author's permission at the next upload, as fixes 26 and 38 do |
| 38 | Fix 38 isn't checked in game | Wait for a Grudge empire to use a relic. The log and build already fit |
| 37 | Fix 37 isn't checked in game | As in the [thirty-two years](2026-10-11-thirty-two-years.md#what-to-do-next) report. This galaxy still has no Archeotech Preserve zone |
| 1 | Still unchecked in play | As in the [ten years](2026-10-10-ten-years.md#what-to-do-next) report, less the Starhold log: five Starholds logged nothing. A Starhold or Citadel on screen, and a Hyper Relay, are still to see |
| — | This report isn't committed | Commit it |

The Grudge relic, the Stellar AI variables, the fleet repairs and the
game's own entries are harmless, and no fix is proposed.

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../../../src/stellaris_patcher/paradox/error_log.py), and
  grouped it as the last report did.
- Split the entries by time. Loading ends at 11:06:23, the save loads at
  11:12:05 (`time.log`), and play entries run from 11:31:14 to 12:34:22.
- Read the build record, and compared the patch's 71 files in the built mod
  with the patch folder byte for byte.
- Ran `check-update`. No game file or mod changed since the 10 October
  baseline, all 28 fixes build, nothing is left unreviewed, and nothing
  changed after the build. It wasn't accepted, as it had nothing new.
- Searched the raw log for each name the fixes removed, and counted the
  duplicate object notices naming the patch's files.
- Traced each play entry's file in the build record and read the code at
  its line: More Events Mod's Astral Tales event and text and its Grudge dig
  site and situation, Stellar AI's commitment event, and the game's
  leader trait rule, Substance Abuser trait, Nomads contract effect and
  trigger, Glancing Hit anomaly, specimen and portraits.
- Unpacked the `2232.02.02`, `2241.01.03` and `2243.01.02` saves into a
  scratch folder: the user's government and ruler's traits, the Neboritan
  and Evandarian empires, relic traits, the starbases by level with their
  owners' cultures, the faculties and Archeotech Preserve zones, Hyper
  Relays and default flags.

## Limits

- **What happened on screen.** The user saw nothing unusual, but didn't say
  which windows they opened. Visual problems don't reach the logs. Fix 31's
  Starholds weren't looked at.
- **The empty portrait selector** names nothing, so its mod isn't known.
- **Whether Astral Tales showed the 33% risk** in its tooltip. That's read
  from the `random_list`, not seen.
- **Fix 37's bonuses, fix 38's relic pick and Hyper Relays** didn't come
  up.
