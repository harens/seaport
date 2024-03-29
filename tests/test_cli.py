# Copyright (c) 2023, harens
#
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice,
#       this list of conditions and the following disclaimer in the documentation
#       and/or other materials provided with the distribution.
#     * Neither the name of seaport nor the names of its contributors
#       may be used to endorse or promote products derived from this software
#       without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os

from beartype import beartype
from click.testing import CliRunner
from pytest_mock import MockFixture

from seaport import __version__
from seaport._clipboard.format import format_subprocess
from seaport._init import seaport


@beartype
def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"seaport, version {__version__}\n"


@beartype
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


@beartype
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


@beartype
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


@beartype
def test_no_sudo() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.7.0"])
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.7.0" in format_subprocess(["pbpaste"])


@beartype
def test_test_only_mainport() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "ioping", "--bump", "1.2", "--test"])
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "1.2" in format_subprocess(["pbpaste"])


@beartype
def test_test_only_subports() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.8.0", "--test"])
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.8.0" in format_subprocess(["pbpaste"])


@beartype
def test_lint_only() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.7.0", "--lint"])
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.7.0" in format_subprocess(["pbpaste"])


@beartype
def test_install_only() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "py-rich", "--bump", "9.8.0", "--install"])
    assert (
        "📋 The contents of the portfile have been copied to your clipboard!"
        in result.output
    )
    assert result.exit_code == 0
    assert "9.8.0" in format_subprocess(["pbpaste"])


@beartype
def test_lint_fail(session_mocker: MockFixture) -> None:
    # If linting fails
    session_mocker.patch(
        "seaport._clipboard.clipboard.perform_lint",
        return_value=False,
    )

    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "gping", "--bump", "1.7.0", "--lint"])
    assert result.exit_code == 1


@beartype
def test_tests_fail(session_mocker: MockFixture) -> None:
    session_mocker.patch(
        "seaport._clipboard.clipboard.perform_test",
        return_value=False,
    )

    runner = CliRunner()
    result = runner.invoke(seaport, ["clip", "ioping", "--bump", "1.2", "--test"])
    assert result.exit_code == 1


@beartype
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
