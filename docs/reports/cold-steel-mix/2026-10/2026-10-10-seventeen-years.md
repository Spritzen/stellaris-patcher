# Game report: Cold Steel Mix, seventeen years with Stellar AI's update, 10 October 2026

**A new galaxy as Divine Elven Order, the Life-Seeded theocracy, played for
seventeen years, to 2217.05.04. It's the longest run since the patch reached
4.5.2, and the first with Stellar AI's 10 October update. The patch held.
Play logged 3 entries, all the game's own and harmless. The user saw nothing
unusual. One older clash turned up in the override notices, and one fix is
proposed, and since added as fix 37.**

- **Play logged 3 entries in about 1¾ hours, all the game's own.** Twice an
  AI empire's Luxury Residences couldn't be finished: the game lets the AI
  build one only while its planet has fewer than 500 spare amenities. Once
  the game sent a stray AI fleet home. See [During play](#during-play-3).
- **Stellar AI's copy of the Archaeostudies Faculty beats More Arcologies'.**
  More Arcologies gives the faculty its Relic World bonuses on planets with
  its Archeotech Preserve zone. Stellar AI's copy, named `~…` so it sorts
  after More Arcologies' `zzz_…`, drops that. This isn't new today. Fix 37
  now ships a merged copy. See
  [Stellar AI and More Arcologies](#stellar-ai-and-more-arcologies).
- **Stellar AI updated today**, and the build carries its new files. Its new
  diplomacy, vassal and budget files add 4 override notices and one harmless
  loading entry. No other mod defines what they replace. See
  [Stellar AI's update](#stellar-ais-update).
- **Fix 36 looks right, but still isn't checked on screen.** An AI empire
  found More Events Mod's laser rifle in 2208. Before fix 36 its text logged
  `Unknown promotion` lines. This log has none.
- **No AI empire defaulted on its debts in seventeen years.** Item 24 asked
  for longer runs to watch this.
- **Every copy the patch ships is the one the game uses.** Its 69 files in
  the build match our source byte for byte.

## The run

| | |
|---|---|
| Game | Stellaris 4.5.2 (Cygnus), native Linux, in English |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last. No mod is switched off |
| Patch | The local copy, `local:stellaris_patcher_cold_steel_mix`, version `2026.10.10`. Its 69 files in the build match our source folder byte for byte |
| Built | The Cold Steel build at 22:23 on the log's clock, after Stellar AI's update reached Steam. The build record has no mismatches |
| Session | Started 22:27:10. New galaxy, seed 2111005531, made at 22:29:12: medium, `spiral_3`, 18 empires, one Fallen Empire, one Marauder, late scaling. Played to `2217.05.04`, saved at 00:13. About 1¾ hours of play |
| Empire | Divine Elven Order, the user's custom Life-Seeded empire, as in the [ten years](2026-10-10-ten-years.md) run |
| Logs | `error.log`: 6,604 entries. 5,717 resources not installed, 836 override notices and 51 problems: 43 from loading, 4 from the game's Life-Seeded check in the empire designer, 1 at game start, 3 from play |

The log's clock is one hour ahead of the file times, as before. The last
entry is at 23:59:43. The quarter hour of play after it logged nothing.

## Compared with earlier runs

The ten years run played the same empire in a similar galaxy. The quick
check played a premade for three years.

| Group | Ten years | Quick check | This run | Change from ten years |
|---|---:|---:|---:|---|
| Diverse Rooms (All in One) | 27 | 27 | 27 | None |
| Real Space family, with Cinematic Camera | 8 | 8 | 8 | None |
| Descriptors, Just Star Names, Apocryphos | 6 | 6 | 7 | +1: "Could not find files for mod" for Stellar AI. See [Stellar AI's update](#stellar-ais-update) |
| The game's own, while loading | 1 | 1 | 1 | None: the missing `trait_organic` |
| More Events Mod, at game start | 0 | 2 | 1 | The Lost Emperor spawn. It depends on the galaxy |
| More Events Mod, in play | 3 | 0 | 0 | The holo projector's text, gone since fix 36 |
| The game's Life-Seeded check | 4 | 21 | 4 | None: Divine Elven Order was played, so only the designer's 4 |
| The game's own, in play | 0 | 0 | 3 | +3: two Luxury Residences and one stray fleet |
| **Total** | **49** | **65** | **51** | |

**The override notices: 4 more, all from Stellar AI's new files.**

| Kind | Ten years | This run | Change |
|---|---:|---:|---|
| Duplicate objects | 286 | 290 | +4: Stellar AI's new defensive pact action, vassal preset and two food budgets |
| Duplicate entities | 480 | 480 | None |
| Duplicate section templates | 23 | 23 | None |
| Duplicate events | 30 | 30 | None |
| Duplicate variables | 12 | 12 | None |
| Real Space's initializer | 1 | 1 | None |
| **Total** | **832** | **836** | **+4** |

## The patch's fixes

**None of the names the fixes removed are in the log**, the same list as the
[ten years](2026-10-10-ten-years.md#the-patchs-fixes) run,
with fix 36's `Unknown promotion`. Its one `ion_core_effect` is a duplicate
entity notice, and its one `solar_system` is fix 17's initializer notice.

**The game uses every copy the patch ships.** 35 duplicate object notices
name the patch's files, as last run. The duplicate event notices for fixes
11, 12 and 26, and fix 17's initializer notice, name the mods' own files, so
the patch's copies win.

| Fix | In game |
|---|---|
| 36 | **Not checked on screen, but the log fits.** An AI empire found More Events Mod's laser rifle on 2208.07.12. Before fix 36, this specimen's text logged `Unknown promotion From` in the [long session](2026-10-04-long-session.md) and the [new-galaxy run](2026-10-05-new-galaxy.md). This log has none. The log can't show whether the text was drawn |
| 31 | No attach point, sound, particle or animation entries. The galaxy went from 17 Starports to 33, so 16 were built in play. No starbase went past Starport |
| 32 | No `Duplicate trigger`. The galaxy's two arkship starbases and 11 waystations built in play logged nothing |
| 28 | Not reached: no Hyper Relay was built |

## Stellar AI's update

**Stellar AI's author published the update at 19:22 on the log's clock, and
the build at 22:23 carries it.** Its 103 files in the build match Steam's
copy in size and time. Its version stays `0.11`. Against the update check's baseline of 9 October, it
changed 29 files: its economic plans, budgets, personalities, market scripts
and AI events. It also added files that replace 4 of the game's objects:

| Object | Its file | Replaces |
|---|---|---|
| `action_form_defensive_pact` | `common/diplomatic_actions/zz_stellarai_cooperation.txt` | The game's, in `00_actions.txt` |
| `preset_vassal_nice_01` | `common/agreement_presets/zz_stellarai_fair_protection.txt` | The game's, in `01_agreement_presets_ai_vassal.txt` |
| `food_expenditure_armies`, `food_expenditure_armies_threatened` | `common/ai_budget/stellarai_strategy_budgets.txt` | The game's, in `00_food_budget.txt` |

No other mod in the playset defines these, so they're no clash. They change
how the AI forms defensive pacts, treats its vassals and pays for armies.
That's Stellar AI's own design. Stellar AI now replaces 89 objects in all.
None of them is one the patch copies. One is also replaced by another mod
(next section).

**"Could not find files for mod" names Stellar AI's Workshop folder.** It
came at 22:27:10. Steam's record shows it touched Stellar AI's item in that
same second. The folder is there, and the game loads only the build, which
has Stellar AI's files. Harmless. The
[long session](2026-10-04-long-session.md) logged the same
for Diverse Rooms.

The update check run for this report (`check-update --notes`) found nothing
else new: no game file changed, and all 26 fixes are still in. It wasn't
accepted. See [What to do next](#what-to-do-next).

## Stellar AI and More Arcologies

**Three copies of `building_archaeostudies_faculty` load, and Stellar AI's
wins.** The log has two notices for it at 22:27:24: More Arcologies' copy
replaces the game's, then Stellar AI's replaces More Arcologies'. Buildings
keep the last definition, and `~stellarai_research_buildings.txt` sorts
after `zzz_pd_archaeostudies_faculty_archeotech_override.txt`.

Each copy is the game's with one change:

| Copy | Its change to the game's |
|---|---|
| More Arcologies, `common/buildings/zzz_pd_archaeostudies_faculty_archeotech_override.txt` | The faculty's two Relic World bonuses, +0.25 minor artifacts per biologist and +25% archaeostudies research speed, also apply on a planet with More Arcologies' `zone_pd_archeotech_preserve`. Two `OR` blocks |
| Stellar AI, `common/buildings/~stellarai_research_buildings.txt` line 700 | The AI's weight coefficient is `@research_building_tier1_coefficient` (4.8), not 1.5, so the AI builds it more |

**So the faculty on an Archeotech Preserve planet loses both bonuses.** The
building still works, and Relic Worlds keep them. Stellar AI's change stays
either way. The two changes touch different lines, so a merged copy keeps
both.

This isn't from today's update. Stellar AI's research buildings file is the
same as at the 9 October baseline, and More Arcologies last updated on
22 September. Earlier reports didn't group the notices by object, so missed
it. Cold Steel has no conflict choice for it.

The only other objects two mods replace are the patch's own fixes, and two
within Planetary Diversity's family, by design. Ascension Worlds fills in
Planetary Diversity's empty `pd_is_aw_world`. More Arcologies'
`calculator_biologist` is Planetary Diversity's copy with the same
Archeotech Preserve change added, so nothing is lost.

## Loading and game start (48)

The same 42 as the ten years run, group for group, with Stellar AI's
"Could not find files" (above). Details of each group are in
[run 3](2026-10-03-errors-run-3.md#whats-left-by-mod).

**The game's Life-Seeded check (4).** Four `Invalid context switch
[founder_species]` entries at 22:28:10–22:28:16, in the empire designer, for
Divine Elven Order. The game's own, as the
[ten years](2026-10-10-ten-years.md#the-games-life-seeded-check-4)
report explains.

**The Lost Emperor's system couldn't be placed (1).** At 22:29:24,
`test_spawn_neochadamus` at line 28 of `mem_descended_scripted_effects.txt`
found no system to connect it to. The save has the `mem_system_spawned` flag
and no `mem_descended_system`, so the story is lost in this galaxy.
`game.log`'s "spawned Scylla" is wrong: the effect logs the last system made
before it. More Events Mod's own code, item 20, left to its author
([decision 41](../../../decisions.md)). It's the third run to log this.

## During play (3)

**Luxury Residences couldn't be added, twice.** At 22:59:59 on Shazuu and
at 23:59:43 on Arnhalla. Both are AI homeworlds, named from the game's
species name lists. The check that failed is in the game's
`building_luxury_residence` (`common/buildings/07_amenity_buildings.txt`):
an AI may build it only while the planet has fewer than 500 spare amenities
(`@amenity_ai_limit`). The planets had more by the time the building was
due. No mod changes this building or that limit. More Events Mod adds one by
effect, but only for its Sadrell newcomers. The
[new-galaxy report](2026-10-05-new-galaxy.md#the-games-own-7)
logged one too. The game's own.

**A fleet was sent home (1).** At 23:56:57, the game program found the
Gilded Star Flock, an AI fleet named from the game's avian name list, in
interstellar space, and sent it home. No script file is named. The game's
own.

## Not errors: AI empires defaulting

**No AI empire defaulted on its debts in seventeen years.** `game.log` has
no default line, and the save has no `country_defaulted` flag. The
[UNE five years](2026-10-09-une-five-years.md) run had one in
five years, and item 24 asked to watch for more in longer runs. This is the
longest run since, and the first with Stellar AI's new budgets.

## What to do next

| # | Problem | Proposal |
|---|---|---|
| 37 | Stellar AI's copy of the Archaeostudies Faculty beats More Arcologies', so a faculty on an Archeotech Preserve planet loses its Relic World bonuses (see [Stellar AI and More Arcologies](#stellar-ai-and-more-arcologies)) | **Done** on 10 October as fix 37 ([decision 53](../../../decisions.md)). Not yet checked in game. Was: ship one merged `building_archaeostudies_faculty`: Stellar AI's copy with More Arcologies' two `OR` blocks, in a `common/buildings/` file named to sort after `~stellarai_…` (`~~…`). The fix checks both mods' copies are still as found, and is left out if either changes. Small, and it works in existing saves. At the next Workshop upload it ships both authors' lines, so it needs their permission, as fixes 29–34 do |
| 36 | Fix 36 isn't checked on screen | Open the Grand Archive on a More Events Mod specimen when the player owns one: it should say where it was found, with no blank. The log already fits (see [The patch's fixes](#the-patchs-fixes)) |
| 24 | AI defaults, from the UNE five years run | **Close it.** None in seventeen years, with Stellar AI's update. Reopen if a long run shows several |
| — | The update check has 26 unreviewed findings | Run the update check and write its report. It covers Stellar AI's 29 changed files, and Starbase Extended's and shrimpAI's findings, which show as new because the last accept was made while those two mods were off. Then accept it |
| 1 | Still unchecked in play | As in the [ten years](2026-10-10-ten-years.md#what-to-do-next) report. This run built 16 Starports, still none past Starport, and no Hyper Relay |
| — | This report isn't committed | Commit it |

## How this was worked out

- Read `error.log` with our
  [error_log.py](../../../../src/stellaris_patcher/paradox/error_log.py), and
  grouped it as the last report did.
- Split the entries by time. The galaxy was made at 22:29:12 (`game.log`).
  Loading ends at 22:27:44 and the designer's entries at 22:28:16. Play
  entries are at 22:59:59, 23:56:57 and 23:59:43.
- Read the build record, and compared the patch's 69 files in the built mod
  with the patch folder byte for byte. Compared Stellar AI's files in the
  build with Steam's copy by size and time.
- Searched the raw log for each name the fixes removed, and read the
  duplicate object, event and initializer notices for the patch's copies.
- Grouped the duplicate object notices by the mod whose file the game uses,
  and searched the build and the game for each of Stellar AI's 4 new
  objects.
- Listed every object with notices from more than one mod, and compared the
  three copies of `building_archaeostudies_faculty` with the game's.
  Checked Cold Steel's conflict choices for the playset (none).
- Ran `check-update --notes`, and compared Stellar AI with its baseline
  snapshot file by file.
- Read Steam's Workshop record for Stellar AI's update and touch times.
- Unpacked the `2200.01.01`, `2215.01.01` and `2217.05.04` saves into a
  scratch folder: the galaxy settings, the starbases by level, the Grand
  Archive's specimens, the Lost Emperor's flag, the Luxury Residences
  planets and default flags.

## Limits

- **What happened on screen.** The user saw nothing unusual, but didn't say
  which windows they opened. Visual problems don't reach the logs.
- **Stellar AI's update was read only for clashes.** Whether its new AI
  plays well is for the update check and longer play.
- **No starbase past Starport** and no Hyper Relay. Attach points on a
  Starhold or larger, and fix 28, weren't reached.
- **One galaxy, one empire.** The bio-ship, Megacorp and lithoid cases the
  fixes cover didn't come up.
