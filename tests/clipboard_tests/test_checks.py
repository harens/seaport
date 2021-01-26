#!/usr/bin/env python3

# Copyright (c) 2021, harens
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

# See https://alexmarandon.com/articles/python_mock_gotchas/

import os

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
        occurrences=3,
    )

    # Only do these tests in GitHub Actions
    # These test are brokent if the user has GH CLI already installed
    github_actions = os.getenv("GITHUB_ACTIONS") == "true"

    # Don't want to install GitHub CLI
    session_mocker.patch("click.confirm", return_value=False)
    if github_actions:
        # No GH CLI Installed
        with pytest.raises(SystemExit):
            # Shouldn't matter whether port is existent or not
            preliminary_checks(*existent_port)

    # Does want to install GitHub CLI
    session_mocker.patch("click.confirm", return_value=True)
    fake_process.register_subprocess(
        ["/opt/local/bin/sudo", "/opt/local/bin/port", "install", "gh"],
        stdout=["gh installed"],
    )
    if github_actions:
        # No GH CLI Installed
        preliminary_checks(*existent_port)

    # Both port and gh pass
    session_mocker.patch("seaport.clipboard.checks.cmd_check", return_value=True)
    preliminary_checks(*existent_port)

    # port fails since it's the first test
    session_mocker.patch("seaport.clipboard.checks.cmd_check", return_value=False)
    with pytest.raises(SystemExit):
        preliminary_checks(*existent_port)

    # Port that doesn't exist
    # port and gh tests pass
    session_mocker.patch("seaport.clipboard.checks.cmd_check", return_value=True)
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", nonexistent_port[0]], callback=callback_info
    )

    with pytest.raises(SystemExit):
        preliminary_checks(*nonexistent_port)
