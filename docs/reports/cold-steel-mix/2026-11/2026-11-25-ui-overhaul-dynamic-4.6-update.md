# Update check: Cold Steel Mix, UI Overhaul Dynamic, 25 November 2026

**UI Overhaul Dynamic updated this morning, at 06:43. Its bottom bar now
has 4.6's Ideological Border Mode toggle, the one thing in the playset's
Left to the authors list. The line was dropped after this report, and the
list is empty. The update also
finishes its Willpower interface: the galaxy view, the outliner, the planet
view, the factions window and the megastructure view lose their `#UIOD_WIP`
markers, and it now ships its own Ideologies window. Nothing in it touches
the patch. All 35 fixes build, and a fresh build matches the written patch
byte for byte. No other mod and no game file changed, and nothing in the
check is new. Cold Steel's build, from 24 November at 22:06, predates the
update, so it needs a rebuild before play.**

- **The border toggle is there.** The game's `main_bottom.gui` has a
  `toggle_mapmode_ideologies` button in its map filters, beside the sectors
  and hyperlanes toggles. Its tooltip, `TOGGLE_MAPMODE_IDEOLOGIES_INFO`,
  says it "highlights the borders of all known Ideologies". UI Overhaul
  Dynamic's `Ω_uiod_main_bottom.gui` now has the same button and its
  `GFX_map_mode_ideologies` icon, first in its filter row. The sectors,
  hyperlanes and players toggles move one place right. Every named element
  in the game's bottom bar is now in UI Overhaul Dynamic's, except two
  decorations it never had: `map_button_bg` and `mapmode_divider`.
- **Its Ideologies window is complete.** The new `interface/ideologies.gui`
  is a restyled copy of the game's, with every element the game's has. The
  ideology editor and the map icons are still the game's files, as UI
  Overhaul Dynamic doesn't replace them.
- **The other changes are layout.** The ideology window and the war status
  icon move in the galaxy view, its column headers are resized, and the
  outliner's ideology entries take the outliner's width. The factions
  window's ethic slots widen from 75 to 100 px. The megastructure view's
  Modules tab is redrawn. None of these files is in the patch or in another
  playset mod.
- **`100%%` is UI Overhaul Dynamic's own habit.** Two new lines size a
  window `100%%`. UI Overhaul Dynamic has 190 such lines in 34 files, and
  the game has 8. It isn't a new problem.

## What to do next

1. **Done** 25 November: **drop the UI Overhaul Dynamic line from
   [Left to the authors](../../../patches/cold-steel-mix.md#left-to-the-authors).**
   UI Overhaul Dynamic now has the toggle. `LEFT_TO_AUTHORS` in
   [cold_steel_mix.py](../../../../src/stellaris_patcher/patchmod/cold_steel_mix.py)
   becomes empty, so the Workshop description loses its "Known issues"
   section. The code already handles an empty list, and a test covers it.
   Note it in [decision 69](../../../decisions.md), and in the next patch
   notes.
2. **Rebuild.** Run `cold-steel-mix --write`, then rebuild Cold Steel Mix
   in Cold Steel: its build predates this update. The patch was written on
   25 November.
3. **Done** with this report: **accept the check** with
   `check-update --accept`, so the baseline holds this UI Overhaul Dynamic.
4. **In the next game run, look at** the bottom bar's map filters: the
   Ideological Border Mode toggle should show borders once an Ideology is
   known. Also look at the galaxy view's empire list, where the ideology
   and war status columns moved.

## UI Overhaul Dynamic

Its version stays `4.6.*`, for `v4.6.*`. 8 files changed, 2 of them new.

| File | Then | Now | Result |
|---|---|---|---|
| `Ω_uiod_main_bottom.gui` | No ideology toggle in the map filters | `toggle_mapmode_ideologies` and its icon, as in the game | The Left to the authors line can go. Item 1 |
| `ideologies.gui` | None, so the game's | Its own, with every game element | Ok |
| `ideology_tab_bottom_bg.dds` | None | New background for the Ideologies tab | Ok |
| `galaxy_view.gui` | Ideology window and column marked `#UIOD_WIP` | Placed and sized. War status header narrower | Ok. Item 4 |
| `outliner.gui` | 4.5-style ideology entry | Uses the outliner's width variables | Ok |
| `planet_view.gui` | Ideology window marked `#UIOD_WIP` | Moved a few pixels | Ok |
| `topbar_factions_view.gui` | 75 px ethic slots | 100 px, room for the percentage | Ok |
| `megastructure_view.gui` | Modules tab in the 4.5 layout | Redrawn in UI Overhaul Dynamic's style | Ok |

Only the game and UI Overhaul Dynamic have these 8 paths. Dark UI and
Extended Topbar don't. Fix 30 copies UI Overhaul Dynamic's starbase window,
which didn't change. Its notes are as before: Upgrade and Station Details
swap places, and the slots take Starbase Extended's sizes.

## How it was worked out

- `check-update --notes`, in `~/.cache/stellaris-patcher/checks/2026-11-25_1834/`.
  No new patch notes, no game file changed, one mod changed. The 3
  undefined variables and the 830 older copies were all reviewed before.
  Planetary Diversity - Planet View shows as removed, as it was switched
  off on 24 November ([decision 72](../../../decisions.md)).
- UI Overhaul Dynamic's 8 changed files were read from the baseline's
  snapshot and the Workshop folder, and diffed.
- The element names in the game's `main_bottom.gui` and `ideologies.gui`
  were compared with UI Overhaul Dynamic's copies.
- Every layer's files were searched for the 8 paths.
- The patch was built in memory and compared with the written patch: 69
  files, all the same.

## Limits

- **Nothing about play.** Whether the toggle draws the borders needs a run.
- **Positions weren't judged.** Moved elements may overlap at some
  resolutions. Only a look in game shows it.
- **The `.dds` file wasn't looked at.** It's an image, compared by size.
