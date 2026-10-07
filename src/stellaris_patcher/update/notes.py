"""Stellaris's announcements from Steam, in full, as plain text.

    notes = fetch()                            # newest first; raises NotesError
    archive(notes)                             # kept in ~/.local/share/stellaris-patcher/notes/
    kept = load_archive()                      # every one fetched so far, newest first
    names = modding_names(kept[0].text)        # names its Modding section removes or renames

Steam's news API gives each announcement's whole text, where a web page
summary can cut the bug fixes and modding notes off. It only gives the
newest ones, so each fetch is archived: a mod that hasn't updated since 4.5
needs the 4.5 notes long after Steam stops listing them.
"""

import json
import re
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from stellaris_patcher.paradox.game import STELLARIS_APP_ID
from stellaris_patcher.store import paths

URL = (
    "https://api.steampowered.com/ISteamNews/GetNewsForApp/v2/"
    f"?appid={STELLARIS_APP_ID}&count={{count}}&maxlength=0&feeds=steam_community_announcements"
)


class NotesError(Exception):
    """Steam's news couldn't be fetched or read."""


@dataclass(frozen=True)
class Note:
    date: datetime
    title: str
    text: str
    url: str

    @property
    def file_name(self) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", self.title.casefold()).strip("-")[:60]
        return f"{self.date:%Y-%m-%d}-{slug}.txt"

    def as_file(self) -> str:
        """The title, link and time on the first three lines, then the text."""
        return f"{self.title}\n{self.url}\n{self.date.isoformat()}\n\n{self.text}"


def notes_dir() -> Path:
    return paths.data_dir() / "notes"


def archive(notes: list[Note], folder: Path | None = None) -> int:
    """Saves the notes not already kept. Returns how many were new."""
    folder = folder or notes_dir()
    folder.mkdir(parents=True, exist_ok=True)
    new = 0
    for note in notes:
        target = folder / note.file_name
        if not target.exists():
            target.write_text(note.as_file(), "utf-8")
            new += 1
    return new


def load_archive(folder: Path | None = None) -> list[Note]:
    """Every kept note, newest first. A file that isn't a kept note is skipped."""
    found: list[Note] = []
    for path in sorted((folder or notes_dir()).glob("*.txt")):
        parts = path.read_text("utf-8").split("\n", 4)  # title, url, time, "", text
        try:
            date = datetime.fromisoformat(parts[2])
        except IndexError, ValueError:
            continue
        found.append(Note(date, parts[0], parts[4] if len(parts) > 4 else "", parts[1]))
    return sorted(found, key=lambda n: n.date, reverse=True)


# A Modding line about a name that went away, and the names in it.
_GONE = re.compile(
    r"remov|renam|deprecat|moved|no longer|is now|now called|supersed|replac", re.IGNORECASE
)
_NAME = re.compile(
    r"`([^`\s<>*]+)`"  # anything in backticks
    r"|(?<![\w.@/])(@?[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)+(?:\.txt)?)"  # snake_case, FILE.txt
)


def modding_names(text: str) -> set[str]:
    """Names in the Modding section's lines that remove, rename or move
    something: leads to search mods for, old and new names alike."""
    found: set[str] = set()
    inside = False
    for line in text.splitlines():
        bare = line.strip().strip("​").removeprefix("- ").strip().strip("​").rstrip(":")
        if bare.casefold() == "modding":
            inside = True
            continue
        if inside and line.strip() and not line.startswith("- "):
            inside = False
        if inside and _GONE.search(line):
            found.update(a or b for a, b in _NAME.findall(line))
    return {n for n in found if "_" in n}


def fetch(count: int = 10, timeout: float = 30) -> list[Note]:
    try:
        with urllib.request.urlopen(URL.format(count=count), timeout=timeout) as response:
            items = json.load(response)["appnews"]["newsitems"]
    except (OSError, ValueError, KeyError, TypeError) as error:
        raise NotesError(f"Couldn't fetch Steam's news: {error}") from error
    return [
        Note(
            datetime.fromtimestamp(int(i["date"]), UTC),
            str(i["title"]),
            plain(str(i["contents"])),
            str(i.get("url", "")),
        )
        for i in items
    ]


_HEADING = re.compile(r"\[h\d\](.*?)\[/h\d\]", re.DOTALL)
_ITEM = re.compile(r"\[\*\]")
_TAG = re.compile(r"\[/?[a-z0-9*]+(?:[= ][^\]]*)?\]")


def plain(bbcode: str) -> str:
    """Steam's BBCode as text: headings on their own lines, list items as `- `."""
    text = _HEADING.sub(lambda m: f"\n\n## {m.group(1).strip()}\n", bbcode)
    text = _ITEM.sub("\n- ", text)
    text = re.sub(r"\[/?p\]", "\n", text)
    text = _TAG.sub("", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"^- *\n+", "- ", text, flags=re.MULTILINE)  # an item's text, on its line
    return re.sub(r"\n{3,}", "\n\n", text).strip() + "\n"
