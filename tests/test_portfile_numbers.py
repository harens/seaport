import pytest
from pytest_mock import MockFixture

from seaport.portfile_numbers import new_version, undo_revision


def test_undo_revision(capfd) -> None:

    # If there are no revision numbers to change
    assert undo_revision("No revision numbers here") == "No revision numbers here"
    out, err = capfd.readouterr()
    assert out == "⏪️ Changing revision numbers\nNo changes necessary\n"
    assert not err

    # If there's one revision
    assert (
        undo_revision("name   example\n revision    1\n version      1.0")
        == "name   example\n revision    0\n version      1.0"
    )
    out, err = capfd.readouterr()
    assert out == "⏪️ Changing revision numbers\nRevision number changed\n"
    assert not err

    # If there's multiple revision numbers with 0
    assert (
        undo_revision("name   example\n revision    0\n revision      0")
        == "name   example\n revision    0\n revision      0"
    )
    out, err = capfd.readouterr()
    assert out == "⏪️ Changing revision numbers\nNo changes necessary\n"
    assert not err

    # If there's multiple revision numbers, with at least one of them 1
    with pytest.raises(SystemExit):
        undo_revision("revision      1\n name     relkjwk\n  revision    1")


def test_new_version(fake_process, session_mocker: MockFixture, capfd) -> None:

    # Manually set new version
    assert new_version("example-port", "4.0", "3.0") == "4.0"
    out, err = capfd.readouterr()
    assert not out
    assert not err

    # Current version is the same as new version
    # Manually set
    with pytest.raises(SystemExit):
        new_version("example-port", "1.0", "1.0")

    # Livecheck where the port is already up-to-date
    # Set default path
    session_mocker.patch(
        "seaport.portfile_numbers.user_path", return_value="/opt/local/bin"
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "livecheck", "example-port"], stdout=[""]
    )

    # Already up-to-date by livecheck
    with pytest.raises(SystemExit):
        new_version("example-port", "", "2.0")

    # Livecheck new version
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "livecheck", "example-port"],
        stdout=[
            "example-port seems to have been updated (port version: 2.0, new version: 2.1)\n"
        ],
    )

    assert new_version("example-port", "", "2.0") == "2.1"
