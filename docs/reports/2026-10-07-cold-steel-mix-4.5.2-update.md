# Update check: Cold Steel Mix, 4.5.2, 7 October 2026

**Nothing in the update needs a fix. Since yesterday's baseline, one mod
changed one file: UI Overhaul Dynamic caught up with 4.5.2's fleet view.**
The game didn't change, and Steam posted no new notes. All 10 of the patch's
fixes still build.

- **UI Overhaul Dynamic now uses 4.5.2's deselect button.** It changed one
  sprite name in `interface/fleet_view.gui`, in two places. The game defines
  the new sprite and uses it in the same two places. No other mod ships the
  file, and no fix touches it. See [The mod that changed](#the-mod-that-changed).
- **The patch and the Cold Steel build aren't in the game.** This isn't from
  the update. Cold Steel's build record and its patch mod for the playset
  were removed this morning. Its conflict choices are empty. The patch isn't
  in the playset or linked in the game's mod folder. Playing now would load
  none of the fixes. The user cleared it on purpose. See
  [The playset's state](#the-playsets-state).

## What to do next

1. **Done.** It was on purpose. The patch was relinked at 17:18 and the
   playset rebuilt at 17:20, before the
   [first run on 4.5.2](2026-10-07-cold-steel-mix-4.5.2-first-run.md).
   Was: **Say whether the empty Cold Steel state was on purpose.** If it wasn't,
   close the game, the launcher and Cold Steel, then run
   `cold-steel-mix --write --add-to-playset --cold-steel-closed` and rebuild
   the playset in Cold Steel.
2. **Done** at 16:18. Was: **Accept the check** with `check-update --accept`, so the next check
   compares with UI Overhaul Dynamic's new file.

No fixes are proposed.

## The mod that changed

| Mod | File | What changed | Against the game |
|---|---|---|---|
| UI Overhaul Dynamic (`workshop:1623423360`), updated 6 October 18:04 | `interface/fleet_view.gui` | The `deselect` button's sprite, twice: `GFX_close_square` → `GFX_fleet_action_button_deselect` | Matches. The game's `fleet_view.gui` uses the new sprite in the same two buttons, and its `interface/fleet_view.gfx` defines it. That `.gfx` file has no mod copy |

UI Overhaul Dynamic's copy still wins over the game's. It now has this part
of the 4.5.2 fleet view. The check didn't compare the rest of the file with
the game's, because the game's copy didn't change since the baseline.

## Notes against the playset

Steam posted no Stellaris announcements since the baseline, so there's
nothing new to match.

| Finding | Result |
|---|---|
| Game files changed | None. Still v4.5.2 |
| Mods changed | UI Overhaul Dynamic only, one file |
| The patch's fixes | All 10 ok. A fresh build makes the same 12 files |
| Mod copies of changed game files | None |
| Removed names still used | None |
| Variables nothing defines | 9, all reviewed at the last accept. Fix 3 defines the two Starbase Extended ones in the patch. The seven More Events Mod ones have no fix |
| Outdated mods | Five: both UI Overhaul Dynamic add-ons, The Galaxy Is Flat, Realistic Asteroids and Extended Soundtrack. None of them changed |

## The playset's state

| What | State |
|---|---|
| Cold Steel's playsets | Cold Steel Mix has its 26 mods. No playset is `active` |
| Its conflict choices (`resolutions/d8f5e037….json`) | Empty, `built: 0`. Written 07:23 |
| Its patch mod (`patches/`) | The folder is empty. Changed 07:23 |
| Its build record (`builds/`) | The folder is empty. Changed 07:44 |
| The game's mod folder | No `Cold Steel build` mod, no Cold Steel patch link, no `stellaris_patcher_cold_steel_mix` link. Cold Steel synced the launcher at 15:51 |
| Our patch | Built on 6 October in `~/.local/share/stellaris-patcher/mods/cold_steel_mix_patch`. It's not in the playset. Its Workshop copy, `workshop:3812655652`, isn't subscribed |

## How it was worked out

- `check-update --notes`, in `~/.cache/stellaris-patcher/checks/2026-10-07_1556/`.
- The check counts changed files but doesn't name them. The changed file
  came from comparing UI Overhaul Dynamic's baseline manifest with its
  files now, then diffing the two copies.
- The sprite was looked up in every winning `interface/*.gfx` file.
- `cold-steel-mix` without `--write` gave the fixes' outcomes.
- Cold Steel's state came from its data folder and the game's mod folder.

## Limits

- **Nothing about play.** No game was run.
- **The rest of UI Overhaul Dynamic's `fleet_view.gui`.** The game's copy
  didn't change since the baseline, so the check doesn't compare them. If
  4.5.2 added other fleet view elements that UI Overhaul Dynamic lacks,
  only an error log or a full diff against the game would show it.
- **Why Cold Steel's state is empty.** Only its files were read. The user
  said afterwards that it was cleared on purpose.
