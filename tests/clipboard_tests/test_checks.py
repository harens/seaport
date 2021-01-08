# See https://alexmarandon.com/articles/python_mock_gotchas/

import pytest
from pytest_mock import MockFixture

from seaport.clipboard.checks import cmd_check, exists, preliminary_checks, user_path


def test_cmd() -> None:
    """Should be true if the cmd exists"""
    assert not cmd_check("fjslfksdjf")
    assert cmd_check("echo")


def test_user_path(fake_process) -> None:

    # Port prefix
    fake_process.register_subprocess(
        ["/usr/bin/which", "port"], stdout=["/opt/local/bin/port\n"], occurrences=5
    )

    assert user_path(True) == "/opt/local/bin"

    # Default prefix (first party tools)
    assert user_path() == "/usr/bin"

    # Third party tool prefixes

    # If installed by MacPorts
    fake_process.register_subprocess(
        ["/usr/bin/which", "seaport"], stdout=["/opt/local/bin/seaport\n"]
    )

    assert user_path(False, True) == "/opt/local/bin"

    # If installed by Homebrew

    fake_process.register_subprocess(
        ["/usr/bin/which", "seaport"], stdout=["/usr/local/bin/seaport\n"]
    )

    assert user_path(False, True) == "/usr/local/bin"

    # Poetry example (should default to MacPorts)

    fake_process.register_subprocess(
        ["/usr/bin/which", "seaport"],
        stdout=[
            "~/Library/Caches/pypoetry/virtualenvs/seaport-kpP_O3aU-py3.8/bin/seaport\n"
        ],
    )

    assert user_path(False, True) == "/opt/local/bin"


def callback_info(process) -> None:
    """`port info some-nonexistent-port` output"""
    process.returncode = 1
    process.stdout = "Error: Port some-nonexistent-port not found"


def test_exists(fake_process, session_mocker: MockFixture) -> None:

    # Set default path
    session_mocker.patch(
        "seaport.clipboard.checks.user_path", return_value="/opt/local/bin"
    )

    # Port that exists
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "some-port"], stdout=["some output"]
    )

    exists("some-port")

    # Port that doesn't exist
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "some-nonexistent-port"], callback=callback_info
    )

    with pytest.raises(SystemExit):
        exists("some-nonexistent-port")


def test_preliminary_checks(fake_process, session_mocker: MockFixture) -> None:
    # Set default path
    session_mocker.patch(
        "seaport.clipboard.checks.user_path", return_value="/opt/local/bin"
    )

    # port name, pr location
    existent_port = ["some-port", "~/example"]
    nonexistent_port = ["some-nonexistent-port", "~/example"]

    # Port that exists
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", existent_port[0]],
        stdout=["some output"],
        occurrences=2,
    )

    # Both port and gh pass
    session_mocker.patch("seaport.clipboard.checks.cmd_check", return_value=True)
    preliminary_checks(*existent_port)

    # port fails since it's the first test
    session_mocker.patch("seaport.clipboard.checks.cmd_check", return_value=False)
    with pytest.raises(SystemExit):
        preliminary_checks(*existent_port)

    # Port that doesn't exist
    session_mocker.patch("seaport.clipboard.checks.cmd_check", return_value=True)
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", nonexistent_port[0]], callback=callback_info
    )

    with pytest.raises(SystemExit):
        preliminary_checks(*nonexistent_port)
