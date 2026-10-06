# Game report: Cold Steel Mix build, solid-colour background, 3 October 2026

**About an hour into play, the background turned one solid colour when
entering a system. It stayed that way back in the galaxy view. The game
logged nothing about it.** The error log's last entry is from 16 seconds
after the galaxy was made. The next 57 minutes of play left nothing there.

- **Cause, confirmed in game: our patch's fix 4 left Cinematic Camera's
  `ENTER_SYSTEM_ZOOM_STEP = 12` pointing at a zoom step that no longer
  exists.** Fix 4 now cuts the system zoom steps to System Scale's 8 (steps
  0–7). Nothing reset the step the camera jumps to on entering a system.
  With the fix, Baku opens normally. See
  [the zoom step](#the-likely-cause-a-zoom-step-past-the-end).
- **This build is the first long session with that change.** Run 4 had 13
  steps, so step 12 was valid then.
- **Ruled out, in the files:** Real Space's system-view scenes, its
  colour-correction tables, its copy of the game's mesh shader, and every
  star class in the save. See [Ruled out](#ruled-out).
- **Fix 4's test worked.** The zoom mismatch from
  [run 4](2026-10-03-cold-steel-mix-errors-run-4.md#fix-4-the-zoom-mismatch-is-still-there)
  is gone from the log. This was already recorded in
  [decision 17](../decisions.md).

## The run

| | |
|---|---|
| Game | Stellaris 4.5.1 (Cygnus), native Linux, OpenGL, GTX 1080 Ti, NVIDIA 580.178.04 |
| Loaded | One mod: `Cold Steel build: Cold Steel Mix` (playset `d8f5e037…`), 27 mods with `Cold Steel Mix patch` last |
| Built | 14:41:54 local time (UTC+1), 20 seconds before the game started |
| Session | Started 14:42. Galaxy made at 14:43. Played until 15:40, from 2200.01.01 to 2204.08.26 |
| Save | `save games/elvendivineorder_-1604279663/2204.08.26.sav` |
| Empire | Elven Divine Order. Home system Ar, a triple G star |
| Logs | `error.log`, 6,589 lines, last entry 14:43:35. `game.log` has events until 15:39 |

Settings that matter for graphics: borderless window at 1920×1080,
`gfx_quality=2`, bloom quality 1, no lens flare, no multisampling, vsync on.

## What the logs say

**Nothing about the background.** Every error-log entry comes from loading
or from the first 16 seconds of the new galaxy. `game.log` shows events
being picked until 15:39, so the game kept logging to its other files.

There are no crash dumps or exception files. The container can't read the
host's kernel log, so an NVIDIA driver error (an "Xid" line) can't be ruled
out from here.

Events seen during play were vanilla, More Events Mod and Real Space's
start menu (closed without changes). None of them changes how a system looks.

## The likely cause: a zoom step past the end

**After fix 4, the game has 8 system zoom steps but is told to enter
systems at step 12.** Steps count from 0, so 12 is the 13th step.

| Setting | Game | System Scale | Cinematic Camera | Patch | What the game gets |
|---|---:|---:|---:|---:|---:|
| `ZOOM_STEPS_SYSTEM_PERCENTAGES` | 7 steps | 8 steps | 13 steps | 8 steps | **8 steps (0–7)** |
| `PLANET_SCALE_SYSTEM` | 7 | 8 | | 8 | 8 |
| `ENTER_SYSTEM_ZOOM_STEP` | 6 | 7 | 12 | | **12: out of range** |
| `FOCUS_START_ZOOM_STEP` | 4 | 3 | 6 | | 6: in range, but a different distance |
| `SYSTEM_FOCUS_PLANET_STEP` | | 2 | | | 2 |
| `ZOOM_STEPS_SHOW_FLEET_HEALTH_BARS` | 3–6 | | 3–6 | | 3–6 |
| `LEAVE_SYSTEM_ZOOM_STEP` | 1 | 2 | 3 | | 3, a galaxy step: fine |

The last file to set a value wins. The fix-4 test showed this for the
zoom steps.

**Why it fits:**

- It happens on entering a system, which is exactly when this setting is used.
- It came in with this build. In run 4 there were 13 steps.
- Reading a step that isn't there can give the camera a nonsense distance.
  A broken camera can't draw the 3D scene, so only the clear colour shows.
  The game also carries its screen brightness over from frame to frame,
  in system and galaxy view alike. One broken value there would stay after
  leaving the system.

**What doesn't fit yet:** if every system entry broke, it would have shown
up long before an hour in. Reading past the end of a list gives whatever is
in memory there, which can change. Or the game may clamp the step, and this
is a separate bug.

**Fix:** fix 4 should also set the steps that point into the zoom list to
System Scale's own values: `ENTER_SYSTEM_ZOOM_STEP = 7` and
`FOCUS_START_ZOOM_STEP = 3`. And it should check that every step index is
inside the list, so a later change can't leave one past the end.

## Ruled out

| Checked | Result |
|---|---|
| Real Space's `gfx/FX/pdxmesh.shader` | The game's 4.5 file unchanged, with 411 lines added at the end. The added effects call shader code that doesn't exist (`PixelOmniMeshShip` and others), but no model uses them |
| Real Space's `rs_pdxmesh.shader` | Only used for planet rings. Same maths as the game's own additive shader |
| Every scene file in `gfx/worldgfx/`, 65 of them, 44 from Real Space and one from More Events Mod | Every texture they name exists. HDR, tonemap and bloom values are the same as the game's own star scenes |
| Real Space's colour-correction tables | Same size and format as the game's (1024×32, 24-bit) |
| Star classes | All 227 have a scene file. The save uses no class the build doesn't define |
| Other shaders | Only Real Space ships any. The sky, bloom and post-processing shaders are the game's own |
| Shader cache | None to clear: on OpenGL the game compiles shaders each run |

## Baku reproduces it

**Reloading the save and entering Baku broke the background again.** The
camera zoomed in fast first, then the screen went one colour. So it's tied to
the system, and the camera dive is part of it.

Baku is a normal size (outer radius 454, like Lari Castellum's). What sets it
apart is its biggest star sitting near the centre, where the camera aims:

| System | Biggest star near the centre | Distance from centre |
|---|---|---:|
| Baku | G, size 34 | 20.5 |
| Omega Columbae | T Tauri, size 33 | 20.1 |
| Mu Camelopardalis | G, size 27 | 25.1 |
| Ar | G, size 24 | 25.1 |
| Lari Castellum, Albaldah | One star, at the centre | 0 |

This fits a camera sent far too close by a step past the end: in Baku it
ends up inside the G star. If so, **Omega Columbae should break the same
way**. Real Space's rings aren't the cause: 387 systems have them, Ar and
Lari Castellum among them.

## The fix

**Confirmed on 3 October: after rebuilding, the same save entered Baku
normally.**

**Fix 4 now also ships System Scale's own `ENTER_SYSTEM_ZOOM_STEP = 7` and
`FOCUS_START_ZOOM_STEP = 3`.** It checks every setting that names a system
zoom step, and leaves the fix out if one would still point past the end.

## Still to check

- **Entering a system now lands on System Scale's widest system view**
  instead of Cinematic Camera's. That's expected with 8 steps.
- If a solid background comes back, note the system and the colour, and
  check the host's kernel log for driver errors in that session:
  `journalctl -k -b | grep -i xid`.

## How this was worked out

- Read the timestamps of every file in the game's user folder and logs, and
  matched them to the build time and the save times.
- Counted the error log by source, and searched it for shaders, textures and
  the zoom mismatch.
- Listed every graphics file in the build record that touches shaders,
  scenes, skies, nebulae and the map, with the mod it came from.
- Compared Real Space's mesh shader and colour tables with the game's.
- Read every scene file in the build, checked the textures it names exist,
  and checked that each star class's `class` has a matching scene.
- Unpacked the save into a scratch folder and read its systems, the player's
  fleets and their locations with
  [script.py](../../src/stellaris_patcher/paradox/script.py).
- Listed every define in the build that points at a zoom step, and compared
  each with the length of the step list the game ends up with.

**Limits.** No log entry ties the bug to a cause; the fix was confirmed by
entering Baku again. Whether the camera really ended up inside the G star
wasn't checked, and Omega Columbae wasn't tried.
