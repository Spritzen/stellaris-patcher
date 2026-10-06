---
name: update-check
description: Check the Cold Steel Mix playset and its patch after Stellaris or a playset mod updates. Use when the user says the game or a mod has updated, asks to check patch notes against the patch, or asks for the update check.
---

Follow [docs/update-check.md](../../../docs/update-check.md) step by step. It
holds the commands, how to read the check, how to write the report, and
the lessons from earlier checks.

Two rules from it that are easy to miss:

- Propose fixes in the report and wait for the user before adding any
  ([decision 25](../../../docs/decisions.md)).
- Ask the user to close the game and the launcher before `--write`. The
  container can't see them.
