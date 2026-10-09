---
name: commit
description: Commit the changes on a branch named for the work, open a pull request, wait for GitHub's check to pass, merge it into main, switch back to main, and delete every branch merged into main, locally and on GitHub. Use when the user asks to commit, push, open or merge a PR, or ship the changes.
---

Follow [Commit and merge](../../../docs/development.md#commit-and-merge) in
docs/development.md.

- Asking for this skill is the request to push and merge. Don't ask again.
- `make check` must pass before the commit.
- Stage files by name, never with `git add -A`.
- **Pause for GitHub's check before merging** (step 4). Run the wait loop
  and `--watch` as one Bash call in the background, so the session picks up
  again when it ends. Don't merge while it's running.
- Watching straight after `gh pr create` stops with "no checks reported".
  That isn't a pass: wait for the check to show up, as the loop does.
- If the check fails, don't merge, and never use `--admin` to get past it.
  Read the failed log, fix the cause on the branch, push, and wait again.
- Merge with `--merge`, not squash or rebase. Only a merge commit leaves
  the branch listed by `git branch --merged`, which the cleanup relies on.
- Delete only branches `--merged` lists, and never `main`. Show the list
  before deleting.
