"""Stellaris's announcements from Steam, in full, as plain text.

    notes = fetch()                            # newest first; raises NotesError
    recent = [n for n in notes if n.date > when]

Steam's news API gives each announcement's whole text, where a web page
summary can cut the bug fixes and modding notes off.
"""

import json
import re
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime

from stellaris_patcher.paradox.game import STELLARIS_APP_ID

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
