from click.testing import CliRunner
from pytest_mock import MockFixture

from seaport import __version__
from seaport.init import seaport


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"seaport, version {__version__}\n"


def test_help() -> None:
    runner = CliRunner()
    # clip used to get 100% cov in init file
    result = runner.invoke(seaport, ["clip", "--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output


# The following tests are slow...and requires macports to be installed
# They could also be more in-depth with their assertions
# Fortunately, GH Actions doesn't require sudo password
# py-rich 9.8.0 chosen since all tests/linting pass


def test_all() -> None:
    runner = CliRunner()
    result = runner.invoke(
        seaport, ["clip", "py-rich", "--bump", "9.8.0", "--lint", "--test", "--install"]
    )
    assert result.exit_code == 0


def test_no_sudo() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.8.0"])
    assert result.exit_code == 0


def test_test_only() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.8.0", "--test"])
    assert result.exit_code == 0


def test_lint_only() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.8.0", "--lint"])
    assert result.exit_code == 0


def test_install_only() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.8.0", "--install"])
    assert result.exit_code == 0


def test_test_fail() -> None:
    # gping has no tests, so this should fail
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "gping", "--bump", "1.1.0", "--test"])
    assert result.exit_code == 1
    assert "Tests failed\n" in result.output


def test_lint_fail(session_mocker: MockFixture) -> None:

    # If linting fails
    session_mocker.patch(
        "seaport.clipboard.clipboard.perform_lint",
        return_value=False,
    )

    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "gping", "--bump", "1.1.0", "--lint"])
    assert result.exit_code == 1
