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
   | `notes/` | Steam's announcements since the baseline, in full |
   | `game-files-changed.txt` | Every changed game text file |

2. **Read `check.md`, top to bottom.**

   | Section | What to do |
   |---|---|
   | Game and mods | What updated. A mod updated after the game may already carry the update. **outdated** means its `supported_version` is older than the game's |
   | The patch's fixes | A fix that's **left out** says why. Usually its cause is gone ([decision 14](decisions.md)). Check the reason, then propose dropping the fix or changing it |
   | Mod copies of changed game files | A mod's copy at the same path replaces the game's whole file. A winning copy that "misses" lines, or is "the game's old file", undoes some of the update. Read both diffs, and match them to the notes |
   | Names the update removed that mods still use | Renamed triggers, effects and variables. The notes' Modding section usually gives the new name |
   | Variables nothing defines | **(new)** marks findings not reviewed at the last accept. Each is a value the game treats as missing |
   | Cold Steel build | Says whether Cold Steel's build is older than the game or a mod. If so, it must be rebuilt before play |

3. **Read the patch notes** in `notes/`. Read the Modding section first,
   then the bug fixes. Match each line to a finding, or to a file a mod
   replaces. Some notes change what the next error log shows. 4.5.2's
   "Duplicate keys in a database now always log an error" was one.

4. **Sort each finding.** Does it break play, change balance or only look
   different? Is it the mod's own to fix, and is that mod likely to update
   soon? Would a fix ship other authors' work? A Workshop copy needs their
   permission for that ([cold-steel-mix.md](patches/cold-steel-mix.md#uploading-it-to-the-workshop)).

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
   mod as they are now, as the next check's baseline. It also marks today's
   undefined variables as reviewed. Accept after a mod update too, even if
   nothing needed doing.

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

## Lessons from earlier checks

From the 4.5.2 check on 6 October:

- **Keep the old game.** Steam leaves no copy of the previous version, so the
  accepted baseline is the only one. Without it, each diff mixes a mod's own
  changes with the update's.
- **A mod can catch up the same day.** Stellar AI updated for 4.5.2 hours
  after the game. Look at its newest file and `supported_version` before
  calling a copy old.
- **A mod's rule may hold in one file and not another.** Ships in Scaling
  divides every range by 6 in one weapons table. In the other it sets many
  ranges by hand. Check every row before relying on a rule.
- **Zipped mods, and mods with no `descriptor.mod`, exist.** The check reads
  inside zips. The patch's fixes can't: [layers.py](../src/stellaris_patcher/patchmod/layers.py)
  sees only loose files.
- **Read the full notes.** A web page summary cut 4.5.2's notes off before
  the bug fixes and the Modding section. Steam's news API, which `--notes`
  uses, gives the whole text.

## Where things are

| What | Where |
|---|---|
| The code | [update/](../src/stellaris_patcher/update/): `check.py` the findings, `snapshot.py` the baselines, `notes.py` Steam's news |
| Baselines | `~/.local/share/stellaris-patcher/snapshots/`, about 25 MB. The current one and the three before it are kept ([decision 26](decisions.md)) |
| Checks | `~/.cache/stellaris-patcher/checks/<date_time>/`. Safe to delete |
