# Doc pass

**Read every doc and every code comment against the code and the decisions.
Fix what's stale or inconsistent, and cut history that no longer helps. Keep
the gotchas.** A pass changes words only, never what the code does.

## The steps

1. **Read [CLAUDE.md](../CLAUDE.md) first**, then
   [How we write docs](README.md#how-we-write-docs) and
   [decisions.md](decisions.md). The decisions are the current answer: a
   doc or comment that disagrees with one is the thing to fix.

2. **Go through every doc**, one at a time:
   - [CLAUDE.md](../CLAUDE.md) and the [README](../README.md)
   - each file in the [documentation map](README.md#documentation-map),
     except the records below
   - each skill in [.claude/skills/](../.claude/skills/)

3. **Go through every comment and docstring** in
   [src/](../src/stellaris_patcher/), [tests/](../tests/),
   [tools/](../tools/), the [Makefile](../Makefile),
   [.devcontainer/](../.devcontainer/) and
   [.github/workflows/](../.github/workflows/).

4. **Check each against the code.** Open the file, function, flag or
   command it names and confirm it still exists and still does that. Run a
   command's `--help` rather than trusting the doc.

5. **Fix it in place**, following [How we write docs](README.md#how-we-write-docs).
   Where it's unclear which side is right, or a decision itself looks wrong,
   ask the user instead of guessing.

6. **Run `make check`.** Then tell the user what changed, file by file, and
   what's left as a question. Offer the `commit` skill.

## What to look for

**Stale:**

- a file, function, flag, command or path that's gone or renamed
- a count, a fix number or a decision number that no longer matches
- a step a skill or doc repeats that its doc has since changed
- a "todo", "for now" or "not yet" that has since been done

**Inconsistent:**

- one fact told two ways in two places
- one fact written out in two places. Keep it in one, and link to it from
  the other ([one place per fact](README.md#how-we-write-docs))
- a table that's missing a row, like a skill missing from the README's
  [skills table](../README.md#work-with-claude-code) or a doc missing from
  the [documentation map](README.md#documentation-map)

**Bloat:**

- history: what it used to be, what was tried first, when it changed, which
  report found it. Write the current state only. The reports, the decisions'
  "Changed" column and git keep the history
- reasons that repeat a decision row. Link to the row
- a comment that says what the next line plainly does

## What to keep

- **Gotchas.** A trap someone would fall into again stays, even if it was
  learned the hard way. Write it as a present-tense rule with its reason,
  and keep the link to the report that found it.
- **Why a workaround exists**, in a comment next to it. Without it, the
  next reader "fixes" it.

## Leave these alone

They're records of what happened, so their old facts are right for their
date:

- the reports in [docs/reports/](README.md#reports)
- the uploads in
  [cold-steel-mix-patch-notes.md](patches/cold-steel-mix-patch-notes.md)
- the "Date" and "Changed" columns of [decisions.md](decisions.md)

A broken link in a record can be fixed. Nothing else in it changes.
