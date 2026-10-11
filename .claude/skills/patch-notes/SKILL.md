---
name: patch-notes
description: Write the Workshop patch notes for the next upload of the Cold Steel Mix patch, from what changed since the last upload, ready to paste into Steam, and record the upload once it's done. Use when the user is about to upload the patch, asks for patch notes, change notes or Workshop update text, or says they've uploaded it. Not for the game's own patch notes, which the update-check skill reads.
---

Follow [docs/patch-notes.md](../../../docs/patch-notes.md) step by step.
The past uploads and their notes are in
[cold-steel-mix-patch-notes.md](../../../docs/patches/cold-steel-mix-patch-notes.md).

Rules from it that are easy to miss:

- Start from the commit of the newest upload in the history, not from the
  last notes written. An upload with no notes still counts.
- Write for players: what they see in game, no fix numbers, decisions or
  file names. Leave out reports, docs, tests and tools.
- Say "Load this patch last", never "Load it last" after a mod's name:
  only the patch loads last.
- Give the text as plain text, with no BBCode, in one fenced block. A
  `[h2]` heading breaks out of Steam's change note box.
- Record the upload only after the user says it's done, with Steam's time
  and the notes as they pasted them.
