# After a game run

**After the user plays the playset, read the error log, trace each entry to
its mod, write a report and propose fixes. Add no fix until the user agrees**
([decision 25](decisions.md)). Reading is safe while the game is open.

## The steps

1. **Ask what happened in game.** How long, which galaxy, a new game or a
   save, and anything that looked wrong. Visual problems, like the
   [solid background](reports/2026-10-03-cold-steel-mix-solid-background.md),
   don't reach the logs.

2. **Read the log** with
   [error_log.py](../src/stellaris_patcher/paradox/error_log.py). It's
   `Stellaris/logs/error.log` in `$PARADOX_DATA_DIR`
   ([stellaris-files.md](reference/stellaris-files.md)). Older runs are kept
   as `error.log.<date>`.

   ```sh
   PYTHONPATH=src python3 -c 'import os; from pathlib import Path; from stellaris_patcher.paradox.error_log import read_error_log; print(len(read_error_log(Path(os.environ["PARADOX_DATA_DIR"], "Stellaris"))))'
   ```

3. **Split the entries by time**: loading, the empire designer, game start,
   and play. `game.log` gives the time the galaxy was made. Play entries
   matter most.

4. **Trace each entry to its mod.** Look up the file it names in Cold Steel's
   build record ([cold-steel-data.md](reference/cold-steel-data.md#the-files)),
   and read the code at that line. Entries with no file go to the mod their
   text or asset belongs to. Compare with the game's own copy before calling
   one the game's.

5. **Check the patch.** The build record lists it last. Its files match our
   source folder byte for byte. The raw log has none of the names the fixes
   removed ([cold-steel-mix.md](patches/cold-steel-mix.md#what-each-fix-does)).

6. **Check the save, if a finding needs it.** Unpack the save into a scratch
   folder and read it with [script.py](../src/stellaris_patcher/paradox/script.py).

7. **Write a report** in `docs/reports/`, named
   `YYYY-MM-DD-<playset>-<what>.md`, and add it to
   [the reports table](README.md#reports). Give the result first, then the
   run, a comparison with earlier runs, the patch's fixes, the entries by
   mod, a numbered "What to do next" table, how it was worked out, and its
   limits. The [new-galaxy report](reports/2026-10-05-cold-steel-mix-new-galaxy.md)
   is a good model.

8. **Propose the fixes and wait for the user.** Once agreed, add them as in
   [cold-steel-mix.md](patches/cold-steel-mix.md#add-a-fix).

   If the report read the update check's findings, as the
   [first 4.5.2 run](reports/2026-10-07-cold-steel-mix-4.5.2-first-run.md)
   did, run `check-update --accept` afterwards. The next check then skips
   what was read ([decision 30](decisions.md)).

Reports before 6 October ran Cold Steel's own error reader. Its source is no
longer mounted ([decision 27](decisions.md)), so use ours.
