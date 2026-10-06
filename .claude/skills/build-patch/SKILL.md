---
name: build-patch
description: Build the Cold Steel Mix patch mod and link it into the game, optionally adding it to the playset. Use when the user asks to build, rebuild or write the patch, or after a fix has been added or changed.
---

Follow [Build it](../../../docs/patches/cold-steel-mix.md#build-it) in
docs/patches/cold-steel-mix.md.

- Run it without `--write` first, and show the user which fixes are written
  and which are left out, with the reasons.
- Ask the user to close the game and the launcher before `--write`. The
  container can't see them.
- `--add-to-playset` writes Cold Steel's files: pass `--cold-steel-closed`
  only after the user says Cold Steel is closed.
- End by reminding the user to **rebuild Cold Steel Mix in Cold Steel**. The
  game only sees the patch once it's rebuilt.
