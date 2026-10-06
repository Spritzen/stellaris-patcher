# Error log report: Cold Steel Mix build, fourth run, 3 October 2026

**The first run with the [Cold Steel Mix patch](../patches/cold-steel-mix.md).
Six of its seven fixes work. Fix 4 doesn't.** The patch aimed at 25 log
entries. 24 are gone. The one left is the zoom mismatch fix 4 was for:
`PLANET_SCALE_SYSTEM does not match in size with ZOOM_STEPS_SYSTEM`.

- **96 entries point at real problems, down from 121 in run 3.** None of them
  stops play.
- **The patch added no errors.** No entry names one of its files, and the
  override notices are the same 752 as run 3.
- **Why fix 4 failed isn't known yet.** Its file is in the build with the
  right 13 values. By the files, the game should see 13 zoom steps and 13
  planet scales. It doesn't. See [Fix 4](#fix-4-the-zoom-mismatch-is-still-there).
- **Everything else is the same as run 3**, mostly Starbase Extended 3.0
  (47 entries) and Diverse Rooms (28).

## The run

| | |
|---|---|
| Game | Stellaris 4.5.1 (Cygnus), native Linux |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`) |
| Built | 14:04:37 local time, from the 27-mod playset, 14 seconds before the game started |
| Log | `logs/error.log`, 6,589 lines, 6,565 entries |
| Session | Started 14:04, one galaxy generated at 14:06, saved and quit at 14:09 (game date 2201.01.13) |

The playset is run 3's 26 mods plus `Cold Steel Mix patch`, last. The build
record lists the patch's 9 files, and each matches the patch mod's copy byte
for byte.

## Compared with run 3

| Group | Run 3 | Run 4 | Change |
|---|---:|---:|---|
| Universal Resource Patch: resources not installed | 5,717 | 5,717 | None |
| Override notices | 752 | 752 | None |
| Problems | 121 | 96 | −25 |
| **Total** | **6,590** | **6,565** | |

Of the 25: 24 are the patch's fixes. The other is More Events Mod's ship-set
notice, which depends on the galaxy (an empire picked `mem_ancient_01`).

## The patch's fixes, checked against the log

| # | Fix | Run 3 entries | Run 4 | Works? |
|---|---|---:|---:|---|
| 1 | System Scale's old `.asset` copies | 2 | 0 | Yes. The Starlit and Voidspawn entries are gone. The Dyson sphere and catapult models never showed in a log, so still check those in game |
| 2 | Starlit Starbase gun slots | 4 | 0 | Yes |
| 3 | `nsc_starbases.txt` variables | 4 | 0 | Yes |
| 4 | Planet scales for Cinematic Camera's zoom steps | 1 | 1 | **No** |
| 5 | Sol neighbour names | 6 | 0 | Yes |
| 6 | More Events Mod's renamed PD trigger | 2 | 0 | Yes |
| 7 | Six missing text keys | 6 | 0 | Yes |
| | **Total** | **25** | **1** | |

Checked by searching the raw log too: no `MEDIUM_GUN_01*`,
`build_block_radius`, `starbase_formation_priority`, `sol_neighbor`,
`is_pd_planet_for_aqua_trait`, `starlit`, `voidspawn`, `rs_d_dark_matter`,
`fire_rate_reduction`, `hp_increased` or `nsc.requires`.

## Fix 4: the zoom mismatch is still there

**The patch's planet scales are in the build and should win, but the game
still finds a mismatch.** It's logged once, at 14:07:05 from `planet.cpp`.
That's during play, a minute after the galaxy was made, not while loading.

Only three files set these values:

| File | Zoom steps | Planet scales |
|---|---:|---:|
| The game's `00_defines.txt` | 7 | 7 |
| System Scale's `systemscale_defines.txt` | 8 | 8 |
| Cinematic Camera's `zzzzz_cc_defines.txt` | 13 | |
| The patch's `zzzzzz_stellaris_patcher_cold_steel_mix.txt` | | 13 |

If the last file by name wins, as
[merge_rules.json](../../src/stellaris_patcher/data/merge_rules.json) says,
the game gets Cinematic Camera's 13 steps and the patch's 13 scales. If the
first wins, it gets System Scale's 8 and 8. **Neither gives a mismatch, so
something in that picture is wrong.**

Ruled out, in the files:

- **Not a typo.** The file has 13 numbers, and so does Cinematic Camera's list.
- **Not the file's format.** It's a plain top-level `NGraphics = { … }` block,
  the same shape as System Scale's and Cinematic Camera's files. It's ASCII
  and the log has no parse error for it.
- **Not sort order.** Cinematic Camera doesn't set planet scales, so the
  patch only has to sort after `systemscale_defines.txt`. `z` beats `s` under
  any rule, with or without case.
- **Not another file.** Nothing else in the build or the game sets either
  value.

Still possible:

1. **The game doesn't apply a later file's array the way we assume.** The
   `common/defines` row in merge_rules.json comes from Irony and has never
   been checked in game.
2. **The game's `ZOOM_STEPS_SYSTEM` isn't Cinematic Camera's list as
   written.** The game has no define by that name. It only reads
   `ZOOM_STEPS_SYSTEM_PERCENTAGES`, and works out the steps during play.
   It might drop some, for example steps the camera can't reach in that
   system. That would fit an error logged once, a minute into play.

The two August logs, from an older game version and another playset, have
the same error. Cinematic Camera was installed then, but those logs don't say
whether it was loaded.

**Next step: one short test run to tell these apart.** Make the patch's
defines file also set `ZOOM_STEPS_SYSTEM_PERCENTAGES` back to System Scale's
own 8 steps, beside System Scale's 8 scales.

- **If the error goes**, the patch's file is read and wins, and cause 2 is
  likely. Then Cinematic Camera's 13 steps can't be matched by counting them.
- **If it stays**, the patch's file isn't winning, which is cause 1. Then
  `common/defines` needs a live check, like Cold Steel's `live_rules.py` did
  for the other folders.

Also look at planets at each system zoom step. If they look right, the error
may not matter in play.

## What's left, by mod

Run 3 covers each of these in detail. Nothing in them changed, except for the
rows the patch fixed.

| Mod | Entries | Matters? | Details |
|---|---:|---|---|
| Starbase Extended 3.0 | 47 | A little: duplicate `potential` blocks (6), missing buildings (5), the `category` trigger (2), orbital ring sections (2), starbase window (2), sounds and particles (19), animations (11) | [Run 3](2026-10-03-cold-steel-mix-errors-run-3.md#starbase-extended-30-56) |
| Diverse Rooms (All in One) | 28 | No | [Run 3](2026-10-03-cold-steel-mix-errors-run-3.md#diverse-rooms-all-in-one-28) |
| Real Space family, with Cinematic Camera | 9 | Cosmetic: System Scale's 6 infernal ring world textures, the zoom mismatch (1), Real Space 4.0's two `nospec.dds` mix-ups | [Run 3](2026-10-03-cold-steel-mix-errors-run-3.md#real-space-family-with-cinematic-camera-16) |
| The game's own | 5 | No | [Run 3](2026-10-03-cold-steel-mix-errors-run-3.md#the-games-own-5) |
| Descriptors, Just Star Names, Apocryphos | 7 | No | [Run 3](2026-10-03-cold-steel-mix-errors-run-3.md#small-things-7) |
| **Total** | **96** | | |

Planetary Diversity and More Events Mod have none left.

Cold Steel's error reader put 11 entries under "Game / unknown". 6 belong to
mods and are counted under them here: three `.anim` files (Starbase
Extended), `planets\nospec.dds` (Real Space 4.0), the zoom mismatch and the
Apocryphos track.

## What the patch could do next

| # | Problem | Status |
|---|---|---|
| 4 | Zoom steps and planet scales | Shipped, doesn't work. Run the test [above](#fix-4-the-zoom-mismatch-is-still-there) first |
| 8 | Starbase Extended's duplicate `potential` blocks, the `category` trigger, two missing buildings | Open, from [run 3](2026-10-03-cold-steel-mix-errors-run-3.md#what-a-patch-mod-could-fix). Needs reading what the author meant |
| 9 | Orbital ring sections, starbase window items, sounds, animations | Open, from run 3. Cosmetic |

## Did the merge cause anything?

**No.** Cold Steel's build record was saved 14 seconds before the game
started, so it matches this run. Every entry that names a file traces to one
of the 27 source mods or to the game.

## How this was worked out

- Ran Cold Steel's error reader (`ErrorReader`) read-only, from its mounted
  source, with its cache in a scratch folder, the same way as run 3.
- Moved 6 entries from "Game / unknown" to the mods they belong to.
- Compared each of the patch's 9 files with the build's copy, byte for byte,
  and checked the build record lists the patch last.
- Searched the raw log for each name the fixes were meant to remove.
- For fix 4: found every file in the build and the game that sets either
  value, counted the values, compared file formats and encodings, and looked
  for the define names in the game's binary.

**Limits.** One galaxy and about three minutes of play. Whether planets look
wrong at some zoom steps, and whether the newer-style megastructures from
fix 1 look right, wasn't checked in game.
