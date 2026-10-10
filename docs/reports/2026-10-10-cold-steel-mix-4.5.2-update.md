# Update check: Cold Steel Mix, 4.5.2, 10 October 2026

**Nothing in the playset needs a new fix. The game didn't change since the
baseline of 9 October, and Steam posted no new notes. The 26 new findings
come from Starbase Extended 3.0 and shrimpAI, which were switched back on
after the last accept, so the check saw them for the first time. Each is
either one the patch already fixes (fixes 3, 28, 30 and 32) or the mod's
own design. Stellar AI's update was already read in the
[seventeen years](2026-10-10-cold-steel-mix-seventeen-years.md#stellar-ais-update)
report. All 27 fixes still build.**

- **The Cold Steel build doesn't have fix 37 yet.** The build is from 21:23.
  The patch was written again with fix 37 at 23:30, and the playset wasn't
  rebuilt after. The build record has 69 of the patch's files, and
  `~~_stellaris_patcher_cold_steel_mix_faculty.txt` isn't one of them. Until
  it's rebuilt, the Archaeostudies Faculty loses More Arcologies' Relic World
  bonuses again. See [What to do next](#what-to-do-next), item 1.
- **The check said "Nothing changed after it" all the same.** Its Cold Steel
  build line compares the build with the game and the Steam mods only, not
  with our patch. It does now (item 2).
- **Starbase Extended's 23 older copies lose nothing from the game.** Its
  window copies are emptied by fix 30, and its hangar bay is mended by fix 32.
  Its other copies only add its own changes. Its three starbase icon sheets
  have the game's 4.5 frames, with its own art for the five starbase tiers.
  See [Starbase Extended](#starbase-extended-30).
- **shrimpAI's Hyper Relay lacks the 4.5.2 waystation clause**, which fix 28
  adds back. The rest of its diff is its own design.

## What to do next

1. **Done** at 23:40. The build record now has fix 37's faculty file, the
   same as the patch's. Was: **Rebuild Cold Steel Mix in Cold Steel**, so
   fix 37 reaches the game.
2. **Done.** The check's Cold Steel build line now looks at our patch too.
   It says "Changed after it: the patch" when a file in the patch's folder
   is newer than the build record. See `_build_status` in
   [check.py](../../src/stellaris_patcher/update/check.py). Was: **Proposed:
   the check's Cold Steel build line should also look at our patch.**
3. **Done** after this report was written. Was: **Accept the check** with
   `check-update --accept`, so Starbase Extended's and shrimpAI's findings
   are marked reviewed.

No fixes to the playset are proposed.

## Notes against the playset

Steam posted no Stellaris announcements since the baseline. The check
listed the 10 announcements from 4.5's open beta onwards, because
Starbase Extended's last update, on 11 July, is older than all of them.
Only lines that name a finding are listed.

| Note | Finding | Result |
|---|---|---|
| 4.5.2: "Fixed Gateways, Hyper-Relays and the Grand Archive not being buildable by Nomadic empires in some cases" | shrimpAI's `hyper_relay` lacks the game's clause for a system with your own waystation | Fix 28 adds it. Ok |
| 4.5 (open beta 5): "Starbase, Orbital Ring, and Waystation weapon modules are now weapon-type-specific" | Starbase Extended's weapon modules | None of its 24 modules has a game name, apart from `detection_array` and `orbital_ring_hangar_bay`. So the game's new weapon modules aren't replaced. Its generic batteries sit beside them. That's its own design |
| 4.5.2: "Removed the starbase strike craft weapon preference policy" | Starbase Extended's hangar bay AI weight checks `is_preferred_weapons = weapon_type_strike_craft` | That's the fleet preference, which 4.5.2 keeps. The check found no removed name in it. Ok |
| None | Starbase Extended's `defense_grid`, `detection_array` and three icon sprites | No note names them. Each diff is Starbase Extended's own change. See below |

| Finding | Result |
|---|---|
| Game files changed | None. Still v4.5.2 |
| Mods changed | Stellar AI, 29 files. Read in the [seventeen years](2026-10-10-cold-steel-mix-seventeen-years.md#stellar-ais-update) report: it updated after the game, so it has no older copies. Starbase Extended and shrimpAI show as `new`: they were off at the last accept |
| The patch's fixes | All 27 ok. A dry run makes 70 files |
| Mod copies of changed game files | None |
| Removed names still used | None |
| Variables nothing defines | 2 new: Starbase Extended's `@build_block_radius_starbase` and `@starbase_formation_priority`. Fix 3 defines both in the patch. The 7 More Events Mod ones were reviewed before |
| Names the notes removed that older mods use | None |
| Outdated mods | The same five as on 7 October. None changed |
| Left to the authors | The list is empty |

## Starbase Extended 3.0

Updated 11 July 2026, before 4.5 was released. 23 objects replace newer
copies.

| Objects | What the diff shows | Result |
|---|---|---|
| 16 starbase window elements in `interface/zzz_sbx_3_0_starbase_view.gui` | July copies that replace UI Overhaul Dynamic's 4.5 ones | Fix 30 ships the file emptied, so the game uses UI Overhaul Dynamic's. Ok |
| `orbital_ring_hangar_bay` | No hangars, one energy upkeep, no tooltip, no tech unlock condition | Fix 32 ships the file whole, with the game's two hangar sets, both upkeeps, its tooltip and `show_tech_unlock_if`. Starbase Extended's own lines stay: cost 50 alloys in place of 120, up to 5 per ring, +2 defense platforms always in place of the game's +1 with an overlord's Orbital Assembly Complex. Its other icon, `GFX_starbase_hangar_bay`, is defined by the game. Ok |
| `detection_array` | Cheaper (25 alloys in place of 100, 0.25 energy upkeep in place of 1), 60 days, in the naval support category, not on orbital rings | Starbase Extended's own balance. Nothing of the game's is missing. Fix 32 ships it with its checks mended |
| `defense_grid` | Adds +33% upkeep for defense platforms it protects | Starbase Extended's own. Nothing of the game's is missing |
| `ship_uses_starbase_components` | Adds its Stronghold and HQ sizes | Starbase Extended's own. Every game size is still listed |
| `GFX_starbase_outliner`, `GFX_starbase_ship_size_small`, `GFX_starbase_ship_size_medium` | 18 frames in place of 16 and 15 | Starbase Extended ships its own sheets. They have the game's frame width, and frames 6 to 16 match the game's 4.5 sheets pixel for pixel. Frames 1 to 5, the starbase tiers, are its own art. Frames 17 and 18 are its Stronghold and HQ. Ok |

## shrimpAI

Smarter Hyper Relays, updated 22 September 2026, before 4.5.2. One object.

| Object | What the diff shows | Result |
|---|---|---|
| `hyper_relay` | It lacks the game's 4.5.2 clause for a system with your own waystation | Fix 28 adds it. Ok |
| | Costs as variables, wild space clauses, its own AI weight, `on_build_complete` checks that the scopes exist | shrimpAI's own design. Its AI weight replaces the game's whole one, including the rule that an AI Nomad builds a relay only where it has a tier 2 or 3 waystation. The building rule itself, in `possible`, stays |

## How it was worked out

- `check-update --notes`, in `~/.cache/stellaris-patcher/checks/2026-10-10_2333/`.
- Each of the 24 new diffs was read, and the notes searched for its object.
- Starbase Extended's module names were looked up in the game's
  `common/starbase_modules/`.
- The icon sheets were read as raw 32-bit DDS files, and each frame compared
  with the game's.
- The patch's hangar bay was read in its written folder.
- `cold-steel-mix` without `--write` gave the fixes' outcomes.
- The build record, `builds/d8f5e037….json`, was searched for the patch's
  files.

## Limits

- **Nothing about play.** No game was run. Fix 37 isn't checked in game.
- **Starbase Extended's balance.** Its cheaper modules and generic batteries
  are read as its own design, beside 4.5's weapon-type modules. Whether they
  make starbases too strong only shows in play.
- **The forum notes.** Steam's notes for 4.5 are cut short. A Starbase
  Extended change that no Steam note names may still undo a fix only in the
  full notes.
