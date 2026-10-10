# Documentation map

| File | What it answers |
|---|---|
| [decisions.md](decisions.md) | Every settled decision, one row each, result first |
| [development.md](development.md) | How to run, test and lint, commit and merge, and how the code is laid out |
| [reference/stellaris-files.md](reference/stellaris-files.md) | Where Stellaris, Steam and the launcher keep things, and what's inside |
| [reference/patch-rules.md](reference/patch-rules.md) | How a patch file wins over other mods' files, and lessons from the reports |
| [reference/cold-steel-data.md](reference/cold-steel-data.md) | Cold Steel's data files: which we read and write, and how writes are guarded |
| [reports/](#reports) | Write-ups of real game runs: what went wrong and why |
| [patches/cold-steel-mix.md](patches/cold-steel-mix.md) | The Cold Steel Mix patch: how to build it, and what each fix does |
| [update-check.md](update-check.md) | What to do after a game or mod update: the check, the report, and what it can't tell |
| [game-report.md](game-report.md) | What to do after a game run: reading the error log, tracing entries to mods, and the report |

Don't create a folder until it has something in it.

## Reports

Each report is one real game run: what the error log said, which mod caused
it, and what to do. Name them `YYYY-MM-DD-<playset>-<what>.md`.

| Report | Summary |
|---|---|
| [2026-10-03-cold-steel-mix-errors.md](reports/2026-10-03-cold-steel-mix-errors.md) | From Cold Steel. 11,463 entries; Ariphaos Unofficial Patch (4.2) replaced 220 vanilla files with 4.2 copies and caused half of them |
| [2026-10-03-cold-steel-mix-errors-run-2.md](reports/2026-10-03-cold-steel-mix-errors-run-2.md) | From Cold Steel. Ariphaos removed: 5,674 entries, 153 that matter. Real Space - System Scale ships an old `.asset` copy |
| [2026-10-03-cold-steel-mix-errors-run-3.md](reports/2026-10-03-cold-steel-mix-errors-run-3.md) | The 26-mod build: 121 entries that matter, none blocking. System Scale drops 116 game entities; Cinematic Camera's zoom steps don't match System Scale's planet scales. Ends with what a patch mod could fix |
| [2026-10-03-cold-steel-mix-errors-run-4.md](reports/2026-10-03-cold-steel-mix-errors-run-4.md) | The first run with the Cold Steel Mix patch: 96 entries that matter. Fixes 1–3 and 5–7 work; fix 4's zoom mismatch is still logged (solved in the next report) |
| [2026-10-03-cold-steel-mix-solid-background.md](reports/2026-10-03-cold-steel-mix-solid-background.md) | An hour of play: the background turned one solid colour on entering a system, with nothing logged. Reproduced in Baku. Cause: fix 4's 8 zoom steps left Cinematic Camera's `ENTER_SYSTEM_ZOOM_STEP = 12` past the end. Fix 4 now sets it to 7, confirmed in game |
| [2026-10-04-cold-steel-mix-long-session.md](reports/2026-10-04-cold-steel-mix-long-session.md) | 10.5 hours, 2244 to 2282: the patch's fixes held, and 80 of 95 play entries are the game's own. New: Planetary Diversity's broken text function. The builder didn't skip the patch's Workshop copy (fixed 5 October) |
| [2026-10-05-cold-steel-mix-new-galaxy.md](reports/2026-10-05-cold-steel-mix-new-galaxy.md) | New galaxy, 2200 to 2225, the first run with fix 10: the fixes held, 24 play entries. New: More Events Mod saves the Ziaskehorn planet too late, so its dig site is never made |
| [2026-10-07-cold-steel-mix-4.5.2-update.md](reports/2026-10-07-cold-steel-mix-4.5.2-update.md) | Update check. Only UI Overhaul Dynamic changed, catching up with 4.5.2's fleet view; no fix needed. Cold Steel's build and patch for the playset were empty, and the patch wasn't in the game |
| [2026-10-07-cold-steel-mix-4.5.2-first-run.md](reports/2026-10-07-cold-steel-mix-4.5.2-first-run.md) | First run on 4.5.2, a Sol start played four minutes: the rebuilt patch held, and fixes 11 and 12 win over More Events Mod's events. New: 4.5.2 renamed the shield upkeep variables, so More Events Mod's Progenitor shields have no upkeep. The 4.5–4.5.2 notes, checked against the 24 older mods, show six copies that undo a game fix, among them Ships in Scaling's Large Mega Bombard range |
| [2026-10-07-cold-steel-mix-pre-upload.md](reports/2026-10-07-cold-steel-mix-pre-upload.md) | New galaxy, three years before the Workshop upload: play logged nothing. Fix 15 clears the shield errors and fix 17 wins over Real Space's system; 16 and 19 don't show in the log. New: More Events Mod's Lost Emperor story can fail to place its system and never start |
| [2026-10-09-cold-steel-mix-three-mods-off.md](reports/2026-10-09-cold-steel-mix-three-mods-off.md) | New galaxy, four months, the first run with Starbase Extended, Ascension Worlds and shrimpAI switched off: 47 problems, down from 112, none in play. The patch held, and fix 17's system is unsealed in the save. New: with Ascension Worlds off, Planetary Diversity's own Lithoid Budding splits the Massive Crater bonus again |
| [2026-10-09-cold-steel-mix-une-five-years.md](reports/2026-10-09-cold-steel-mix-une-five-years.md) | New galaxy as the United Nations of Earth, five years: the patch held, fix 21 is in the build, play logged nothing. 67 problems, none new to the mods: the game's Life-Seeded check is back to 21, now explained, and the game's own UNE start logs 4. The Gundersen Research Society defaulted. No new fix |
| [2026-10-09-cold-steel-mix-ascension-worlds-back.md](reports/2026-10-09-cold-steel-mix-ascension-worlds-back.md) | New galaxy as the United Nations of Earth, two years, the first run with Ascension Worlds back on and fix 25 in the build: the patch held, and Ascension Worlds added 51 override notices but no problems. New in play: More Events Mod's Under the Blanket story picked a Fallen Empire's heir, who can't take Substance Abuser. Harmless. The Gundersen entries come from Vela, not Sol. Fix 26 now keeps that story to leaders who can take its traits, and to normal empires |
| [2026-10-10-cold-steel-mix-starbase-extended-back.md](reports/2026-10-10-cold-steel-mix-starbase-extended-back.md) | New galaxy, paused at the start, the first run with Starbase Extended back on and fixes 29–34: the patch held, and every copy it ships is the one the game uses. Starbase Extended's problems fell from 47 to 7: its descriptor, and six parse warnings from its own module file. Fix 30's starbase window works in game. No attach point entries from 21 Starports in 12 cultures. Fix 32 now ships its module and building files whole, which silences them (item 35) |
| [2026-10-10-cold-steel-mix-ten-years.md](reports/2026-10-10-cold-steel-mix-ten-years.md) | New galaxy as a Life-Seeded empire, ten years of play: the patch held, and fix 32's whole files silenced Starbase Extended's six warnings and 17 override notices. Five Starports built in play logged nothing. Play logged 3 entries, all More Events Mod's holo projector text. Six More Events Mod specimen texts can't name their planet in the Grand Archive; item 36 proposes rewording them |
| [2026-10-10-cold-steel-mix-quick-check.md](reports/2026-10-10-cold-steel-mix-quick-check.md) | New galaxy as the Sathyrel, three years, a quick check with fix 36 in the build: the patch held and play logged nothing. Fix 36 wasn't reached, as no specimen was found. More Events Mod's Lost Emperor and ship set entries and the 18 Life-Seeded checks are back, all seen before. No new fix |

The two reports marked "From Cold Steel" were copied from it: "Decision N" in
them means Cold Steel's decisions, not ours.

A game report follows [game-report.md](game-report.md). An update report
follows [update-check.md](update-check.md).

## How we write docs

- **Result first.** Open with what is true or what was decided. Reasons come
  after, and are short.
- **Plain words.** Short sentences. If a term needs explaining, explain it the
  first time or link to where it's explained.
- **One place per fact.** If something is written down in one doc, other docs
  link to it instead of repeating it.
- **Decisions are rows, not documents.** Add a row to
  [decisions.md](decisions.md). If a decision changes, edit the row so it
  always shows the current answer, and note the date it changed.
