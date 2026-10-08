"""Localisation files: `localisation/**/*_l_<language>.yml`.

    l_english:
     tech_lasers_1:0 "Red Lasers"

Each file says its language on its first line. `keys()` gives each `KEY: "text"`
line as a script `Entry`, so callers treat both kinds of file alike.
"""

import re

from stellaris_patcher.paradox.script import Entry

_LANGUAGE = re.compile(rb"\A(?:\xef\xbb\xbf)?(?:[ \t]*+(?:#[^\n]*+)?\r?\n)*+[ \t]*(l_\w+)[ \t]*:")
# The `:0` is optional: the game's own files leave it out on most English lines.
_KEY = re.compile(rb'^[ \t]*([^\s:#"]+)[ \t]*:[ \t]*\d*[ \t]*(".*)$', re.MULTILINE)


def language(data: bytes) -> str:
    """The language the first line names, like "l_english", or "" if there's none."""
    found = _LANGUAGE.match(data)
    return found.group(1).decode("ascii", "replace") if found else ""


def keys(data: bytes) -> list[Entry]:
    entries: list[Entry] = []
    line = 1
    counted = 0
    for found in _KEY.finditer(data):
        start = found.start(1)
        line += data.count(b"\n", counted, start)
        counted = start
        end = found.end(2)
        if data[end - 1 : end] == b"\r":
            end -= 1
        entries.append(Entry(found.group(1), start, found.start(2), end, line, False))
    return entries
