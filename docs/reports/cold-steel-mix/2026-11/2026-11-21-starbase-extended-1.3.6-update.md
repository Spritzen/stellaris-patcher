# Update check: Cold Steel Mix, Starbase Extended 1.3.6, 21 November 2026

**The game stayed on 4.5.4, and one mod updated: Starbase Extended 3.0,
from 1.3.5 to 1.3.6, "Reworked ACoT compatibility". All 31 fixes build,
and a fresh build is the same as the written patch, byte for byte. One
fix is proposed. Starbase Extended's copy of the game's
`ship_uses_starbase_components` now counts the game's three tier-3
arkships as starbases. A tier-3 arkship can then take the starbase combat
computers, and its own arkship computer is what gives it its actions:
settle, survey, build megastructures and the rest. Cold Steel's build
predates the update, so it needs a rebuild before play.**

- **Tier-3 arkships get starbase components.** The trigger gates the
  game's starbase reactors, starbase combat computers and the Hyperlane
  aura. Starbase Extended's copy wins over the game's: the last error log
  says so. Its new lines add `civilian_arkship_tier_3`,
  `science_arkship_tier_3` and `military_arkship_tier_3`, next to ACoT's
  tier-4 arkships. Tier 1 and 2 arkships aren't added.
- **An arkship's design is made by the game.** Its size has
  `is_designable = no` and `enable_default_design = yes`. So the game picks
  its combat computer and reactor. `COMBAT_COMPUTER_ARKSHIP` holds all 22
  arkship actions. `STARBASE_COMBAT_COMPUTER_1` to `_3` hold none, have an
  `ai_weight` and upgrade each other. The starbase reactors give half a
  juggernaut reactor's power. Which ones the game picks shows only in play.
- **The rest of 1.3.6 is ACoT's and changes nothing here.** 28 ACoT ship
  sizes are added to the same trigger and to `ship_uses_special_starbase_components`.
  No playset mod defines them. Nothing uses the second trigger.
- **The Security Branch limit isn't in the files.** The change log says
  it's now 1 per starbase. `security_branch_office` has no limit, and the
  module file is from 5 July. Fix 32 ships that file whole, so the patch
  takes the limit when Starbase Extended adds it.

## What to do next

1. **Done** after this report was written: fix 44 was added, as below.
   Was: **Proposed: fix 44, Starbase Extended's starbase trigger without the
   game's arkships.** A copy of Starbase Extended's
   `ship_uses_starbase_components`, in a `zz_` scripted triggers file, so it
   wins. Every `is_ship_size` line naming one of the game's arkships, as
   the game's `is_arkship_ship` lists them, is taken out. Its own sizes
   and ACoT's stay. Only while Starbase Extended's trigger names one.
   The copy is 65 lines. Fixes 30 to 34 already ship larger copies of Starbase Extended's files.
   The other way is to leave it to the author, as a Left to the authors
   line. They update often: 1.3.5 and 1.3.6 came two weeks apart.
2. **Half done** after this report was written: the patch was written at
   20:58, with fix 44. Cold Steel Mix still needs rebuilding in Cold Steel.
   Was: **Rebuild, once the game and the Paradox launcher are closed.** If fix
   44 is agreed, add it first, then run `cold-steel-mix --write`. Without
   it, `--write` would change nothing but the descriptor's dated version.
   Then rebuild Cold Steel Mix in Cold Steel. Its build, from 14 November
   at 19:43, predates Starbase Extended's update on 20 November.
3. **A Workshop upload is due**, as fix 44 was added. Write its patch notes
   first, and paste the collection's description, which now says 32 fixes.
4. **Done** after this report was written: **Accept the check** with
   `check-update --accept`, so this baseline holds Starbase Extended 1.3.6.
5. **In a game with a Nomadic empire,** upgrade an arkship to tier 3 and
   look at its actions and its design's combat computer. This settles
   whether item 1 is needed. Without fix 44, an arkship that loses them
   shows it. 1.3.6 may also log entries for ACoT's sizes, which no playset
   mod defines. No earlier run logged a missing ship size, so it's unknown
   whether the game checks them.

## Notes against the playset

No game update. Steam posted one announcement since the baseline: Dev
Diary 441, on 19 November. It isn't a release, so it has no notes to match.

| Finding | Result |
|---|---|
| Game files changed | None |
| Mods changed | Starbase Extended 3.0, 1.3.5 to 1.3.6. Steam updated it on 20 November at 10:44 UTC |
| The patch's fixes | 31 of 31 ok. A fresh build's 74 files are byte for byte the written patch's |
| Mod copies of changed game files | None |
| Removed names still used | None |
| Variables nothing defines | 9, all reviewed before. None new. Fix 3 covers Starbase Extended's two |
| Older mod copies | 261 in 12 mods, none new. Starbase Extended isn't among them: its files are newer than the game's |
| Names the notes removed that older mods use | None |
| Outdated mods | The same five as on 14 November. None changed |
| Left to the authors | One line, Stewart's Resolve. Real Space didn't change, so it stays |

## Starbase Extended 1.3.6

| File | Change | Result |
|---|---|---|
| `common/scripted_triggers/sbx_scripted_triggers.txt` | Both triggers get 28 ACoT ship sizes, the game's three tier-3 arkships and a second `starbase_waystation_3` | The arkships in `ship_uses_starbase_components` reach play. See above. Fix 44 is proposed |
| `descriptor.mod` | `version="1.3.6."` | Ok |
| `SBX_3_0_Change_Log.txt` | "Limited the amount of buildable Security Branch modules to 1 per starbase", and "Reworked ACoT compatibility" | The limit isn't in the module file. Ok |
| `interface/zzz_sbx_3_0_starbase_view_gui.bak` | A backup of its starbase window | The game reads only `.gui` files there. Fix 30 still empties `zzz_sbx_3_0_starbase_view.gui`. Ok |
| `common/starbase_levels/zzzz_sbx_3_0_starbase_levels.txt` | A new file time only. Its text is the baseline's | Ok |

### What the trigger gates for a tier-3 arkship

| Game component | Set | Before 1.3.6 | With 1.3.6 |
|---|---|---|---|
| `COMBAT_COMPUTER_ARKSHIP`: 22 arkship actions, `ship_behavior = "arkship"` | combat computers | The only choice | One of four |
| `STARBASE_COMBAT_COMPUTER_1` to `_3`: fire rate and tracking, `ship_behavior = "platform"`, `ai_weight = 1` | combat computers | Not offered | Offered |
| `JUGGERNAUT_*_REACTOR`: 3,850 to 14,300 power | power core | The only choice | One of two per tier |
| `STARBASE_*_REACTOR`: 1,875 to 7,125 power | power core | Not offered | Offered |
| `SHIP_AURA_HYPERLANE` | auras | Not offered | Offered |

The bio-ship starbase reactors and computers also need
`is_arkship_ship = no`, so bio-ship empires' arkships keep only their own.
The game's weapons that need `ship_uses_starbase_components = no` also need
`is_arkship_ship = no`, so arkships never had them, and nothing changes.

## How it was worked out

- `check-update --notes`, in `~/.cache/stellaris-patcher/checks/2026-11-21_2043/`.
- Starbase Extended's 1.3.5 baseline was unpacked from `snapshots/` and
  compared with 1.3.6, file by file. Files newer than the baseline were
  listed by time, which found the `.bak` file the snapshot doesn't keep.
- Each ship size the trigger names was looked up in the game's and every
  playset mod's `ship_sizes`. The game's component templates were searched
  for each component that uses the trigger, with its set, size, power and
  other checks. The last error log, from 14 November, showed which copy
  of the trigger wins.
- The tier-3 arkship's ship size was read for how its design is made.
- The patch was built in memory and compared with the written patch, file
  by file.
- Update times came from `appworkshop_281990.acf`, and were compared with
  Cold Steel's build.

## Limits

- **Nothing about play.** No game was run on 1.3.6. Whether the game's
  default design for a tier-3 arkship takes a starbase computer or reactor
  shows only in a game with a Nomadic empire.
- **ACoT isn't in the playset.** Whether the game logs the 28 sizes no mod
  defines is unknown until the next run.
