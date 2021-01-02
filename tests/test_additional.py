from pytest_mock import MockFixture

from seaport.additional import perform_lint


def test_perform_lint(fake_process, session_mocker: MockFixture) -> None:

    # If there are errors present in port lint

    # Set default path
    session_mocker.patch("seaport.additional.user_path", return_value="/opt/local/bin")

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
