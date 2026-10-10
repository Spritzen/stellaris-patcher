"""Is the Paradox launcher or the game running? Read from /proc.

A patch mod is written only while both are closed. Inside the container
host processes can't be seen, so this finds nothing there.
"""

from pathlib import Path

# Names as /proc/<pid>/comm gives them: the program's file name, cut to 15 characters.
LAUNCHER = frozenset({"dowser", "Paradox Launche"})
GAME = frozenset({"stellaris"})


def running(names: frozenset[str], proc: Path = Path("/proc")) -> bool:
    try:
        entries = list(proc.iterdir())
    except OSError:
        return False
    for entry in entries:
        if not entry.name.isdigit():
            continue
        try:
            comm = (entry / "comm").read_text("utf-8", errors="replace").strip()
        except OSError:  # it ended while we looked, or isn't ours to read
            continue
        if comm in names:
            return True
    return False
