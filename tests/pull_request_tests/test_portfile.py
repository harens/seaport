import pytest
from pytest_mock import MockFixture

from seaport.pull_request.portfile import new_contents


def test_new_contents(fake_process, session_mocker: MockFixture) -> None:
    # If the new version cannot be found
    fake_process.register_subprocess(
        ["pbpaste"], stdout=["Example portfile contents"], occurrences=2
    )

    session_mocker.patch("os.getenv", return_value=None)

    with pytest.raises(SystemExit):
        new_contents()

    # If everything works
    session_mocker.patch("os.getenv", return_value="v1.2")

    assert new_contents() == ("Example portfile contents\n", "v1.2")

    # If the portfile contents can't be found

    fake_process.register_subprocess(["pbpaste"], stdout=["something else"])

    with pytest.raises(SystemExit):
        new_contents()
