import os

from click.testing import CliRunner
from pytest_mock import MockFixture

from seaport import __version__
from seaport._clipboard.format import format_subprocess
from seaport._init import seaport


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
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.8.0" in format_subprocess(["pbpaste"])


def test_url() -> None:
    runner = CliRunner()
    result = runner.invoke(
        seaport,
        [
            "clip",
            "py-rich",
            "--bump",
            "9.7.0",
            "--url",
            "https://files.pythonhosted.org/packages/source/r/rich/rich-9.8.0.tar.gz",
        ],
    )
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.7.0" in format_subprocess(["pbpaste"])


def test_no_sudo() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.7.0"])
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.7.0" in format_subprocess(["pbpaste"])


def test_test_only() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.8.0", "--test"])
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.8.0" in format_subprocess(["pbpaste"])


def test_lint_only() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.7.0", "--lint"])
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.7.0" in format_subprocess(["pbpaste"])


def test_install_only() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.8.0", "--install"])
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.8.0" in format_subprocess(["pbpaste"])


def test_lint_fail(session_mocker: MockFixture) -> None:

    # If linting fails
    session_mocker.patch(
        "seaport._clipboard.clipboard.perform_lint",
        return_value=False,
    )

    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "gping", "--bump", "1.1.0", "--lint"])
    assert result.exit_code == 1


def test_write() -> None:
    # Only do these tests in GitHub Actions
    # These tests would overwrite the user's local portfiles
    github_actions = os.getenv("GITHUB_ACTIONS") == "true"

    if github_actions:
        runner = CliRunner()
        result = runner.invoke(
            seaport, ["clip", "py-rich", "--bump", "9.8.0", "--write"]
        )
        assert result.exit_code == 0
        assert "9.8.0" in format_subprocess(["pbpaste"])
        assert (
            "📋 The contents of the portfile have been copied to your clipboard!"
            in result.output
        )
