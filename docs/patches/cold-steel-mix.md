# Cold Steel Mix patch

**A mod named "Cold Steel Mix patch" that fixes 15 problems in the Cold
Steel Mix playset.** They're fixes 1–7 from the
[third run's report](../reports/2026-10-03-cold-steel-mix-errors-run-3.md#what-a-patch-mod-could-fix),
fix 10 from the
[long-session report](../reports/2026-10-04-cold-steel-mix-long-session.md#what-to-do-next),
fixes 11 and 12 from the
[new-galaxy report](../reports/2026-10-05-cold-steel-mix-new-galaxy.md#what-to-do-next),
and fixes 15–17 and 19 from the
[4.5.2 first-run report](../reports/2026-10-07-cold-steel-mix-4.5.2-first-run.md#what-to-do-next),
and fix 25 from the localisation errors Cold Steel lists for the playset.
Problems it leaves to the mods' authors are listed on its Workshop page
([Left to the authors](#left-to-the-authors)).
Fixes 2 and 3 are left out for now: their mod is
[switched off](#mods-switched-off-for-now).
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
The other fixes are still written. A fix is left out too when none of the mods
it patches is switched on in the playset.

## Mods switched off for now

**Two mods are switched off in the playset until they update for 4.5.2**
([decision 35](../decisions.md)). They stay in the playset, so they're one
switch from coming back. The Workshop description ends with them, and says
we aim to put them back: `SWITCHED_OFF` in
[cold_steel_mix.py](../../src/stellaris_patcher/patchmod/cold_steel_mix.py),
one line per mod. The section goes once the list is empty.

| Mod | Why | Fixes left out |
|---|---|---|
| Starbase Extended 3.0 | 47 load errors each run, a starbase window from before 4.5, and the modules, buildings and sections in [Left to the authors](#left-to-the-authors) | 2, 3, and its text key in 7 |
| Smarter Hyper Relays: Improved AI (shrimpAI) | A Nomadic empire can't build a Hyper Relay at its own waystation | None |

To bring one back:

1. Switch it on in Cold Steel's Cold Steel Mix playset, in the same place.
2. [Build the patch](#build-it). Its fixes come back if the update still
   needs them, and are left out with a reason if not.
3. Read the [first report after 4.5.2](../reports/2026-10-07-cold-steel-mix-4.5.2-first-run.md)
   for what it still breaks. Put the lines it still needs back in
   `LEFT_TO_AUTHORS`. They were taken out in the change that switched it off.
   Drop its line from `SWITCHED_OFF`.
4. At the next upload, add it back to the Workshop page's **Required items**.

**Switching a mod off can put another mod's older copy back in use.** With
Ascension Worlds off, Planetary Diversity's Lithoid Budding came back
([three-mods-off report](../reports/2026-10-09-cold-steel-mix-three-mods-off.md#planetary-diversitys-lithoid-budding)).
After switching one off, run the [update check](../update-check.md) and read
the copies it lists as new.

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
- The Cold Steel Mix collection's background is drawn by
  [collection_background.py](../../tools/collection_background.py): the
  patch icon and name on the left, Tron-style lines on the right. Render it
  to `mods/cold_steel_mix_collection.png`:

  ```sh
  python3 tools/collection_background.py /tmp/bg.svg
  rsvg-convert -w 1920 -h 1080 /tmp/bg.svg -o ~/.local/share/stellaris-patcher/mods/cold_steel_mix_collection.png
  ```

- Upload it from the Paradox launcher. The launcher saves the Workshop id in
  the `.mod` file, and later builds keep it, so the next upload updates the
  same Workshop item.
- On the Workshop page, add the same mods as **Required items**. Steam doesn't
  read `dependencies`. Remove any it no longer lists: at the next upload,
  Starbase Extended 3.0 ([switched off](#mods-switched-off-for-now)). Keep
  Planetary Diversity - Ascension Worlds, which is back on. Add Planetary
  Diversity - More Arcologies, which fix 25 patches.

### Left to the authors

**The description ends with the playset's known problems that the patch
doesn't fix**, under "Known issues, waiting for the mod authors"
([decision 33](../decisions.md)). They're in `LEFT_TO_AUTHORS` in
[cold_steel_mix.py](../../src/stellaris_patcher/patchmod/cold_steel_mix.py),
written by hand, one line per problem.

- Add a line when a report leaves a problem to a mod's author.
- Drop it once the mod fixes it. The [update check](../update-check.md) shows
  when one of these mods changes.

Today's lines come from the
[4.5.2 first-run report](../reports/2026-10-07-cold-steel-mix-4.5.2-first-run.md)
(item 18, and the findings for Planetary Diversity's Aquatic trait and Dark
UI) and the [pre-upload report](../reports/2026-10-07-cold-steel-mix-pre-upload.md#what-to-do-next)
(item 20, the Lost Emperor).

**Ask the other authors first.** The patch ships work that isn't ours:

| File | Whose work |
|---|---|
| `common/ship_sizes/nsc_starbases.txt` | Starbase Extended 3.0's whole file, with two lines added |
| `common/solar_system_initializers/stellaris_patcher_cold_steel_mix_sol_neighbors.txt` | Three of Real Space 4.0's systems, copied |
| The three `.asset` files | The game's files, with Real Space - System Scale's sizes |
| `events/!!_stellaris_patcher_cold_steel_mix_ziaskehorn.txt` | One of More Events Mod's events, with two lines moved |
| `events/!!_stellaris_patcher_cold_steel_mix_stuck_in_glacier.txt` | One of More Events Mod's events, with one word changed |
| `common/component_templates/mutation_weapon_components.csv` | Real Space - Ships in Scaling's whole file, with one range changed |
| `common/solar_system_initializers/!!_stellaris_patcher_cold_steel_mix_supercomputer.txt` | One of Real Space 4.0's systems, with one flag removed |
| `common/traits/!!_stellaris_patcher_cold_steel_mix_lithoid_budding.txt` | Lithoid Budding from Ascension Worlds, or from Planetary Diversity while Ascension Worlds is off, with one line added |
| `common/game_rules/zz_stellaris_patcher_cold_steel_mix_terraform.txt` | Ascension Worlds' terraforming rule, with two of the game's checks added |
| Seven `localisation/<language>/planetarydiversity_…` files | Planetary Diversity's whole files, with broken lines mended |
| Ten `localisation/<language>/planetarydiversity_aw_…` files | Planetary Diversity - Ascension Worlds' whole files, with one line mended in each |
| Two `localisation/<language>/planetarydiversity_more_arcologies_…` files | Planetary Diversity - More Arcologies' whole files, with one line mended in each |

The game's own files are fine to ship in a mod. The others need their
authors' permission, or fixes 3, 5, 11, 12, 16, 17, 19 and 25 left out. Fix 3
isn't shipped while Starbase Extended is
[switched off](#mods-switched-off-for-now).

## What each fix does

| # | Problem | What the patch ships |
|---|---|---|
| 1 | System Scale's old `.asset` copies drop 116 game entities | The game's own copies of the three files, sized the way System Scale sizes them. Dyson spheres: `@dyson_scale` 35 → 140. Quantum catapults: every entity ×3, except three lightning effects System Scale leaves alone. System effects: storms 20 → 120, Starlit 4 → 24, Voidspawn 15 → 90 ([decision 18](../decisions.md)) |
| 2 | The Starlit Starbase design uses citadel slots `MEDIUM_GUN_010`–`013` | The game's `biogenesis_ship_designs.txt`, with that design's slots moved to Starbase Extended's `_10`–`_12`. `_013` has no match, so that gun is dropped: 12 of 13 guns ([decision 16](../decisions.md)) |
| 3 | `nsc_starbases.txt` uses two variables it doesn't define | Starbase Extended's file, with `@build_block_radius_starbase = 20` and `@starbase_formation_priority = 1` at the top |
| 4 | Cinematic Camera's 13 zoom steps meet System Scale's 8 planet scales | A defines file that sorts last, with System Scale's own 8 zoom steps and 8 planet scales, and its own step for entering a system (7) and focusing (3). Cinematic Camera's finer system zoom is lost ([decision 17](../decisions.md)) |
| 5 | Planetary Diversity and More Events Mod use the game's Sol neighbour names | `sol_neighbor_t1`, `sol_neighbor_t2` and `sol_neighbor_t1_no_guaranteed_colony`, as copies of Real Space's systems for the same stars |
| 6 | More Events Mod calls Planetary Diversity's trigger by its old name | `is_pd_planet_for_aqua_trait`, which calls `pd_is_planet_for_aqua_trait` |
| 7 | Six text keys are missing. Five while Starbase Extended is off | One English file ([decision 19](../decisions.md)) |
| 10 | Planetary Diversity's text calls `[GetAdministratorPluralWithIcon]`, which the game no longer has | A `localisation/replace/` file. The bureaucrats' unity modifier gets the game's own text. The three necro world tooltips keep Planetary Diversity's text, calling the game's `$bureaucrat_type_plural_with_icon$` instead ([decision 22](../decisions.md)) |
| 11 | More Events Mod's `mem_scfe_ziaskehorn.1` fires the discovery before saving the planet it's about, so the Ziaskehorn dig site is never made | A copy of that one event, with the `save_event_target_as` block moved above the `ship_event` call. It's in an `events/` file whose name starts `!!_`, so it sorts first and wins ([decision 23](../decisions.md)) |
| 12 | More Events Mod's `mem_stuck_in_glacier.22` makes an official with Iron Fist, a commander-only trait since 4.0, so the leader gets no trait | A copy of that one event, the same way as fix 11. That leader is a commander, the one class the game's Iron Fist allows ([decision 24](../decisions.md)) |
| 15 | More Events Mod's three Progenitor shields use `@shield_*_t7_upkeep_*`, which 4.5.2 renamed to `@defense_*_t7_upkeep_*`, so they have no upkeep | A `common/scripted_variables/` file that defines each old name a component still uses, with the game's value for its new name |
| 16 | Ships in Scaling's copy of `mutation_weapon_components.csv` predates 4.5.2, so the Large Mega Bombard keeps a range of 2 | Ships in Scaling's whole file, with each range it missed set to the one it gives every other weapon with the same game range: 100 → 17. A range is only changed when at least two other rows agree ([decision 31](../decisions.md)) |
| 17 | Real Space 4.0's copy of the Surveillance Supercomputer system keeps the `sealed_system` flag 4.5.2 removed, so jump drive fleets can't enter | A copy of that one system without the flag, in a file whose name starts `!!_`. Initializers go to the first file by name |
| 19 | Planetary Diversity's and Ascension Worlds' Lithoid Budding lack 4.5.2's `divide_over_pop_groups = no` on the Massive Crater bonus. Ascension Worlds' terraforming rule lacks the game's checks for a consecrated world and a Knights detox in progress | A copy of the trait in use, with the game's line added, in a `!!_` file. Both mods ship a whole `04_species_traits.txt`, and Ascension Worlds' replaces Planetary Diversity's, so the copy is from whichever is on ([decision 37](../decisions.md)). Only Ascension Worlds has the rule: a copy of it, with the two checks added, in a `zz_` file: game rules go to the last file by name. The legendary leader check Ascension Worlds comments out on purpose stays out ([decision 32](../decisions.md)) |
| 25 | Lines in Planetary Diversity's, Ascension Worlds' and More Arcologies' translations the game can't read: quotes missing (German, Russian, Polish), text with no key (German, and Ascension Worlds' flooded world tooltip in all nine translations), and German obsidian world text pasted in after its own key (also Japanese, Korean and Russian, which read but show the key) | Each broken file whole, at its own path, with the lines mended. The keyless line takes the key the mod's English file has in its place ([decision 39](../decisions.md)). A file whose line no rule mends is skipped |

### Notes

- **Fix 2 gets back three guns, not four.** The report says Starbase
  Extended's slots go up to `_20`. They stop at `_12`.
- **Fix 5 matches stars by name, not as the report guessed.** The game's
  `sol_neighbor_t2` is Procyon, so it becomes Real Space's
  `procyon_mediumsector`, not Sirius. Before copying, the fix checks that
  both systems have the same `name`.
- A fix that ships a whole file only does so while that file still comes
  from the expected mod or the game. Otherwise it could undo another mod's
  newer copy. Fixes 11 and 12 do the same for one event: More Events Mod's
  copy must be the one the game uses.
- **Fixes 11 and 12 copy the whole event**, and the game then has two events
  with one id. More Events Mod's copy is still loaded, but never used.
  Fixes 17 and 19 do the same for one system, one trait and one rule.
- **Fix 15 doesn't name More Events Mod.** It defines every old shield upkeep
  name any component uses and nothing defines.
- **Fix 18 isn't in the patch.** The trait copies from Planetary Diversity,
  Ascension Worlds and More Events Mod would be 18 traits from three mods, for
  a one-word change each. It's [left to their authors](#left-to-the-authors).

## Check in game

**Fixes 1–7 cleared every log entry they aimed at**, in the
[fourth run](../reports/2026-10-03-cold-steel-mix-errors-run-4.md) and, for
fix 4, the [solid-background run](../reports/2026-10-03-cold-steel-mix-solid-background.md).
Later runs found none back.

**Fix 25 cleared every localisation error Cold Steel's health check listed**:
Planetary Diversity's and More Arcologies' 7, and on 9 October Ascension
Worlds' 10, once it was back on. Cold Steel's health check passes.

These weren't seen in game yet:

- The bureaucrats' unity line in a planet's tooltip names the job, and the
  error log has no `GetAdministratorPluralWithIcon` (fix 10).
- Planets look right at every system zoom step (fix 4).
- A Dyson sphere, quantum catapult, Starlit system and Voidspawn storm in a
  newer style look the right size next to the older styles (fix 1).
- The game uses the patch's copy of each event, not More Events Mod's
  (fixes 11 and 12). The log has one notice for each, `an event with id
  [mem_scfe_ziaskehorn.1] already exists!` and the same for
  `mem_stuck_in_glacier.22`, naming More Events Mod's file. That's the check
  that the patch's copy won: the
  [4.5.2 first run](../reports/2026-10-07-cold-steel-mix-4.5.2-first-run.md#the-patchs-fixes)
  had both. Both events are rare: the Ziaskehorn roll is 1 in 10 on a
  molten or volcanic survey after year 20, and the Iron Fist leader 1 in 4 when the robot is brought
  online. A new save with the `discovered_ziaskehorn` flag should have the
  dig site too.
- A researched Progenitor shield shows an upkeep of energy and alloys in the
  ship designer (fix 15). At load, the log has no `Malformed token` for
  `@shield_*_t7_upkeep_*`: the
  [pre-upload run](../reports/2026-10-07-cold-steel-mix-pre-upload.md#the-patchs-fixes)
  had none.
- A Large Mega Bombard on space fauna fires in combat (fix 16).
- A jump drive fleet can jump into the Surveillance Supercomputer system
  (fix 17). The log has one notice, `An initializer called
  "surveillance_supercomputer_system" already exists`, naming Real Space's
  `special_system_initializers.txt`. That's the check that the patch's copy
  won, as for fixes 11 and 12. The
  [pre-upload run](../reports/2026-10-07-cold-steel-mix-pre-upload.md#the-patchs-fixes)
  had it.
- A lithoid species with Lithoid Budding on a Massive Crater gets the full
  bonus (fix 19). That traits go to the first file by name hasn't been
  checked either.
- A consecrated world can't be terraformed (fix 19).
