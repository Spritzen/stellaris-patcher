# Game report: Cold Steel Mix, the seventeen years save continued to 2232, 11 October 2026

**The [seventeen years](2026-10-10-cold-steel-mix-seventeen-years.md) game,
loaded from its 2217.05.04 save and played to 2232.02.02. That's about
fifteen more years in 1¼ hours. It's the first run with fix 37 in the build,
in a save started before it. The patch held, and the user saw nothing
unusual. Play logged 32 entries, up from 3. 28 are More Events Mod's and 4
are the game's own. One More Events Mod problem is worth a fix, since added
as fix 38, and one is proposed for the update check.**

- **Fix 37's faculty wins in an existing save.** The log has a third
  duplicate object notice for `building_archaeostudies_faculty`, naming the
  patch's `~~_stellaris_patcher_cold_steel_mix_faculty.txt`. The galaxy has
  no Archeotech Preserve zone, so its bonuses weren't reached. See
  [The patch's fixes](#the-patchs-fixes).
- **More Events Mod's Ancestors' Grudge gave an AI official no relic
  trait.** The Neboritan Collective, a hive mind with the mod's own Grudge
  origin, used its pauldron relic. The story picked an official that the
  game's rule won't give a normal trait, probably a councilor. Fix 26
  mends the same mistake in Under the Blanket. Fix 38 now mends it here the
  same way. See [Ancestors' Grudge](#ancestors-grudge-4).
- **23 entries came from one More Events Mod dig site, all at once.** An AI
  empire stopped digging the giant sphere site. The site was deleted, and
  the event's `after` block and the game's visibility check then read it.
  That was the mod's own choice, and it was harmless. See
  [The giant sphere site](#the-giant-sphere-site-23).
- **The game repaired the save on load.** It cleared 2 deposits that had no
  type. Both were already in the 2217 save. The saves written after it are
  clean. See [Loading the save](#loading-the-save-1).
- **The update check's build line is wrong.** It says the patch changed
  after the build, but the patch's 70 built files match our source byte for
  byte. The newer file is `descriptor.mod`, which never goes into the build.
  It got the Workshop id at 23:47. The check now skips it (item 39).
- **No AI empire defaulted in 32 years.** `game.log` has no default line,
  and the save has no `country_defaulted` flag.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.10`. Its 70 files in the build match our source folder byte for byte, fix 37's faculty file among them |
| Built | The Cold Steel build at 00:40 on the log's clock, after fix 37 was written. The build record has no mismatches |
| Session | Started 08:35:53. Loaded `2217.05.04` at 08:38:35. Played to `2232.02.02`, saved at 09:51. Saves at 2219.04.09 and 2226.08.02 on the way. About 1¼ hours of play |
| Empire | Divine Elven Order, the user's custom Life-Seeded empire, in the seventeen years galaxy (seed 2111005531) |
| Logs | `error.log`: 6,629 entries. 5,717 resources not installed, 837 override notices and 75 problems: 42 from loading, 1 from loading the save, 32 from play |

The log's clock is one hour ahead of the file times, as before. The last
entry is at 09:51:10, just before the last save.

## Compared with earlier runs

| Group | Seventeen years | This run | Change |
|---|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 7 | 6 | −1: no "Could not find files" for Stellar AI, as Steam didn't touch it this time |
| The game's own, while loading | 1 | 1 | None: the missing `trait_organic` |
| The game's Life-Seeded check | 4 | 0 | The empire designer wasn't used: a save was loaded |
| More Events Mod, at game start | 1 | 0 | No new galaxy |
| The game's own, loading the save | 0 | 1 | The repaired deposits |
| The game's own, in play | 3 | 4 | Different ones. See [The game's own](#the-games-own-4) |
| More Events Mod, in play | 0 | 28 | The sphere site, the Grudge and Aevum |
| **Total** | **51** | **75** | |

**The override notices: 1 more, from fix 37.**

| Kind | Seventeen years | This run | Change |
|---|---:|---:|---|
| Duplicate objects | 290 | 291 | +1: the patch's `building_archaeostudies_faculty` |
| Duplicate entities | 480 | 480 | None |
| Duplicate section templates | 23 | 23 | None |
| Duplicate events | 30 | 30 | None |
| Duplicate variables | 12 | 12 | None |
| Real Space's initializer | 1 | 1 | None |
| **Total** | **836** | **837** | **+1** |

The [long session](2026-10-04-cold-steel-mix-long-session.md) was the last
long run from a save, at 95 play entries in 10.5 hours. 32 in 1¼ hours is
more than any run since. 23 of them are one event, so the rate isn't a
trend.

## The patch's fixes

**The game uses every copy the patch ships.** 36 duplicate object notices
name the patch's files, the 35 of last run and fix 37's. The duplicate event
notices for fixes 11, 12 and 26, and fix 17's initializer notice, name the
mods' own files, so the patch's copies win.

**None of the names the fixes removed are in the log**, the same list as the
[ten years](2026-10-10-cold-steel-mix-ten-years.md#the-patchs-fixes) run,
with fix 36's `Unknown promotion`. Its one `ion_core_effect` is a duplicate
entity notice, and its one `solar_system` is fix 17's initializer notice.
Its one `rules_leader_cannot_get_normal_trait` is from the Ancestors' Grudge,
not fix 26's Under the Blanket (below).

| Fix | In game |
|---|---|
| 37 | **Wins, but not reached.** The faculty notices come in the order More Arcologies, Stellar AI, the patch, so the patch's copy is the one in use. A building is read fresh at load, so it works in a save started before the fix. The 2232 save has 2 faculties, none in 2217, and no planet in the galaxy has `zone_pd_archeotech_preserve`. So its bonuses had nothing to apply to |
| 31 | No attach point, sound, particle or animation entries. The galaxy went from 33 Starports to 56, so 23 were built in play. None went past Starport. The 5 Citadels were already there in 2217 |
| 36 | Not reached: no `Unknown promotion`, and no new specimen to look at |
| 28 | Not reached: no Hyper Relay was built |

## Loading (42)

The same 42 as the seventeen years run, group for group, without Stellar AI's
"Could not find files". Details of each group are in
[run 3](2026-10-03-cold-steel-mix-errors-run-3.md#whats-left-by-mod).

## Loading the save (1)

**`Repaired savegame, cleared 2 invalid deposits!`** at 08:38:35. The 2217
save has 2 deposits with no `type`:

| Deposit | On | In the saves |
|---|---|---|
| 437 | Planet 275, the Neboritan Collective's Relic World capital | Since the first save, `2200.01.01` |
| 16781018 | Planet 1020, a nuked world | Since some time before `2217.05.04` |

The game removed both, and the 2219 and 2232 saves have none. The cause
isn't found. Every deposit More Events Mod's Grudge origin adds is defined.
A new game doesn't check its deposits, so only a loaded save shows this. The
game's own repair, and harmless.

## During play (32)

### The giant sphere site (23)

**All at 09:46:27–28, from one More Events Mod dig site.** The Nation of
Suth-Kasa's science ship SNN Jal Tesk finished the first stage of the
`mem_asp_epilogue_site` on its capital. That fires `mem_asp.81`
(`events/mem_asp_scfe_events.txt`, line 1466).

- Option b, `destroy_archaeological_site = from`, ends the story. Every stage
  has one, so stopping is the mod's own design.
- The event's `after` block then reads `from.planet` (line 1486) and `from`
  (line 1493), the deleted site. 3 entries.
- The game checks every empire's view of the site again. Its own
  `default_site_visible_trigger` reads `from.solar_system` and
  `from.planet`. 1 `intel_level` entry and 19 context switch entries, one
  per empire.

The site was in the 2231.01.01 autosave and gone by 2231.07.01. The
planet still exists, and no planet got `mem_aspmod_giant_sphere_on_planet`,
which option a's `after` adds. So the site was removed, not lost.
`game.log` records `mem_asp.81` with option 0 at 09:46:28. It isn't clear
which option that counts. Only option b deletes the site.

Harmless. A guard on the `after` block would only quiet the log. Left to
More Events Mod.

### Ancestors' Grudge (4)

**An AI official was picked for a relic trait the game won't give them.**
At 09:43:34 the Neboritan Collective, a hive mind with More Events Mod's
`origin_mem_ancestors_grudge_hive`, used its pauldron relic
(`last_activated_relic`). Event `mem_ancestors_grudge.45` offers the relic's
legendary trait to a leader. The AI took option a, `leader_1`
(`events/mem_ancestors_grudge_events.txt`, line 6425).

`mem_ancestors_grudge_trait_effect` then failed to add
`leader_trait_legendary_mem_ancestors_grudge_relicowner_official`
(`common/scripted_effects/mem_ancestors_grudge_scripted_effects.txt`, line
107), with `rules_leader_cannot_get_normal_trait`. The game's
`can_leader_get_normal_trait` rule refuses a gestalt empire's councilor, an
autocracy's ruler and an heir. The pick in
`common/inline_scripts/mem_ancestors_grudge/random_leader.txt` leaves out
rulers and leaders with `trait_imperial_heir`, but not councilors. In a hive
mind, that's likely the one it hit.

**So the relic's owner got nothing.** The visible trait is a tooltip only,
and no leader in the 2231 and 2232 saves has a `relicowner` trait. The relic
still counts as used. The origin is a hive version of the story, so a hive
empire is who uses it most. A player on it could lose the trait too.

This is the mistake fix 26 mends in Under the Blanket
([decision 40](../decisions.md)). Fix 38 now mends it the same way.

**`leader_forge_leader` isn't set (3).** The same script compares each pick
with the relic planet's governor, which is only saved when the planet has
one. The comparison logs an error but gives the right answer. The
[long session](2026-10-04-cold-steel-mix-long-session.md) logged it too.

### Aevum (1)

**A relic added twice.** At 09:40:38, `mem_aevum.320`'s option a
(`events/mem_aevum_events.txt`, line 3146) adds the Hourglass, which the
story gives earlier too. The empire already had it. Harmless, More Events
Mod's own, like the Grudge's double relic in the long session.

### The game's own (4)

| Time | Entry | Cause |
|---|---|---|
| 08:57:45 | `CShipAura::GetToolTipString received a scope that was neither empty nor a ship scope` | A tooltip in the game's program. No file |
| 09:20:11 | Invalid context switch `[observation_outpost_owner]` from Ulm I, `events/first_contact_dlc_events.txt` line 1820 | The game's `fircon.1280`. A pre-FTL world watched only by a Nomadic waystation has no outpost owner. The next line handles waystations. No mod has this file |
| 09:47:23 | `Missing sound effect: aqu_portrait_02_ascended` | The game's aquatic portrait 2 has no psionic `_ascended` greeting |
| 09:51:10 | `Failed to find uplifted portrait for portrait 'pre_art1'` | The game's pre-sapient arthropod has no uplifted portrait |

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 38 | More Events Mod's Ancestors' Grudge picks leaders with no check that the game lets them take a normal trait. In a gestalt empire, a councilor can be picked and get no relic trait (see [Ancestors' Grudge](#ancestors-grudge-4)) | **Done** on 11 October as fix 38 ([decision 57](../decisions.md)), without the optional `exists` check. Not yet checked in game. Was: ship a copy of `common/inline_scripts/mem_ancestors_grudge/random_leader.txt` at its own path, with `can_leader_get_normal_trait_trigger = yes` in each of its four picks: the forge leader and `leader_1`–`3`. That's the game's own rule, as in fix 26. An inline script is replaced as a whole file, and the patch loads last, so its copy wins ([merge_rules.json](../../src/stellaris_patcher/data/merge_rules.json)). Event `.45` always keeps a fallback option, scrap or archeotech, so a story with no leader left still ends. Optionally, check `exists` before comparing with `leader_forge_leader`, which quiets its 3 entries. Small, about 80 lines, and works in existing saves. It ships More Events Mod's lines, so needs its author's permission at the next upload, as fix 26 does |
| 39 | `check-update` says "Changed after it: the patch" when only `descriptor.mod` is newer. The build never copies it or `thumbnail.png` | **Done** on 11 October. `_build_status` in [check.py](../../src/stellaris_patcher/update/check.py) skips those two (`NOT_BUILT`). The check now says "Nothing changed after it" for this build. Was: skip those two, or read the build record's `left_out` |
| 37 | Fix 37 isn't checked in game | Look at an Archaeostudies Faculty on a planet with More Arcologies' Archeotech Preserve zone. The log already fits |
| 36 | Fix 36 isn't checked on screen | As in the [seventeen years](2026-10-10-cold-steel-mix-seventeen-years.md#what-to-do-next) report |
| 1 | Still unchecked in play | As in the [ten years](2026-10-10-cold-steel-mix-ten-years.md#what-to-do-next) report. This run built 23 Starports, still none past Starport, and no Hyper Relay |
| — | This report isn't committed | Commit it |

The giant sphere's `after` block, the Aevum relic and the typeless deposits
are harmless, and no fix is proposed.

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../src/stellaris_patcher/paradox/error_log.py), and
  grouped it as the last report did.
- Split the entries by time. Loading ends at 08:36:39, the save loads at
  08:38:35 (`time.log`), and play entries run from 08:57:45 to 09:51:10.
- Read the build record, and compared the patch's 70 files in the built mod
  with the patch folder byte for byte. Found the patch file newer than the
  build: `descriptor.mod`, which the record lists as left out.
- Ran `check-update`. No game file or mod changed since the 10 October
  baseline, all 27 fixes build, and nothing is left unreviewed.
- Searched the raw log for each name the fixes removed, and counted the
  duplicate object notices naming the patch's files.
- Traced each play entry's file in the build record and read the code at
  its line: More Events Mod's sphere event and dig site, its Grudge leader
  pick and trait effect, its Aevum event, and the game's first contact
  event, rule and archaeology trigger.
- Unpacked the `2200.01.01`, `2217.05.04`, `2219.04.09`, `2226.08.02`,
  `2231.01.01`, `2231.07.01` and `2232.02.02` saves into a scratch folder:
  the deposits and their planets, dig site 18, the sphere's modifier, the
  relic traits and the empire that used the pauldron, the faculties and
  Archeotech Preserve zones, the starbases by level, and default flags.

## Limits

- **What happened on screen.** The user saw nothing unusual, but didn't say
  which windows they opened. Visual problems don't reach the logs.
- **Which Grudge leader it was.** The log names no leader, so "a councilor"
  is read from the rule and the empire's government.
- **Which sphere option the AI took.** `game.log` says option 0, but only
  option b deletes the site, and the site is gone.
- **Fix 37's bonuses, starbases past Starport and Hyper Relays** didn't
  come up.
