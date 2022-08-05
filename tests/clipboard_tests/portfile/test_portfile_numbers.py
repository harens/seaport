#!/usr/bin/env python3

# Copyright (c) 2022, harens
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

import pytest
from pytest_mock import MockFixture
from pytest_subprocess import FakeProcess

from seaport._clipboard.portfile.portfile_numbers import new_version
from seaport.portfile import Port


def setup_port(fake_process: FakeProcess, name: str = "gping") -> Port:
    """Generates an example gping v0.1 port for testing."""
    fake_process.register_subprocess(
        ["/usr/bin/which", "port"], stdout=["/opt/local/bin/port"]
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "--index", name],
        stdout=["example output"],
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "--version", "--index", name],
        stdout=["version: 0.1"],
    )

    return Port(name)


def test_livecheck(fake_process: FakeProcess) -> None:
    """Test new version check when using livecheck."""
    port = setup_port(fake_process)

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "livecheck", "gping"],
        stdout=[
            "gping seems to have been updated (port version: 0.1, new version: 0.2)"
        ],
    )

    assert new_version(port, None) == "0.2"


def test_latest_version(fake_process: FakeProcess) -> None:
    """If the port is already up to date."""
    port = setup_port(fake_process)

    with pytest.raises(SystemExit):
        new_version(port, "0.1")


def test_dev_version_nondev_port(
    fake_process: FakeProcess, session_mocker: MockFixture
) -> None:
    """If the latest version is a developer option for a non-dev port"""
    port = setup_port(fake_process)

    # User doesn't want to use the new version
    session_mocker.patch("click.confirm", return_value=False)

    with pytest.raises(SystemExit):
        new_version(port, "0.2-alpha")

    # User does want to continue
    session_mocker.patch("click.confirm", return_value=True)

    assert new_version(port, "0.2-alpha") == "0.2-alpha"


def test_dev_version_dev_port(fake_process: FakeProcess) -> None:
    """New dev version of a port, but the port is a dev port."""
    port = setup_port(fake_process, "gping-devel")

    assert new_version(port, "0.2-alpha") == "0.2-alpha"
