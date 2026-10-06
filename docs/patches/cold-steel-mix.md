# Cold Steel Mix patch

**A mod named "Cold Steel Mix patch" that fixes ten problems in the Cold
Steel Mix playset.** They're fixes 1–7 from the
[third run's report](../reports/2026-10-03-cold-steel-mix-errors-run-3.md#what-a-patch-mod-could-fix),
fix 10 from the
[long-session report](../reports/2026-10-04-cold-steel-mix-long-session.md#what-to-do-next),
and fixes 11 and 12 from the
[new-galaxy report](../reports/2026-10-05-cold-steel-mix-new-galaxy.md#what-to-do-next).
The code is [cold_steel_mix.py](../../src/stellaris_patcher/patchmod/cold_steel_mix.py).

## Build it

```sh
PYTHONPATH=src python3 -m stellaris_patcher cold-steel-mix              # show what it would write
PYTHONPATH=src python3 -m stellaris_patcher cold-steel-mix --write      # write it and link it
PYTHONPATH=src python3 -m stellaris_patcher cold-steel-mix --write --add-to-playset --cold-steel-closed
```

- The mod is written to `~/.local/share/stellaris-patcher/mods/cold_steel_mix_patch/`.
  The game's mod folder gets a link, `mod/stellaris_patcher_cold_steel_mix`,
  and a `.mod` file beside it ([decision 15](../decisions.md)).
- Its thumbnail is Cold Steel's icon with the sword in emerald
  instead of silver:
  [patch-icon.svg](../../src/stellaris_patcher/data/patch-icon.svg), rendered
  to `thumbnail.png` beside it with `rsvg-convert -w 512 -h 512`. Render it
  again after changing the SVG.
- The build skips the patch itself, under its local key and, once uploaded,
  its Workshop key (`workshop:` and the `remote_file_id` in its descriptor).
  Otherwise it reads its own files as another mod's and leaves every fix out.
- `--add-to-playset` puts it last in Cold Steel's Cold Steel Mix playset,
  as `local:stellaris_patcher_cold_steel_mix`. It leaves the playset alone
  when the Workshop copy is already in it. Close Cold Steel first. In the
  container, pass `--cold-steel-closed` once the user says it's closed.
- Then **rebuild Cold Steel Mix in Cold Steel**. You play the built mod, and
  it only has the patch once it's rebuilt.

**Run it again after every game or mod update.** Each fix is worked out from
the files on disk, not from a saved copy ([decision 14](../decisions.md)). If
an update changes a fix's cause, that fix is left out and the reason printed.
The other fixes are still written.

## Add a fix

**Only once the user has agreed to it** ([decision 25](../decisions.md)).

1. Write a `fix_…(layers) -> Made` function in
   [cold_steel_mix.py](../../src/stellaris_patcher/patchmod/cold_steel_mix.py),
   under a `# N. …` comment, and add it to `FIXES` with its number, title and
   the mods it patches. It raises `FixError` when its cause is gone
   ([decision 14](../decisions.md)).
2. Test it in [test_patchmod.py](../../tests/test_patchmod.py): one test that
   it fixes the problem, one that it's left out once the cause is gone.
3. Add a row to [What each fix does](#what-each-fix-does), and to the
   [Whose work](#uploading-it-to-the-workshop) table if it ships another
   author's file. Mark the fix **Done** in the report it came from.
4. Add a row to [decisions.md](../decisions.md) for any choice the fix makes.
5. `make check`, then [build it](#build-it).

## Uploading it to the Workshop

It's uploaded as `workshop:3812655652`. Each build keeps it ready for the
next upload
([decisions 20 and 21](../decisions.md)):

- `descriptor.mod` has the name, a dated version, tags (`Fixes`,
  `Graphics`), the thumbnail, `supported_version`, and `dependencies`: the
  mods the written fixes patch, by the names their own descriptors give.
- The Workshop description is in
  `~/.local/share/stellaris-patcher/mods/cold_steel_mix_patch.workshop.txt`.
  Paste it into the Workshop page.
- Upload it from the Paradox launcher. The launcher saves the Workshop id in
  the `.mod` file, and later builds keep it, so the next upload updates the
  same Workshop item.
- On the Workshop page, add the same mods as **Required items**. Steam doesn't
  read `dependencies`.

**Ask the other authors first.** The patch ships work that isn't ours:

| File | Whose work |
|---|---|
| `common/ship_sizes/nsc_starbases.txt` | Starbase Extended 3.0's whole file, with two lines added |
| `common/solar_system_initializers/stellaris_patcher_cold_steel_mix_sol_neighbors.txt` | Three of Real Space 4.0's systems, copied |
| The three `.asset` files | The game's files, with Real Space - System Scale's sizes |
| `events/!!_stellaris_patcher_cold_steel_mix_ziaskehorn.txt` | One of More Events Mod's events, with two lines moved |
| `events/!!_stellaris_patcher_cold_steel_mix_stuck_in_glacier.txt` | One of More Events Mod's events, with one word changed |

The game's own files are fine to ship in a mod. The others need their
authors' permission, or fixes 3, 5, 11 and 12 left out.

## What each fix does

| # | Problem | What the patch ships |
|---|---|---|
| 1 | System Scale's old `.asset` copies drop 116 game entities | The game's own copies of the three files, sized the way System Scale sizes them. Dyson spheres: `@dyson_scale` 35 → 140. Quantum catapults: every entity ×3, except three lightning effects System Scale leaves alone. System effects: storms 20 → 120, Starlit 4 → 24, Voidspawn 15 → 90 ([decision 18](../decisions.md)) |
| 2 | The Starlit Starbase design uses citadel slots `MEDIUM_GUN_010`–`013` | The game's `biogenesis_ship_designs.txt`, with that design's slots moved to Starbase Extended's `_10`–`_12`. `_013` has no match, so that gun is dropped: 12 of 13 guns ([decision 16](../decisions.md)) |
| 3 | `nsc_starbases.txt` uses two variables it doesn't define | Starbase Extended's file, with `@build_block_radius_starbase = 20` and `@starbase_formation_priority = 1` at the top |
| 4 | Cinematic Camera's 13 zoom steps meet System Scale's 8 planet scales | A defines file that sorts last, with System Scale's own 8 zoom steps and 8 planet scales, and its own step for entering a system (7) and focusing (3). Cinematic Camera's finer system zoom is lost ([decision 17](../decisions.md)) |
| 5 | Planetary Diversity and More Events Mod use the game's Sol neighbour names | `sol_neighbor_t1`, `sol_neighbor_t2` and `sol_neighbor_t1_no_guaranteed_colony`, as copies of Real Space's systems for the same stars |
| 6 | More Events Mod calls Planetary Diversity's trigger by its old name | `is_pd_planet_for_aqua_trait`, which calls `pd_is_planet_for_aqua_trait` |
| 7 | Six text keys are missing | One English file ([decision 19](../decisions.md)) |
| 10 | Planetary Diversity's text calls `[GetAdministratorPluralWithIcon]`, which the game no longer has | A `localisation/replace/` file. The bureaucrats' unity modifier gets the game's own text. The three necro world tooltips keep Planetary Diversity's text, calling the game's `$bureaucrat_type_plural_with_icon$` instead ([decision 22](../decisions.md)) |
| 11 | More Events Mod's `mem_scfe_ziaskehorn.1` fires the discovery before saving the planet it's about, so the Ziaskehorn dig site is never made | A copy of that one event, with the `save_event_target_as` block moved above the `ship_event` call. It's in an `events/` file whose name starts `!!_`, so it sorts first and wins ([decision 23](../decisions.md)) |
| 12 | More Events Mod's `mem_stuck_in_glacier.22` makes an official with Iron Fist, a commander-only trait since 4.0, so the leader gets no trait | A copy of that one event, the same way as fix 11. That leader is a commander, the one class the game's Iron Fist allows ([decision 24](../decisions.md)) |

### Notes

- **Fix 2 gets back three guns, not four.** The report says Starbase
  Extended's slots go up to `_20`. They stop at `_12`.
- **Fix 5 matches stars by name, not as the report guessed.** The game's
  `sol_neighbor_t2` is Procyon, so it becomes Real Space's
  `procyon_mediumsector`, not Sirius. Before copying, the fix checks that
  both systems have the same `name`.
- **Fix 4 can't keep Cinematic Camera's 13 steps.** 13 matching planet
  scales still logged the mismatch. Only System Scale's own 8 and 8 cleared it
  ([decision 17](../decisions.md)).
- A fix that ships a whole file only does so while that file still comes
  from the expected mod or the game. Otherwise it could undo another mod's
  newer copy. Fixes 11 and 12 do the same for one event: More Events Mod's
  copy must be the one the game uses.
- **Fixes 11 and 12 copy the whole event**, and the game then has two events
  with one id. More Events Mod's copy is still loaded, but never used.

## Check in game

**Fixes 1–7 cleared every log entry they aimed at**, in the
[fourth run](../reports/2026-10-03-cold-steel-mix-errors-run-4.md) and, for
fix 4, the [solid-background run](../reports/2026-10-03-cold-steel-mix-solid-background.md).
Later runs found none back.

These weren't seen in game yet:

- The bureaucrats' unity line in a planet's tooltip names the job, and the
  error log has no `GetAdministratorPluralWithIcon` (fix 10).
- Planets look right at every system zoom step (fix 4).
- A Dyson sphere, quantum catapult, Starlit system and Voidspawn storm in a
  newer style look the right size next to the older styles (fix 1).
- The game uses the patch's copy of each event, not More Events Mod's, and
  the log has no new entry about the duplicate ids (fixes 11 and 12). Both
  are rare: the Ziaskehorn roll is 1 in 10 on a molten or volcanic survey
  after year 20, and the Iron Fist leader 1 in 4 when the robot is brought
  online. A new save with the `discovered_ziaskehorn` flag should have the
  dig site too.
