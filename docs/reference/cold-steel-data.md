# Cold Steel's data files

**Cold Steel is the mod manager that holds the user's playsets. We read its
data files and write our results back into them** ([decision 11](../decisions.md)).
Cold Steel then builds the playset, makes its own patch mod from the conflict
choices, and syncs the launcher. We share only its data, never its code
([decision 27](../decisions.md)).

[coldsteel/files.py](../../src/stellaris_patcher/coldsteel/files.py) reads and
writes these files, using the records in
[coldsteel/records.py](../../src/stellaris_patcher/coldsteel/records.py).

## The files

| File | We | What's in it |
|---|---|---|
| `~/.local/share/cold-steel/playsets.json` | read, write | Every playset: its mods in load order (`workshop:<id>` or `local:<file>.mod`), disabled DLC, pinned copies. `active` is the one Play uses |
| `~/.local/share/cold-steel/resolutions/<playset id>.json` | read, write | The playset's conflict choices, ignore rules, and `built`: which choices the patch mod was made from |
| `~/.local/share/cold-steel/patches/<playset id>/` | read | The patch mod Cold Steel made from those choices. Linked into the game as `mod/cold_steel_patch_<playset id>`. It must stay last in the playset |
| `~/.local/share/cold-steel/builds/<playset id>.json` | read | A build's record: which mod each file in the built playset came from. Use it to trace an `error.log` entry to its mod |
| `~/.config/cold-steel/settings.json` | read | A Steam folder or game data folder set by hand |

The user plays the **built** playset, a single mod named
`Cold Steel build: <playset>`. A change to a playset, or a new patch mod
build, reaches the game only after the user rebuilds it in Cold Steel.

## Every write is guarded

`save_playsets` and `save_resolutions` refuse ([decision 12](../decisions.md)):

- **while Cold Steel is open.** It loads its files when it starts and saves
  over them, which would undo our change. It's found by its command line
  (`python3 -m cold_steel`, or the installed `cold-steel`). In the container
  host processes can't be seen, so ask the user to close Cold Steel, then
  pass `cold_steel_closed=True`.
- **a file with fields our records don't have**, or another `version`.
  msgspec drops fields it doesn't know, so writing a newer Cold Steel's file
  would lose its data. Add the new fields to `records.py` first.
  `test_records_read_cold_steels_real_files` reads the real files and fails
  when they drift ([decision 13](../decisions.md)).

Before writing, the old file is backed up into
`~/.local/share/stellaris-patcher/backups/cold-steel/`, newest 20 per file.
`post-create.sh` also keeps one copy from before we first wrote anything.

## Writing a conflict choice

Cold Steel compares `built` with the choices. Leave `built` alone: Cold
Steel's Conflicts window then says the choices changed, and the user presses
**Generate patch mod**.

Each choice's `seen` lists every version of the object when it was chosen.
Cold Steel leaves a choice out of its patch when any digest no longer
matches, so the digests must be worked out exactly its way:

- an object: `Definition.digest` from
  [definitions.py](../../src/stellaris_patcher/core/definitions.py). Don't
  change how it hashes;
- a whole file that's read: `xxh3_64_intdigest` of its bytes;
- a picture or sound: `xxh3_64_intdigest` of the msgpack of `(size, mtime_ns)`;
- a version that's gone: `0`.

A wrong digest fails safe: Cold Steel shows the choice as out of date and
leaves it out of the patch.
