# Cold Steel Mix patch

**A mod named "Cold Steel Mix patch" that fixes 26 problems in the Cold
Steel Mix playset.** [What each fix does](#what-each-fix-does) lists them.
Most were proposed in a [report](../README.md#reports). Problems it leaves to the mods' authors are listed on its
Workshop page ([Left to the authors](#left-to-the-authors)).
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

## Switching a mod off

**No mod is switched off now.** A mod that breaks after a game update can
be switched off in Cold Steel's playset, not removed
([decision 35](../decisions.md)). It keeps its place, so it's one switch
from coming back. Its fixes are left out while it's off. To bring one back:

1. Switch it on in Cold Steel's Cold Steel Mix playset, in the same place.
2. [Build the patch](#build-it). Its fixes come back if the update still
   needs them, and are left out with a reason if not.
3. Play a run and [report on its error log](../game-report.md). For
   Starbase Extended, check its fixes as [Check in game](#check-in-game) lists.
4. At the next upload, add it back to the Workshop page's **Required items**.
   With Starbase Extended, add UI Overhaul Dynamic too: fix 30 ships its
   window, so the build lists it in `dependencies` (`NEEDS` in
   [cold_steel_mix.py](../../src/stellaris_patcher/patchmod/cold_steel_mix.py)).

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
   the mods it patches, and its number to one heading in `FIX_GROUPS`. It
   raises `FixError` when its cause is gone ([decision 14](../decisions.md)).
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
  Paste it into the Workshop page. It lists the fixes under headings, such as
  "Species and traits": `FIX_GROUPS` in
  [cold_steel_mix.py](../../src/stellaris_patcher/patchmod/cold_steel_mix.py).
  A fix in no group is listed last, under "Other".
- The Cold Steel Mix collection's two images are drawn by
  [collection_background.py](../../tools/collection_background.py). The
  background has the patch icon and name on the left, Tron-style lines on the
  right. The branding image, the square one Steam shows in search, has the
  icon and name above the same grid floor, large enough to read at 195 px.
  Render them to `mods/`:

  ```sh
  python3 tools/collection_background.py /tmp/bg.svg
  rsvg-convert -w 1920 -h 1080 /tmp/bg.svg -o ~/.local/share/stellaris-patcher/mods/cold_steel_mix_collection.png
  python3 tools/collection_background.py --square /tmp/brand.svg
  rsvg-convert -w 1024 -h 1024 /tmp/brand.svg -o ~/.local/share/stellaris-patcher/mods/cold_steel_mix_collection_branding.png
  rsvg-convert -w 195 -h 195 /tmp/brand.svg -o ~/.local/share/stellaris-patcher/mods/cold_steel_mix_collection_branding_195.png
  ```

- Upload it from the Paradox launcher. The launcher saves the Workshop id in
  the `.mod` file, and later builds keep it, so the next upload updates the
  same Workshop item.
- On the Workshop page, add the same mods as **Required items**. Steam doesn't
  read `dependencies`. Remove any it no longer lists. At the next upload,
  add Planetary Diversity - More Arcologies, which fix 25 patches, Smarter
  Hyper Relays: Improved AI (shrimpAI), back on with fix 28, and UI Overhaul
  Dynamic, whose window fix 30 ships. Keep Starbase Extended 3.0, back on with
  fixes 29–34, and Planetary Diversity - Ascension Worlds.

### Left to the authors

**The list is empty, so the description has no known issues section.**
When it has lines, the description lists the playset's known problems that
the patch doesn't fix, under "Known issues, waiting for the mod authors"
([decision 33](../decisions.md)). They're in `LEFT_TO_AUTHORS` in
[cold_steel_mix.py](../../src/stellaris_patcher/patchmod/cold_steel_mix.py),
written by hand, one line per problem.

- Add a line when a report leaves a problem to a mod's author.
- Drop it once the mod fixes it. The [update check](../update-check.md) shows
  when one of these mods changes.
- Not listed, as too small to matter
  ([decision 41](../decisions.md)): More Events Mod's Lost Emperor story
  sometimes can't place its system
  ([pre-upload report](../reports/2026-10-07-cold-steel-mix-pre-upload.md#what-to-do-next),
  item 20), and Dark UI has no dark versions of 4.5.2's new icons.

**Ask the other authors first.** The patch ships work that isn't ours:

| File | Whose work |
|---|---|
| `common/ship_sizes/nsc_starbases.txt` | Starbase Extended 3.0's whole file, with two lines added |
| `common/solar_system_initializers/stellaris_patcher_cold_steel_mix_sol_neighbors.txt` | Three of Real Space 4.0's systems, copied |
| The three `.asset` files | The game's files, with Real Space - System Scale's sizes |
| `events/!!_stellaris_patcher_cold_steel_mix_ziaskehorn.txt` | One of More Events Mod's events, with two lines moved |
| `events/!!_stellaris_patcher_cold_steel_mix_stuck_in_glacier.txt` | One of More Events Mod's events, with one word changed |
| `localisation/replace/stellaris_patcher_cold_steel_mix_l_english.yml` | Three of Planetary Diversity's and Ascension Worlds' necro world tooltips, with one call changed in each |
| `common/component_templates/mutation_weapon_components.csv` | Real Space - Ships in Scaling's whole file, with one range changed |
| `common/solar_system_initializers/!!_stellaris_patcher_cold_steel_mix_supercomputer.txt` | One of Real Space 4.0's systems, with one flag removed |
| `common/traits/!!_stellaris_patcher_cold_steel_mix_lithoid_budding.txt` | Lithoid Budding from Ascension Worlds, or from Planetary Diversity while Ascension Worlds is off, with one line added |
| `common/game_rules/zz_stellaris_patcher_cold_steel_mix_terraform.txt` | Ascension Worlds' terraforming rule, with two of the game's checks added |
| Seven `localisation/<language>/planetarydiversity_…` files | Planetary Diversity's whole files, with broken lines mended |
| Ten `localisation/<language>/planetarydiversity_aw_…` files | Planetary Diversity - Ascension Worlds' whole files, with one line mended in each |
| Two `localisation/<language>/planetarydiversity_more_arcologies_…` files | Planetary Diversity - More Arcologies' whole files, with one line mended in each |
| `events/!!_stellaris_patcher_cold_steel_mix_under_blanket.txt` | Two of More Events Mod's events, with 15 lines added |
| `common/traits/!!_stellaris_patcher_cold_steel_mix_trait_categories.txt` | 15 traits from Planetary Diversity, Ascension Worlds and More Events Mod, with one word changed in each |
| `common/traits/!!_stellaris_patcher_cold_steel_mix_aquatic.txt` | Planetary Diversity's Aquatic trait, with the game's AI weight |
| `common/megastructures/zzzz_stellaris_patcher_cold_steel_mix_hyper_relay.txt` | shrimpAI's Hyper Relay, with the game's waystation clause added |
| `common/starbase_modules/zz_stellaris_patcher_cold_steel_mix_sbx_buildings.txt` | Three of Starbase Extended 3.0's modules, with one building name changed in each check |
| `interface/zzzz_stellaris_patcher_cold_steel_mix_starbase_view.gui` | UI Overhaul Dynamic's starbase window and slot, with Starbase Extended's slot sizes and nine header values changed |
| 19 `gfx/models/ships/starbases/_starbase_entities_SBX_3_0_…` files | Starbase Extended 3.0's whole files, rebuilt: its copies of the game's models are the game's, with its attach points added |
| `gfx/models/ships/starbases/zz_stellaris_patcher_cold_steel_mix_attach_points.asset` | 50 of the game's models, with attach points added |
| `common/starbase_modules/sbx_3_0_orbital_ring_modules.txt`, `common/starbase_modules/sbx_3_0_starbase_modules.txt` and `common/starbase_buildings/sbx_3_0_starbase_buildings.txt` | Starbase Extended 3.0's whole files, with 7 modules' and 10 buildings' checks mended, and the game's 4.5 hangar lines in its hangar bay |
| `common/section_templates/!!!!_stellaris_patcher_cold_steel_mix_ring_sections.txt` | Starbase Extended 3.0's ring anchorage section, twice, under two new keys |
| `common/ship_sizes/zzzz_stellaris_patcher_cold_steel_mix_starbase_sizes.txt` | 21 of Starbase Extended 3.0's starbase sizes, with the game's 4.5 values for eight fields |
| `localisation/english/replace/stellaris_patcher_cold_steel_mix_specimens_l_english.yml` | Six of More Events Mod's specimen descriptions, with a planet's name swapped for a few words in each |

The game's own files are fine to ship in a mod. The others need their
authors' permission, or fixes 3, 5, 10–12, 16–19, 25–34 and 36 left out.

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
| 18 | Planetary Diversity's, Ascension Worlds' and More Events Mod's traits file their resources under `planet_pops`, which 4.5.2 keeps for a species' archetype. An `_add` modifier on `planet_pops` applies once per resource table, so Unemployment Benefits and the Shroud-Warped leader's psionic unity count once per trait | A copy of each trait in use with `category = planet_pops`, in one `!!_` file, with the game's `planet_pops_traits` instead. 15 today: 7 from Planetary Diversity (among them Organic, Lithoid, Mechanical and Machine Unit), 5 from Ascension Worlds and 3 from More Events Mod. A trait fix 19 or 27 copies is left to it ([decision 43](../decisions.md)) |
| 19 | Planetary Diversity's and Ascension Worlds' Lithoid Budding lack 4.5.2's `divide_over_pop_groups = no` on the Massive Crater bonus. Ascension Worlds' terraforming rule lacks the game's checks for a consecrated world and a Knights detox in progress | A copy of the trait in use, with the game's line added, in a `!!_` file. Both mods ship a whole `04_species_traits.txt`, and Ascension Worlds' replaces Planetary Diversity's, so the copy is from whichever is on ([decision 37](../decisions.md)). Only Ascension Worlds has the rule: a copy of it, with the two checks added, in a `zz_` file: game rules go to the last file by name. The legendary leader check Ascension Worlds comments out on purpose stays out ([decision 32](../decisions.md)) |
| 25 | Lines in Planetary Diversity's, Ascension Worlds' and More Arcologies' translations the game can't read: quotes missing (German, Russian, Polish), text with no key (German, and Ascension Worlds' flooded world tooltip in all nine translations), and German obsidian world text pasted in after its own key (also Japanese, Korean and Russian, which read but show the key) | Each broken file whole, at its own path, with the lines mended. The keyless line takes the key the mod's English file has in its place ([decision 39](../decisions.md)). A file whose line no rule mends is skipped |
| 26 | More Events Mod's Under the Blanket story picks its scientist with no check that the game lets them take a normal trait, so an autocracy's ruler or heir loses the trait its ending gives: Substance Abuser, Archaeologist or Adaptable. It also starts for Fallen Empires, on the worlds they own from the start | Copies of `mem_under_blanket.1` and `.2`, in an `events/` file whose name starts `!!_`. Each of `.2`'s 14 scientist picks gets the game's `can_leader_get_normal_trait_trigger`, the trigger its rule calls. `.1` starts only for `is_country_type = default`, as the game's Strange Worlds colony events do ([decision 40](../decisions.md)) |
| 27 | Planetary Diversity's copy of the Aquatic trait predates 4.5.2, so the AI doesn't value it for species with Wet Climate Mods (`trait_cyborg_climate_adjustment_wet`), as the game's AI now does | A copy of Planetary Diversity's trait, in a `!!_` file, with the game's `ai_weight` in place of its own. Planetary Diversity's planet classes and checks stay. Only while its weight differs from the game's by that trait alone ([decision 42](../decisions.md)) |
| 28 | Smarter Hyper Relays (shrimpAI) replaces the game's Hyper Relay with a copy from before 4.5.2. Its surveyed-system check lacks the game's clause for a system with your own waystation, so a Nomadic empire can't build one at its waystation until it has surveyed every planet there | A copy of shrimpAI's Hyper Relay, in a `zzzz_` file: megastructures go to the last file by name. Each custom tooltip in its `possible` gets the game's clauses it lacks, matched by fail text. Today that's the one waystation clause. shrimpAI's own changes, such as its wild space clauses and its AI weight, stay ([decision 45](../decisions.md)) |
| 29 | Starbase Extended 3.0's Asteroid Mining checks for a `mining_manager` building, and its Space Foundry and Space Factory for `assembly_line_manufacturing`. Nothing defines either, so their bonuses never apply, and the game logs 5 errors each run | Copies of the three modules, in a `zz_` file: starbase modules go to the last file by name. Each check names Starbase Extended's own building of that kind: Mining Experts, which needs Asteroid Mining, and Chain Manufacturing, which boosts alloys and consumer goods ([decision 46](../decisions.md)). A name that's defined later is left alone |
| 30 | Starbase Extended 3.0's starbase window, from July, replaces UI Overhaul Dynamic's 4.5 copy. It lacks the Orbital Ring → planet button (`open_planet`), the design name, the window's title and two lists' scrollbars, and the game logs 2 errors each run | Starbase Extended's `interface/zzz_sbx_3_0_starbase_view.gui`, emptied, so UI Overhaul Dynamic's windows are used again. Then a copy of UI Overhaul Dynamic's `starbase_view` window and its slot, in a `zzzz_` file that sorts after every file defining them. The slots take Starbase Extended's sizes: 34 px, 7 to a row, icons at 0.6, so all 21 module and building slots fit. Upgrade and Station Details swap places as in Starbase Extended, so Upgrade isn't just above Dismantle. Only while Starbase Extended's window lacks some of UI Overhaul Dynamic's elements. The swap is skipped if UI Overhaul Dynamic's header changes ([decision 47](../decisions.md)) |
| 31 | Starbase Extended 3.0's starbase models are old copies of the game's. 180 of its 397 copies differ from 4.5's, and they win, so starbases lose 79 death explosions, 65 lights and 16 aquatic water surfaces. Its own lines ask for 8 hum sounds, 3 particle effects and 3 `.anim` files nothing defines, and an idle animation 7 synthetic meshes lack. Its larger sizes ask for attach points `part4`–`part7` that many meshes lack. About 30 log entries each run | Its 19 model files, rebuilt at their own paths. A model it copies is the game's 4.5 one, with Starbase Extended's own additions: its gun-slot attach points, and effects and sounds the game's model has none of. Where both have one, on the same node or in the same state, Starbase Extended's is the game's older one, so the game's stays. Its new Stronghold and HQ models on a Citadel's mesh are built on the game's Citadel. A sound, particle or animation nothing defines is left out. Each starbase model gets the attach points its size asks for and its mesh lacks, at its centre, as Starbase Extended places its gun slots. 50 game models need them too, in a `zz_` file that sorts last ([decision 48](../decisions.md)) |
| 32 | Six of Starbase Extended 3.0's modules have two `potential` blocks, and its orbital ring hangar bay two `ai_weight` blocks: the game keeps one, so conditions are lost (6 errors). `financial_space_center`'s `potential` has `category = starbase_buildings`, which isn't a trigger (2). Ten buildings' `potential` scopes to the starbase's system, which an arkship's starbase lacks (3 in play). Its hangar bay predates 4.5: no hangars, energy upkeep for bio-ship empires | Starbase Extended's two module files and its buildings file, whole at their own paths, so the game never reads the duplicate blocks. Each object's checks are mended: the blocks merged into one, the `category` line taken out, `exists = solar_system` first. The hangar bay gets the game's two hangar sets, its tooltips, and its two upkeeps, food for bio-ship empires, in place of Starbase Extended's one, which is the game's for other empires. Its own cost, limit and platforms stay. A module fix 29 copies is left to it ([decision 49](../decisions.md)) |
| 33 | Starbase Extended 3.0's orbital ring shield and armour modules name sections nothing defines, so they have no section (2 errors) | `SHIELD_ORBITAL_RING_SECTION` and `ARMOR_ORBITAL_RING_SECTION`, as copies of its ring anchorage section, as its starbase shield and armour modules use its anchorage. Each only while a module uses it and nothing defines it ([decision 50](../decisions.md)) |
| 34 | Starbase Extended 3.0's 19 copies of the game's starbase sizes predate 4.5: their size and combat size are the old values, they have no map icon, the orbital rings lack `is_orbital_ring`, and the Ion Cannon can be built at a waystation or arkship | Copies of its sizes in a `zzzz_` file, with the game's 4.5 values for eight fields, and the game's construction conditions they lack. Its own hit points, armour, costs and slots stay. Its Stronghold and HQ take the Citadel's values. A variable its file uses but doesn't define takes the one value the other ship size files give it, as fix 3 does ([decision 51](../decisions.md)) |
| 36 | Six of More Events Mod's specimen descriptions name a planet with `[From.From.GetName]` (`[From.From.From.GetName]` for the datacore). A specimen keeps only its event's scope, the science ship, so the name is blank in the Grand Archive and logs `Unknown promotion From` | A `localisation/english/replace/` file with the six lines, each the winning text with the name swapped for a few words: "a lifeless planetoid", "a world of long-dead civilizations", "alien ruins", "an ancient satellite", "a living asteroid", "a disguised planet". A line More Events Mod has reworded is skipped ([decision 52](../decisions.md)) |

### Notes

- **Fix 2 gets back three guns, not four.** Starbase Extended's slots stop
  at `_12`, not `_20` as the third run's report says.
- **Fix 5 matches stars by name.** The game's `sol_neighbor_t2` is Procyon,
  so it becomes Real Space's `procyon_mediumsector`, not Sirius. Before
  copying, the fix checks that both systems have the same `name`.
- A fix that ships a whole file only does so while that file still comes
  from the expected mod or the game. Otherwise it could undo another mod's
  newer copy. Fixes 11 and 12 do the same for one event: More Events Mod's
  copy must be the one the game uses.
- **Fixes 11, 12 and 26 copy whole events**, and the game then has two
  events with one id. More Events Mod's copy is still loaded, but never
  used. Fixes 17, 18, 19, 27 and 28 do the same for a system, traits, a
  rule and a megastructure.
- **Fix 15 doesn't name More Events Mod.** It defines every old shield upkeep
  name any component uses and nothing defines.
- **Fix 18 copies 15 traits, not 18.** Three of More Events Mod's six are
  commented out ([decision 43](../decisions.md)).

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
- More Events Mod's Under the Blanket story gives its scientist the trait its
  ending names, even in an autocracy, and a Fallen Empire never starts it
  (fix 26). The log has no `rules_leader_cannot_get_normal_trait` for
  `mem_under_blanket.txt`, and two duplicate event notices name More Events
  Mod's file, for `mem_under_blanket.1` and `.2`, as for fixes 11 and 12.
- In a Megacorp with Unemployment Benefits, an unemployed pop's upkeep is 2
  consumer goods, not 2 per species trait (fix 18). As for fix 19, the log
  can't show which copy of a trait won.
- An AI cyborg species with Wet Climate Mods can gain Aquatic when it
  modifies its genes (fix 27). It's rare, and only AI empires' choices
  change. As for fix 19, the log has no notice for a copied trait, so it
  can't show which copy won.
- A Nomadic empire can build a Hyper Relay in a system where it has its own
  waystation and some planets aren't surveyed (fix 28). A system it has
  surveyed already worked without the fix.
- A citadel's starbase window shows all 21 module slots and 21 building
  slots, Upgrade sits bottom-left with the next level's name, and Station
  Details top-right (fix 30). **Seen** on a Starport in the
  [Starbase Extended back](../reports/2026-10-10-cold-steel-mix-starbase-extended-back.md)
  run: every slot showed and nothing looked wrong. Still to see on a
  Citadel. An Orbital Ring's window has the button back to its planet, and the log has no `open_planet` or `design_name`. Watch a
  slot under construction: Starbase Extended's progress bar keeps its full
  size in the smaller slot, so it may hang into the row below.
- A destroyed starbase explodes, aquatic and toxoid starbases hum with the
  game's sounds, and toxoid starbases' lights glow (fix 31). The log has no
  `amb_aquatic_starbase_hum`, `amb_toxoid_starbase_hum`, `toxoid_01_ship_light_effect`,
  `does not have an animated mesh`, `fallen_empire_0…_citadel_idle.anim` or
  `has no attach point named part…`. Sections on the added attach points sit
  at the starbase's centre, so look at a humanoid Starport for any that
  stick out oddly.
- A bio-ship empire's orbital ring hangar bay costs food, and its tooltip
  lists the scout hangar (fix 32). An arkship's starbase lists its
  buildings, and the log has no `solar_system` error from
  `sbx_3_0_starbase_buildings.txt`, and no `Duplicate trigger` (fix 32). The
  log half was **seen** in the
  [ten years](../reports/2026-10-10-cold-steel-mix-ten-years.md) run.
- An orbital ring's shield or armour module shows a section, and the log has
  no `SHIELD_ORBITAL_RING_SECTION` (fix 33).
- Starbases have their map counter icons, and the Ion Cannon can't be built
  at a waystation (fix 34).
- A More Events Mod specimen in the Grand Archive, such as the Hologenerator
  Unit, says where it was found, with no blank (fix 36). The log has no
  `Unknown promotion From` for `From.From.GetName]`.
