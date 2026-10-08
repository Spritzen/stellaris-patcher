# After a game or mod update

**When Stellaris or a playset mod updates, run the update check, read what
it found, write a report and propose fixes. Add no fix until the user
agrees** ([decision 25](decisions.md)). The check only reads. It needs no
game run, and it's safe while the game is open.

```sh
PYTHONPATH=src python3 -m stellaris_patcher check-update --notes   # 1. check
PYTHONPATH=src python3 -m stellaris_patcher check-update --accept  # 8. once reviewed
```

## The steps

1. **Run the check.** `check-update --notes` compares the game and the
   Cold Steel Mix playset's mods with the baseline: their state at the last
   accepted check. It writes a folder in `~/.cache/stellaris-patcher/checks/`
   and prints its summary. In the folder:

   | File | What it holds |
   |---|---|
   | `check.md` | Every finding. Start here |
   | `diffs/` | For each mod copy of a changed game file: `…__game.diff` is what the update changed, `…__<mod>.diff` is the mod's copy against the new game file |
   | `notes/` | Release announcements in full, from the baseline or from the oldest mod's update in "Older mod copies", whichever is earlier |
   | `game-files-changed.txt` | Every changed game text file |

2. **Read `check.md`, top to bottom.**

   | Section | What to do |
   |---|---|
   | Game and mods | What updated. A mod updated after the game may already carry the update. **outdated** means its `supported_version` is older than the game's |
   | The patch's fixes | A fix that's **left out** says why. Usually its cause is gone ([decision 14](decisions.md)). Check the reason, then propose dropping the fix or changing it |
   | Mod copies of changed game files | A mod's copy at the same path replaces the game's whole file. A winning copy that "misses" lines, or is "the game's old file", undoes some of the update. Read both diffs, and match them to the notes |
   | Names the update removed that mods still use | Renamed triggers, effects and variables. The notes' Modding section usually gives the new name |
   | Variables nothing defines | **(new)** marks findings not reviewed at the last accept. Each is a value the game treats as missing |
   | Older mod copies | Objects and whole files a mod's copy wins with, where the game's file changed after the mod's last Steam update. Each new one has a diff against the copy it replaces: the game's, or a newer mod's, like UI Overhaul Dynamic's. A mod's own change and a missing game change look the same, so match each to the notes. Reviewed ones are only counted |
   | Names the patch notes removed that older mods still use | Names from the notes' Modding lines that remove, rename or move something, found in a mod last updated before those notes. Names the game's files still contain are left out. **(new)** marks the ones not reviewed |
   | Cold Steel build | Says whether Cold Steel's build is older than the game or a mod. If so, it must be rebuilt before play |

3. **Read the patch notes** in `notes/`. Read the Modding section first,
   then the bug fixes. Match each line to a finding, or to a file a mod
   replaces. Some notes change what the next error log shows. 4.5.2's
   "Duplicate keys in a database now always log an error" was one.

   Then go through **Older mod copies**, mod by mod. For each diff, look for
   a note that names the change: a fix, a balance change or a new check.
   Only those go in the report. On 7 October this found Ships in Scaling's
   Large Mega Bombard range and Planetary Diversity's trait categories
   ([report](reports/2026-10-07-cold-steel-mix-4.5.2-first-run.md#the-patch-notes-against-older-mods)).

4. **Sort each finding.** Does it break play, change balance or only look
   different? Is it the mod's own to fix, and is that mod likely to update
   soon? Would a fix ship other authors' work? A Workshop copy needs their
   permission for that ([cold-steel-mix.md](patches/cold-steel-mix.md#uploading-it-to-the-workshop)).
   A large copy of a mod its author will likely fix is left to the author
   ([decision 33](decisions.md)). If a mod that changed has a line in the
   patch's [Left to the authors](patches/cold-steel-mix.md#left-to-the-authors)
   list, check whether the update fixed it, and propose dropping the line.

5. **Write a report** in `docs/reports/`, named
   `YYYY-MM-DD-<playset>-<version>-update.md`, and add it to
   [the reports table](README.md#reports). Give the result first, then a
   table of notes against the playset, the mod copies, a numbered "What to
   do next" list, how it was worked out, and its limits.

6. **Propose the fixes and wait for the user.** Once agreed, add them as in
   [cold-steel-mix.md](patches/cold-steel-mix.md), with tests. `make check`
   must pass.

7. **Rebuild, once the user says the game and launcher are closed.** Run
   `cold-steel-mix --write`, then rebuild the playset in Cold Steel. The
   container can't see the game's process, so ask first.

8. **Accept the check.** `check-update --accept` saves the game and every
   mod as they are now, as the next check's baseline. It also marks every
   finding as reviewed: undefined variables, older mod copies and names from
   the notes ([decision 30](decisions.md)). Accept once the report is
   written, and after a mod update too, even if nothing needed doing.

   **The next check doesn't analyse a reviewed finding again.** An older
   copy comes back as new only when its copy, the copy it replaces or the
   game's copy changes. A reviewed copy is counted, with no diff, and its
   notes aren't listed again. So read only what's marked new.

## What the check can't tell

- **Nothing about play.** Things only seen in game need a game run and an
  error-log report, the way the earlier reports were made.
- **Meaning.** 4.5.2 moved trait resources to a new category,
  `planet_pops_traits`. Only the diffs and the notes showed it. Search
  mods for whatever the update replaced.
- **Interface names.** Removed names are only looked for in `common/`. A
  `.gui` copy that lacks a new element, like 4.5.2's `policies_popup_anchor`,
  shows only in its diff.
- **Other languages and binary files.** Snapshots keep English text and
  script files. Other files are compared by size and time only.
- **Without a baseline**, changed game files are guessed from file times,
  and nothing can be compared with the old game.
- **When a release changed an object.** "Older mod copies" goes by file
  times, and a game file's time is when Steam installed it. A mod updated on
  release day, before the game was installed, shows as older. Read its diffs
  against the notes like any other.
- **Steam's notes for a big release are cut short.** 4.5's bug fix, AI and
  interface sections end with "visit the Paradox forums for the full notes",
  and the forum asks for a browser check. A diff in "Older mod copies" that
  no note names may be one of those fixes.

## Gotchas

- **Most mods lag a release.** On 4.5.2, 24 of 26 hadn't updated. An older
  copy undoes a game fix without any error, so it shows only in "Older mod
  copies", not in the log.
- **A mod can catch up the same day.** Stellar AI updated for 4.5.2 hours
  after the game. Look at its newest file and `supported_version` before
  calling a copy old.
- **Go by Steam's update times, not file times.** Steam rewrites a mod's
  files without a new version. The check reads `appworkshop_281990.acf`.
- **A mod's rule may hold in one file and not another.** Ships in Scaling
  divides every range by 6 in one weapons table, and sets many by hand in
  the other. Check every row before relying on a rule.
- **Zipped mods, and mods with no `descriptor.mod`, exist.** The check reads
  inside zips. The patch's fixes can't: [layers.py](../src/stellaris_patcher/patchmod/layers.py)
  sees only loose files.
- **Read the full notes.** A web page summary can stop before the bug fixes
  and the Modding section. Steam's news API, which `--notes` uses, gives the
  whole text.

## Where things are

| What | Where |
|---|---|
| The code | [update/](../src/stellaris_patcher/update/): `check.py` the findings, `older.py` older mod copies and the notes' removed names, `snapshot.py` the baselines, `notes.py` Steam's news and the notes archive. Steam's update times: [workshop.py](../src/stellaris_patcher/paradox/workshop.py) |
| Patch notes | `~/.local/share/stellaris-patcher/notes/`, every announcement `--notes` ever fetched ([decision 29](decisions.md)) |
| Baselines | `~/.local/share/stellaris-patcher/snapshots/`, about 25 MB. The current one and the three before it are kept ([decision 26](decisions.md)) |
| Checks | `~/.cache/stellaris-patcher/checks/<date_time>/`. Safe to delete |
