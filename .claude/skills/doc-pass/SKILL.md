---
name: doc-pass
description: Read every doc, skill and code comment against the code and the decisions, fix what's stale or inconsistent, and cut history while keeping the gotchas. Use when the user asks for a doc pass, a docs review or cleanup, or to check the docs or comments for stale entries.
---

Read [CLAUDE.md](../../../CLAUDE.md) first, then follow
[docs/doc-pass.md](../../../docs/doc-pass.md) step by step.

Rules from it that are easy to miss:

- Cover every doc, every skill, and the comments and docstrings in `src/`,
  `tests/`, `tools/`, the Makefile, `.devcontainer/` and the workflow.
- Check each name, flag and command against the code. Don't trust the doc.
- Cut history, keep gotchas. A trap someone could fall into again stays,
  written as a present-tense rule with its reason.
- Change words only, never what the code does.
- Leave the reports, the Workshop upload history and the decisions' "Date"
  and "Changed" columns as they are. They're records.
- If a decision looks wrong, ask the user. Don't edit it to match a doc.
