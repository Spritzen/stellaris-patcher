# Workshop patch notes

**Before each upload of the Cold Steel Mix patch, write its patch notes
from what changed since the last upload, for the user to paste into the
Workshop.** Each upload and its notes are recorded in
[cold-steel-mix-patch-notes.md](patches/cold-steel-mix-patch-notes.md)
([decision 54](decisions.md)). Writing them changes no game or Cold Steel
file.

## The steps

1. **Find the last upload.** It's the newest entry in
   [cold-steel-mix-patch-notes.md](patches/cold-steel-mix-patch-notes.md),
   and gives the commit it was built from. If it has no notes, offer to
   write them first, from the upload before it. Steam's **Edit** on a
   change note adds them afterwards.

2. **Check the build is current.** The version in
   `~/.local/share/stellaris-patcher/mods/cold_steel_mix_patch/descriptor.mod`
   is the build date, in UTC. If the patch's code changed after it, or a mod
   was switched on or off, [build it](patches/cold-steel-mix.md#build-it)
   first.

3. **List what changed since that commit.**

   ```sh
   git log --first-parent --format='%h %ci %s%n%b' <commit>..main
   git diff <commit> main -- src/stellaris_patcher/patchmod/cold_steel_mix.py docs/patches/cold-steel-mix.md docs/decisions.md
   ```

   The commit messages and the fix table say what each fix does. Compare
   the built descriptor's `dependencies` with the last notes and the
   [upload checklist](patches/cold-steel-mix.md#uploading-it-to-the-workshop)
   for mods the patch now needs, or no longer needs.

4. **Keep only what a player would notice:** fixes added, changed or
   dropped, mods switched on or off, required mods added or removed, and a
   new game version. Leave out reports, docs, tests, tools, code tidying and
   the collection's images. If nothing is left, say so: the upload needs no
   notes.

5. **Write the notes** in the shape of the
   [10 October, 11:07 notes](patches/cold-steel-mix-patch-notes.md#10-october-2026-1107):

   - The version, as the built descriptor gives it.
   - One sentence: the main change.
   - A heading for each mod with fixes, then one line per fix. Small fixes
     for other mods go under "Other mods", each starting with its mod's
     name.
   - "Required mods", when they change: which mods it now also needs, or
     no longer needs, then "Load this patch last, after every other mod."
     Name the patch: "Load it last" after a mod's name reads as if that
     mod goes last. A required mod keeps its own place in the load order.

   Each line says what the player sees now, in game words: "Fleets with a
   jump drive can enter…", not the file or the mechanism. Add "as in 4.5.2"
   when the fix brings back the game's own behaviour. No fix numbers,
   decisions or file names: players don't see them. Short sentences, as in
   [how we write docs](README.md#how-we-write-docs).

   Write it as plain text, with no BBCode: a heading is a line of its own,
   and a blank line goes between sections. Steam shows a change note in a
   box, and a `[h2]` heading breaks out of it, leaving the rest of the
   notes outside and an empty box below. Show it in one fenced block,
   ready to paste.

6. **Remind the user of the Workshop page's Required items** when they
   change. Steam doesn't read `dependencies`. Also remind them to paste the
   [description](patches/cold-steel-mix.md#uploading-it-to-the-workshop) if
   its fixes changed.

7. **Once the user has uploaded, record it.** Add an entry at the top of
   [cold-steel-mix-patch-notes.md](patches/cold-steel-mix-patch-notes.md):
   Steam's upload time, the version, the commit on `main` it was built
   from, and the notes as pasted. Clear the "at the next upload" mods in the
   [upload checklist](patches/cold-steel-mix.md#uploading-it-to-the-workshop)
   that the user has added to the page.
