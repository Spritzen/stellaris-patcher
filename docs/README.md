# Documentation map

| File | What it answers |
|---|---|
| [decisions.md](decisions.md) | Every settled decision, one row each, result first |
| [adapting.md](adapting.md) | Adapting the tool to another playset, how a build works, and how to write a fix |
| [development.md](development.md) | How to run, test and lint, commit and merge, and how the code is laid out |
| [reference/stellaris-files.md](reference/stellaris-files.md) | Where Stellaris, Steam and the launcher keep things, and what's inside |
| [reference/patch-rules.md](reference/patch-rules.md) | How a patch file wins over other mods' files, and lessons from the reports |
| [reference/cold-steel-data.md](reference/cold-steel-data.md) | Cold Steel's data files: which we read and write, and how writes are guarded |
| [reports/](#reports) | Write-ups of real game runs: what went wrong and why |
| [patches/cold-steel-mix.md](patches/cold-steel-mix.md) | The Cold Steel Mix patch: how to build it, and what each fix does |
| [update-check.md](update-check.md) | What to do after a game or mod update: the check, the report, and what it can't tell |
| [game-report.md](game-report.md) | What to do after a game run: reading the error log, tracing entries to mods, and the report |
| [patch-notes.md](patch-notes.md) | Writing the Workshop patch notes for an upload, and recording it |
| [doc-pass.md](doc-pass.md) | Checking every doc and code comment for stale entries, inconsistencies and history to cut |
| [patches/cold-steel-mix-patch-notes.md](patches/cold-steel-mix-patch-notes.md) | Every Workshop upload of the Cold Steel Mix patch, with its notes and commit |

Don't create a folder until it has something in it.

## Reports

Each report is one real game run: what the error log said, which mod caused
it, and what to do. File them under `reports/<playset>/YYYY-MM/`, named
`YYYY-MM-DD-<what>.md`.

### Cold Steel Mix

#### 2026-10

| Report | Summary |
|---|---|
| [2026-10-03-errors.md](reports/cold-steel-mix/2026-10/2026-10-03-errors.md) | From Cold Steel. 11,463 entries; Ariphaos Unofficial Patch (4.2) replaced 220 vanilla files with 4.2 copies and caused half of them |
| [2026-10-03-errors-run-2.md](reports/cold-steel-mix/2026-10/2026-10-03-errors-run-2.md) | From Cold Steel. Ariphaos removed: 5,674 entries, 153 that matter. Real Space - System Scale ships an old `.asset` copy |
| [2026-10-03-errors-run-3.md](reports/cold-steel-mix/2026-10/2026-10-03-errors-run-3.md) | The 26-mod build: 121 entries that matter, none blocking. System Scale drops 116 game entities; Cinematic Camera's zoom steps don't match System Scale's planet scales. Ends with what a patch mod could fix |
| [2026-10-03-errors-run-4.md](reports/cold-steel-mix/2026-10/2026-10-03-errors-run-4.md) | The first run with the Cold Steel Mix patch: 96 entries that matter. Fixes 1–3 and 5–7 work; fix 4's zoom mismatch is still logged (solved in the next report) |
| [2026-10-03-solid-background.md](reports/cold-steel-mix/2026-10/2026-10-03-solid-background.md) | An hour of play: the background turned one solid colour on entering a system, with nothing logged. Reproduced in Baku. Cause: fix 4's 8 zoom steps left Cinematic Camera's `ENTER_SYSTEM_ZOOM_STEP = 12` past the end. Fix 4 now sets it to 7, confirmed in game |
| [2026-10-04-long-session.md](reports/cold-steel-mix/2026-10/2026-10-04-long-session.md) | 10.5 hours, 2244 to 2282: the patch's fixes held, and 80 of 95 play entries are the game's own. New: Planetary Diversity's broken text function. The builder didn't skip the patch's Workshop copy (fixed 5 October) |
| [2026-10-05-new-galaxy.md](reports/cold-steel-mix/2026-10/2026-10-05-new-galaxy.md) | New galaxy, 2200 to 2225, the first run with fix 10: the fixes held, 24 play entries. New: More Events Mod saves the Ziaskehorn planet too late, so its dig site is never made |
| [2026-10-07-4.5.2-update.md](reports/cold-steel-mix/2026-10/2026-10-07-4.5.2-update.md) | Update check. Only UI Overhaul Dynamic changed, catching up with 4.5.2's fleet view; no fix needed. Cold Steel's build and patch for the playset were empty, and the patch wasn't in the game |
| [2026-10-07-4.5.2-first-run.md](reports/cold-steel-mix/2026-10/2026-10-07-4.5.2-first-run.md) | First run on 4.5.2, a Sol start played four minutes: the rebuilt patch held, and fixes 11 and 12 win over More Events Mod's events. New: 4.5.2 renamed the shield upkeep variables, so More Events Mod's Progenitor shields have no upkeep. The 4.5–4.5.2 notes, checked against the 24 older mods, show six copies that undo a game fix, among them Ships in Scaling's Large Mega Bombard range |
| [2026-10-07-pre-upload.md](reports/cold-steel-mix/2026-10/2026-10-07-pre-upload.md) | New galaxy, three years before the Workshop upload: play logged nothing. Fix 15 clears the shield errors and fix 17 wins over Real Space's system; 16 and 19 don't show in the log. New: More Events Mod's Lost Emperor story can fail to place its system and never start |
| [2026-10-09-three-mods-off.md](reports/cold-steel-mix/2026-10/2026-10-09-three-mods-off.md) | New galaxy, four months, the first run with Starbase Extended, Ascension Worlds and shrimpAI switched off: 47 problems, down from 112, none in play. The patch held, and fix 17's system is unsealed in the save. New: with Ascension Worlds off, Planetary Diversity's own Lithoid Budding splits the Massive Crater bonus again |
| [2026-10-09-une-five-years.md](reports/cold-steel-mix/2026-10/2026-10-09-une-five-years.md) | New galaxy as the United Nations of Earth, five years: the patch held, fix 21 is in the build, play logged nothing. 67 problems, none new to the mods: the game's Life-Seeded check is back to 21, now explained, and the game's own UNE start logs 4. The Gundersen Research Society defaulted. No new fix |
| [2026-10-09-ascension-worlds-back.md](reports/cold-steel-mix/2026-10/2026-10-09-ascension-worlds-back.md) | New galaxy as the United Nations of Earth, two years, the first run with Ascension Worlds back on and fix 25 in the build: the patch held, and Ascension Worlds added 51 override notices but no problems. New in play: More Events Mod's Under the Blanket story picked a Fallen Empire's heir, who can't take Substance Abuser. Harmless. The Gundersen entries come from Vela, not Sol. Fix 26 now keeps that story to leaders who can take its traits, and to normal empires |
| [2026-10-10-starbase-extended-back.md](reports/cold-steel-mix/2026-10/2026-10-10-starbase-extended-back.md) | New galaxy, paused at the start, the first run with Starbase Extended back on and fixes 29–34: the patch held, and every copy it ships is the one the game uses. Starbase Extended's problems fell from 47 to 7: its descriptor, and six parse warnings from its own module file. Fix 30's starbase window works in game. No attach point entries from 21 Starports in 12 cultures. Fix 32 now ships its module and building files whole, which silences them (item 35) |
| [2026-10-10-ten-years.md](reports/cold-steel-mix/2026-10/2026-10-10-ten-years.md) | New galaxy as a Life-Seeded empire, ten years of play: the patch held, and fix 32's whole files silenced Starbase Extended's six warnings and 17 override notices. Five Starports built in play logged nothing. Play logged 3 entries, all More Events Mod's holo projector text. Six More Events Mod specimen texts can't name their planet in the Grand Archive; item 36 proposes rewording them |
| [2026-10-10-quick-check.md](reports/cold-steel-mix/2026-10/2026-10-10-quick-check.md) | New galaxy as the Sathyrel, three years, a quick check with fix 36 in the build: the patch held and play logged nothing. Fix 36 wasn't reached, as no specimen was found. More Events Mod's Lost Emperor and ship set entries and the 18 Life-Seeded checks are back, all seen before. No new fix |
| [2026-10-10-seventeen-years.md](reports/cold-steel-mix/2026-10/2026-10-10-seventeen-years.md) | New galaxy as a Life-Seeded empire, seventeen years, the first run with Stellar AI's 10 October update: the patch held, and play logged 3 entries, all the game's own. Stellar AI's new files add 4 override notices, with no clash. Its older copy of the Archaeostudies Faculty beats More Arcologies' and drops its Archeotech Preserve bonuses; fix 37 now ships a merged copy. No AI empire defaulted |
| [2026-10-10-4.5.2-update.md](reports/cold-steel-mix/2026-10/2026-10-10-4.5.2-update.md) | Update check. The game didn't change. The 26 new findings come from Starbase Extended and shrimpAI being back on, and each is already fixed (fixes 3, 28, 30, 32) or is the mod's own design. No new fix. The Cold Steel build predated fix 37, now rebuilt. The check's build line now looks at the patch too |
| [2026-10-11-thirty-two-years.md](reports/cold-steel-mix/2026-10/2026-10-11-thirty-two-years.md) | The seventeen years save continued to 2232, the first run with fix 37: the patch held, and fix 37's faculty wins in an existing save. Play logged 32 entries: 23 from one More Events Mod dig site the AI stopped digging, all harmless. New: More Events Mod's Ancestors' Grudge gave a hive mind's official no relic trait, the same mistake as fix 26's; fix 38 now mends it the same way. The check's build line counted the patch's descriptor, which the build leaves out; it now skips it |
| [2026-10-11-forty-three-years.md](reports/cold-steel-mix/2026-10/2026-10-11-forty-three-years.md) | The same save continued to 2243, the first run with fix 38: the patch held, fix 38 wasn't reached, and the galaxy's first five Starholds logged nothing. Play logged 13 entries, none worth a fix. New: More Events Mod's Astral Tales offers an autocracy's ruler a trait the game refuses, which only makes its tooltip wrong; fix 40 now mends it at the user's request |
| [2026-10-11-sixty-years.md](reports/cold-steel-mix/2026-10/2026-10-11-sixty-years.md) | The same save continued to 2260, the first run with fix 40: the patch held, and fix 40 wins but can't be reached, as Astral Tales has run in this galaxy. The galaxy's first 3 Hyper Relays and 17 more Starholds logged nothing. Play logged 39 entries, 38 of them the game's own. Three AI defaults, two by one vassal taxed under the game's own terms. No new fix |
| [2026-10-13-4.5.2-update.md](reports/cold-steel-mix/2026-10/2026-10-13-4.5.2-update.md) | Update check. Only Stellar AI changed, to 0.12, adding an AI-only exotic gas guard to 37 buildings. Planetary Diversity's four Gaia Seeders win and drop it; fix 41 now ships a merged copy. Fix 37 is unchanged, and the patch's output too. The Cold Steel build predates Stellar AI's update |
| [2026-10-13-five-years-stellar-ai.md](reports/cold-steel-mix/2026-10/2026-10-13-five-years-stellar-ai.md) | New galaxy as the United Nations of Earth, five years, the first run with Stellar AI 0.12 and fix 41: the patch held, and fix 41's Gaia Seeders win but no Idyllic Bloom empire was there to reach them. Play logged 1 entry, the game's timeline text. Stellar AI 0.12 adds 10 override notices, as expected. One AI empire defaulted on food in 2201, the earliest yet. No new fix |
| [2026-10-18-4.5.2-update.md](reports/cold-steel-mix/2026-10/2026-10-18-4.5.2-update.md) | Update check. Only Stellar AI changed, to 0.14: its AI goes by the economy, not the calendar, its crisis check reads income, its idle army reserve is gone and its war-goal gate is softer. Nothing clashes, and the patch's output is unchanged. No fix. The Cold Steel build predates Stellar AI's update |

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
