---
name: game-report
description: Read Stellaris's error log after the user plays the Cold Steel Mix playset, trace each entry to its mod and write a report. Use when the user says they played, shares how a game went, mentions errors or something looking wrong in game, or asks for an error-log report.
---

Follow [docs/game-report.md](../../../docs/game-report.md) step by step. It
holds where the log is, how to trace entries to mods, and what the report
holds.

Two rules from it that are easy to miss:

- Propose fixes in the report and wait for the user before adding any
  ([decision 25](../../../docs/decisions.md)).
- Use our [error_log.py](../../../src/stellaris_patcher/paradox/error_log.py),
  not Cold Steel's reader. Older reports name Cold Steel's, and its source
  isn't mounted any more ([decision 27](../../../docs/decisions.md)).
