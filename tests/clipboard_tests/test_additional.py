import subprocess

from pytest_mock import MockFixture

from seaport.clipboard.additional import perform_lint, perform_test


def test_perform_lint(fake_process, session_mocker: MockFixture) -> None:

    # If there are errors present in port lint

    # Set default path
    session_mocker.patch(
        "seaport.clipboard.additional.user_path", return_value="/opt/local/bin"
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "lint", "--nitpick", "some-port"],
        stdout=[
            "--->  Verifying Portfile for some-port\n--->  2 errors and 3 warnings found."
        ],
    )

    assert not perform_lint("some-port")

    # If there are warnings and the user chooses to continue

    session_mocker.patch("click.confirm", return_value=True)

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "lint", "--nitpick", "some-port"],
        stdout=[
            "--->  Verifying Portfile for some-port\n--->  0 errors and 3 warnings found."
        ],
        occurrences=2,
    )

    assert perform_lint("some-port")

    # If there are warnings and the user chooses not to continue

    session_mocker.patch("click.confirm", return_value=False)

    assert not perform_lint("some-port")

    # If there are no errors and no warnings

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "lint", "--nitpick", "some-port"],
        stdout=[
            "--->  Verifying Portfile for some-port\n--->  0 errors and 0 warnings found."
        ],
        occurrences=2,
    )

    assert perform_lint("some-port")


def callback_info(process) -> None:
    """`port test name` output if tests fail"""
    raise subprocess.CalledProcessError(1, cmd="port test someport")


def test_perform_test(fake_process, session_mocker: MockFixture) -> None:

    # Set default path
    # Both sudo and port used (hence example)
    session_mocker.patch(
        "seaport.clipboard.additional.user_path", return_value="/example"
    )

    # If the tests pass

    fake_process.register_subprocess(
        ["/example/sudo", "/example/port", "test", "some-port"],
        stdout=["Testing some-port"],
    )

    assert perform_test("some-port", "some-subport")

    # If all tests fail

    # Tests for main port
    fake_process.register_subprocess(
        ["/example/sudo", "/example/port", "test", "some-port"],
        callback=callback_info,
        occurrences=2,
    )

    # Tests for subport
    fake_process.register_subprocess(
        ["/example/sudo", "/example/port", "test", "some-subport"],
        callback=callback_info,
    )

    assert not perform_test("some-port", "some-subport")

    # IF there's no subports

    assert not perform_test("some-port", "")
