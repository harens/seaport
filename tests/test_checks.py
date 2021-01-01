# See https://alexmarandon.com/articles/python_mock_gotchas/

import pytest
from pytest_mock import MockFixture

from seaport.checks import cmd_check, exists, preliminary_checks, user_path


def test_cmd() -> None:
    """Should be true if the cmd exists"""
    assert not cmd_check("fjslfksdjf")
    assert cmd_check("echo")


def callback_info(process) -> None:
    """`port info some-nonexistent-port` output"""
    process.returncode = 1
    process.stdout = "Error: Port some-nonexistent-port not found"


def test_exists(fake_process, session_mocker: MockFixture) -> None:

    # Set default path
    session_mocker.patch("seaport.checks.user_path", return_value="/opt/local/bin")

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
    session_mocker.patch("seaport.checks.user_path", return_value="/opt/local/bin")

    # port name, pr location
    existent_port = ["some-port", "~/example"]
    nonexistent_port = ["some-nonexistent-port", "~/example"]

    # Port that doesn't exist
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", nonexistent_port[0]], callback=callback_info
    )

    with pytest.raises(SystemExit):
        preliminary_checks(*nonexistent_port)

    # Port that exists
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", existent_port[0]],
        stdout=["some output"],
        occurrences=2,
    )

    # Both port and gh pass
    session_mocker.patch("seaport.checks.cmd_check", return_value=True)
    preliminary_checks(*existent_port)

    # port fails since it's the first test
    session_mocker.patch("seaport.checks.cmd_check", return_value=False)
    with pytest.raises(SystemExit):
        preliminary_checks(*existent_port)
