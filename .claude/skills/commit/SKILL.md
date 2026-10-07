---
name: commit
description: Commit the changes on a branch named for the work, open a pull request, merge it into main, switch back to main, and delete every branch merged into main, locally and on GitHub. Use when the user asks to commit, push, open or merge a PR, or ship the changes.
---

Follow [Commit and merge](../../../docs/development.md#commit-and-merge) in
docs/development.md.

- Asking for this skill is the request to push and merge. Don't ask again.
- `make check` must pass before the commit.
- Stage files by name, never with `git add -A`.
- Merge with `--merge`, not squash or rebase. Only a merge commit leaves
  the branch listed by `git branch --merged`, which the cleanup relies on.
- Delete only branches `--merged` lists, and never `main`. Show the list
  before deleting.
