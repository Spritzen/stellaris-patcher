# Where Stellaris keeps things

Checked against the real install of the native Linux build, last on
**v4.5.2** (2026-10-06). Paths are shown with the container's environment
variables, which are the same paths as on the host.

## Game install (read-only)

`$STEAM_DIR/steamapps/common/Stellaris/`

| Item | What it's for |
|---|---|
| `stellaris` | The game program |
| `dowser` | The Paradox launcher. Its process name is how we tell it's open |
| `launcher-settings.json` | Game version (`rawVersion`: `v4.5.2`) and the user data path (`gameDataPath`: `$LINUX_DATA_HOME/Paradox Interactive/Stellaris`) |
| `common/`, `events/`, `localisation/`, `gfx/`, `interface/`… | Vanilla game files. Mods override these, and a patch mod may need to override them too |
| `dlc/` | One folder per DLC |

Stellaris is Steam app **281990**.

## Steam (read-only)

| Path | What it's for |
|---|---|
| `$STEAM_DIR/steamapps/libraryfolders.vdf` | Every Steam library folder, and which apps are in each. Start game discovery here |
| `$STEAM_DIR/steamapps/workshop/content/281990/<id>/` | One folder per subscribed Workshop mod, named by its Workshop ID |

Some Workshop mods are a single `.zip` instead of loose files (for example
mod `1224507727` holds only `exst.zip`). Their `descriptor.mod` is inside the
zip. Read them in place with `zipfile`; never unpack them into Steam's folder.

## Paradox user data (read-write)

`$PARADOX_DATA_DIR/Stellaris/`

| Path | What it's for |
|---|---|
| `mod/*.mod` | One descriptor per mod the game knows about. Workshop mods get `ugc_<id>.mod` |
| `mod/<folder>/` | Local mods, and links to mods built elsewhere, such as Cold Steel's `cold_steel_patch_<playset id>` |
| `dlc_load.json` | **What the game actually loads**: `enabled_mods` (in order) and `disabled_dlcs` |
| `launcher-v2.sqlite` | The Paradox launcher's database: mods and playsets |
| `launcher-v2.stellaris-patcher-orig.sqlite` | Our one-time original backup ([decision 6](../decisions.md)). Never overwrite. Cold Steel keeps its own, `launcher-v2.cold-steel-orig.sqlite` |
| `playsets_backup/<id>.json` | The launcher's own playset backups |
| `logs/error.log` | Errors from the last game run. Older runs are kept as `error.log.<date>` |

### A `.mod` descriptor

```
name="Extended Soundtrack"
tags={
	"Sound"
}
picture="estn.jpg"
supported_version="2.1.*"
archive="/home/…/workshop/content/281990/1224507727/exst.zip"
remote_file_id="1224507727"
```

Loose-file mods use `path="…"` instead of `archive="…"`. Paths are absolute
host paths. `supported_version` must have three parts with only the last one
`*` (the `v` is optional), or the game logs "Invalid supported_version".

### `dlc_load.json`

```json
{"enabled_mods": ["mod/ugc_1623423360.mod", "mod/ugc_3090328185.mod"],
 "disabled_dlcs": ["dlc/dlc033_cosmic_storms/dlc033.dlc"]}
```

The order of `enabled_mods` is the load order.

### `launcher-v2.sqlite` tables

| Table | Holds |
|---|---|
| `mods` | Every known mod: `id` (the launcher's own ID), `steamId`, `name`, `displayName`, `version`, `requiredVersion`, `dirPath`, `archivePath`, `thumbnailPath`, `status` (`ready_to_play`, or `unsubscribed` for mods gone from disk) and more |
| `playsets` | `id`, `name`, `isActive`, `loadOrder`, `createdOn`, `updatedOn`, `isRemoved`… |
| `playsets_mods` | Which mods are in which playset: `playsetId`, `modId`, `enabled`, `position` |
| `playsets_dlcs` | DLC per playset: `playsetId`, `dlcId`, `enabled` |

A `dlcId` is the DLC's folder name (`dlc033_cosmic_storms`), or for older DLC
the folder name without its number (`arachnoid` for `dlc002_arachnoid`). See
[dlc.py](../../src/stellaris_patcher/paradox/dlc.py).

The layout changes between launcher versions.
[launcher_db.py](../../src/stellaris_patcher/paradox/launcher_db.py) checks for
the columns it needs on open and stops clearly if they're missing. The file
uses `journal_mode=delete`, so opening it read-only creates no `-wal` or `-shm`
files. Adding a mod to the launcher's `mods` table means guessing at 40
columns, so don't.

**Never write it while the launcher is open.** The launcher holds playsets in
memory and writes them back, undoing the change.
[processes.py](../../src/stellaris_patcher/paradox/processes.py) tells whether
it's running, but only on the host: the container can't see host processes.
