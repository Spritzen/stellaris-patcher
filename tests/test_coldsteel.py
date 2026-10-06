from pathlib import Path

import msgspec
import pytest

from stellaris_patcher.coldsteel import files, records
from stellaris_patcher.coldsteel.files import ColdSteelOpenError, UnknownFormatError
from stellaris_patcher.coldsteel.records import (
    PlaysetEntry,
    PlaysetFile,
    Resolution,
    ResolutionFile,
    Seen,
)

BOOK = PlaysetFile(
    active="p1",
    playsets=[
        records.Playset(
            id="p1",
            name="Mix",
            entries=(PlaysetEntry("workshop:1"), PlaysetEntry("local:x.mod", enabled=False)),
        )
    ],
)


@pytest.fixture
def xdg(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.setenv("XDG_DATA_HOME", str(tmp_path / "data"))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "config"))
    return tmp_path


@pytest.fixture
def closed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(files, "cold_steel_running", lambda: False)


def test_paths_follow_cold_steels_xdg_folders(xdg: Path) -> None:
    assert files.playsets_file() == xdg / "data/cold-steel/playsets.json"
    assert files.resolutions_file("p1") == xdg / "data/cold-steel/resolutions/p1.json"
    assert files.settings_file() == xdg / "config/cold-steel/settings.json"
    assert files.backup_dir() == xdg / "data/stellaris-patcher/backups/cold-steel"


@pytest.mark.usefixtures("closed")
def test_save_backs_up_then_round_trips(xdg: Path) -> None:
    assert files.save_playsets(BOOK) is None  # nothing to back up yet
    backup = files.save_playsets(BOOK)
    assert backup is not None
    assert backup.parent == files.backup_dir()
    assert files.load_playsets() == BOOK

    choices = ResolutionFile(
        resolutions=[Resolution("common/technology", "tech_a", "workshop:1", "a.txt", "", ())]
    )
    files.save_resolutions("p1", choices)
    assert files.load_resolutions("p1") == choices


@pytest.mark.usefixtures("closed")
def test_refuses_a_file_with_fields_we_dont_know(xdg: Path) -> None:
    path = files.playsets_file()
    path.parent.mkdir(parents=True)
    newer = {"version": 1, "active": "", "playsets": [], "groups": ["new in Cold Steel"]}
    path.write_bytes(msgspec.json.encode(newer))

    with pytest.raises(UnknownFormatError, match="fields these records don't"):
        files.save_playsets(BOOK)
    assert msgspec.json.decode(path.read_bytes()) == newer
    assert not files.backup_dir().exists()


@pytest.mark.usefixtures("closed")
def test_refuses_another_version(xdg: Path) -> None:
    path = files.playsets_file()
    path.parent.mkdir(parents=True)
    path.write_bytes(b'{"version": 2, "playsets": []}')
    with pytest.raises(UnknownFormatError, match="version 2"):
        files.save_playsets(BOOK)


@pytest.mark.usefixtures("closed")
def test_an_older_file_missing_default_fields_is_fine(xdg: Path) -> None:
    path = files.playsets_file()
    path.parent.mkdir(parents=True)
    path.write_bytes(b'{"version": 1, "playsets": [{"id": "p1", "name": "Mix"}]}')
    files.save_playsets(BOOK)
    assert files.load_playsets() == BOOK


def test_refuses_while_cold_steel_runs_or_cant_tell(
    xdg: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(files, "cold_steel_running", lambda: True)
    with pytest.raises(ColdSteelOpenError, match="Close it"):
        files.save_playsets(BOOK, cold_steel_closed=True)

    monkeypatch.setattr(files, "cold_steel_running", lambda: None)
    with pytest.raises(ColdSteelOpenError, match="cold_steel_closed=True"):
        files.save_playsets(BOOK)
    assert not files.playsets_file().exists()
    files.save_playsets(BOOK, cold_steel_closed=True)
    assert files.load_playsets() == BOOK


@pytest.mark.parametrize(
    ("cmdline", "found"),
    [
        (b"python3\0-m\0cold_steel\0", True),
        (b"/usr/bin/python\0/usr/bin/cold-steel\0", True),
        (b"python3\0-m\0pytest\0cold-steel-tests\0", False),
        (b"/usr/bin/fish\0", False),
    ],
)
def test_finds_cold_steel_by_its_command_line(tmp_path: Path, cmdline: bytes, found: bool) -> None:
    (tmp_path / "42").mkdir()
    (tmp_path / "42/cmdline").write_bytes(cmdline)
    (tmp_path / "self").mkdir()
    assert files.cold_steel_running(tmp_path, container=False) is found


def test_cant_tell_from_inside_a_container(tmp_path: Path) -> None:
    assert files.cold_steel_running(tmp_path, container=True) is None


def test_settings_default_when_missing(xdg: Path) -> None:
    assert files.load_settings() == records.Settings()


@pytest.mark.real_install
def test_records_read_cold_steels_real_files() -> None:
    """If this fails, Cold Steel's format changed: add the new fields to records.py."""
    found = [
        (files.playsets_file(), records.PlaysetFile, records.PLAYSETS_VERSION),
        *(
            (path, records.ResolutionFile, records.RESOLUTIONS_VERSION)
            for path in sorted((files.data_dir() / "resolutions").glob("*.json"))
        ),
    ]
    found = [f for f in found if f[0].exists()]
    if not found:
        pytest.skip("Cold Steel has no data here.")
    for path, type_, version in found:
        files.check_known(path, type_, version)


def test_seen_is_frozen() -> None:
    seen = Seen("game", "a.txt", 1)
    with pytest.raises(AttributeError):
        seen.layer = "x"  # type: ignore[misc]
