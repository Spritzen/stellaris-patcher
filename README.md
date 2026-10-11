# Stellaris Patcher

Builds **patch mods for Stellaris playsets**: a small mod that loads last and
fixes the clashes and breakages between the mods in a playset. It comes with
one patch, the [Cold Steel Mix patch](docs/patches/cold-steel-mix.md), for a
26-mod playset on Stellaris 4.5.2.

**You run it through [Claude Code](https://claude.com/claude-code).** You
tell Claude what happened: you played, or the game updated. Claude reads the
logs, writes a report and proposes fixes. Once you agree, it writes the fixes
and builds the patch. You don't need to know Python or Stellaris's script
files.

- [What you need](#what-you-need)
- [Set it up](#set-it-up)
- [Work with Claude Code](#work-with-claude-code)
- [Your first build](#your-first-build)
- [Five things to know](#five-things-to-know)
- [Use it for your own playset](#use-it-for-your-own-playset)
- [Limits](#limits)

## What you need

- **Linux, with Stellaris from Steam.**
- **[Claude Code](https://claude.com/claude-code).**
- **[Cold Steel](https://github.com/Spritzen/cold-steel)**, the mod manager
  that holds the playsets. You can do without it: see
  [adapting.md](docs/adapting.md#without-cold-steel).
- **One of these:**
  - VS Code with Docker or Podman, for the dev container. This is the
    easy way.
  - Python 3.14 with msgspec and xxhash, installed on your own machine.
- Optional: the GitHub CLI, for the `/commit` skill.

## Set it up

### In the dev container

1. **Run Stellaris and Cold Steel once**, so their folders exist.
2. **Open this folder in VS Code**, press F1 and choose **Rebuild and Reopen
   in Container**.
3. **Read the setup output.** It installs Claude Code, backs up the
   launcher's database and Cold Steel's playsets, and checks each folder. A
   red ✗ names what's missing.

The container sees your Steam, Paradox and Cold Steel folders at the same
paths as your machine does. Steam's folder is read-only. Details:
[.devcontainer/](.devcontainer/) and
[development.md](docs/development.md#container-and-host).

### On your own machine

On Arch:

```sh
sudo pacman -S python python-msgspec python-xxhash python-pytest ruff mypy librsvg
```

On another distribution, install the same packages its own way.

### Check it works

Start Claude Code in this folder (`claude`), and ask:

> Check my setup: run make check and find my Stellaris install.

Claude should report the game's version, such as `v4.5.2`.

## Work with Claude Code

**Type a skill as a slash command, or just describe what happened.** Each
skill knows its steps and its safety rules.

| When | Type | Claude does | You do |
|---|---|---|---|
| You want the patch built, or a fix changed | `/build-patch` | Shows which fixes are written and which are left out, then builds the mod and links it into the game | Close the game and launcher when asked. Then rebuild the playset in Cold Steel |
| You've played | `/game-report` | Reads the error log, traces each entry to its mod, writes a report and proposes fixes | Say how long you played, new game or save, and anything that looked wrong |
| Stellaris or a mod updated | `/update-check` | Compares the game and mods with the last check, reads the patch notes, writes a report and proposes fixes | Read the report's "What to do next" and say which fixes you want |
| You agree to a fix | `/add-fix` | Writes the fix, its tests and its docs | Then run `/build-patch` |
| You're about to upload to the Workshop | `/patch-notes` | Writes the change notes from what changed since the last upload | Paste them into Steam. Tell Claude once it's uploaded, so it's recorded |
| The docs may be out of date | `/doc-pass` | Checks every doc and comment against the code, and fixes what's stale | Answer its questions |
| You want the changes saved | `/commit` | Commits on a branch, opens a pull request, waits for GitHub's check, and merges | Nothing |

The work goes round in a loop:

```
play ─► /game-report ─► you agree ─► /add-fix ─► /build-patch ─► rebuild in Cold Steel ─► play
                            ▲
Stellaris or a mod updates ─► /update-check
```

## Your first build

1. **Type `/build-patch`.** Claude first shows what it would write. Each fix
   is `ok`, or `left out` with a reason. Left out usually means an update
   fixed the problem, or that the fix's mod is switched off.
2. **Close the game and the Paradox launcher** when Claude asks. It then
   writes the mod and links it into the game.
3. **The first time, let Claude add the patch to the playset.** Close Cold
   Steel first. The patch goes last, before Cold Steel's own patch mod.
4. **Rebuild the playset in Cold Steel, then play.**
5. **Type `/update-check` once**, and let Claude accept it. That saves today's
   game and mods as the baseline the next update is compared with.

After that, run `/game-report` after you play, and `/update-check` when
something updates.

## Five things to know

1. **Claude proposes, you decide.** A report proposes fixes. None is added
   until you agree ([decision 25](docs/decisions.md)).
2. **Close the game, the launcher and Cold Steel before anything is
   written.** Each one saves over its files when it closes, which undoes the
   change. In the container, Claude can't see them running, so it asks you.
   Only say yes once they're closed.
3. **Rebuild the playset in Cold Steel after every build.** You play Cold
   Steel's built copy of the playset. It only has the new patch once it's
   rebuilt.
4. **Accept an update check before the next update.** Steam keeps no copy
   of the old game, so the baseline is the only one. Without it, the check
   can only guess what changed.
5. **Your files are backed up first.** Cold Steel's files are copied into
   `~/.local/share/stellaris-patcher/backups/`, and the container keeps one
   untouched copy of them and of the launcher's database. Steam's folders
   and the game are never written.

## Use it for your own playset

Ask Claude:

> Adapt this project to my playset, \<name\>.

It follows [adapting.md](docs/adapting.md): your playset's name, a new patch
module with no fixes, and the skills renamed. Then play a short game and run
`/game-report` to find your playset's problems. The first log is usually
thousands of entries, and most don't matter. The reports in
[docs/reports/](docs/README.md#reports) are worked examples.

To upload your patch to the Workshop, ask the other mod authors first: a fix
that copies a mod's file ships their work. See
[Uploading it to the Workshop](docs/patches/cold-steel-mix.md#uploading-it-to-the-workshop).

## Limits

- **Linux and Steam only.** Flatpak and Snap Steam aren't found on their
  own.
- **Fixes can't patch zipped mods.** The update check does read inside zips.
- **English only.** Missing text is added in English
  ([decision 19](docs/decisions.md)).
- **Some merge rules are unchecked.** Rows in
  [merge_rules.json](src/stellaris_patcher/data/merge_rules.json) with no
  `checked` date come from Irony Mod Manager, not a game test.

### Windows or macOS

**You could fork the project and port it to Windows or macOS fairly
easily.** The fixes, the parsers and the update check are plain Python and
work anywhere. The parts tied to Linux are few:

- **Finding the game:** [game.py](src/stellaris_patcher/paradox/game.py)
  looks for Steam in its Linux folders, and refuses the Windows build of the
  game.
- **Telling whether the game, the launcher or Cold Steel is open:**
  [processes.py](src/stellaris_patcher/paradox/processes.py) and
  [coldsteel/files.py](src/stellaris_patcher/coldsteel/files.py) read
  `/proc`.
- **Linking the patch into the game:**
  [write.py](src/stellaris_patcher/patchmod/write.py) uses a symlink, which
  Windows only allows with Developer Mode turned on.
- **The dev container** mounts Linux paths. Run the code on the host
  instead.

Ask Claude to make the port in your fork. Test it with a real build before
you trust it.

## Read more

[docs/README.md](docs/README.md) maps every doc. The commands Claude runs
are in [cold-steel-mix.md](docs/patches/cold-steel-mix.md#build-it) and
[update-check.md](docs/update-check.md), if you want to run them yourself.

## Licence

MIT. See [LICENSE](LICENSE).
