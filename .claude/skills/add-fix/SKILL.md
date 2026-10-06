---
name: add-fix
description: Add or change a fix in the Cold Steel Mix patch, with its tests and docs. Use when the user agrees to a fix proposed in a report, or asks to add, change or drop a patch fix.
---

Follow [Add a fix](../../../docs/patches/cold-steel-mix.md#add-a-fix) in
docs/patches/cold-steel-mix.md.

- Only add a fix the user has agreed to
  ([decision 25](../../../docs/decisions.md)). If it came from a report but
  wasn't agreed yet, ask first.
- Read [patch-rules.md](../../../docs/reference/patch-rules.md) before
  choosing how the fix's file wins.
- `make check` must pass. Then offer to rebuild with the `build-patch` skill.
