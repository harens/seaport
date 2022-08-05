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

from seaport.portfile import Port


# TODO: Maybe put this somewhere better?
def setup_port(fake_process: FakeProcess, name: str = "gping") -> Port:
    """Generates an example gping v0.1 port for testing.

    Since the docstrings use --index, the setup_port functions doesn't for greater coverage.
    """

    fake_process.register_subprocess(
        ["/usr/bin/which", "port"], stdout=["/opt/local/bin/port"]
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "--index", name],
        stdout=["example output"],
        occurrences=4,
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", name],
        stdout=["different output"],
        occurrences=4,
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "--version", name],
        stdout=["version: 0.1"],
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "--version", "--index", name],
        stdout=["version: 0.1"],
    )

    return Port(name)


def test_outdated_livecheck(fake_process: FakeProcess) -> None:
    """If a port is out of date."""

    port = setup_port(fake_process)

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "livecheck", "gping"],
        stdout=[
            "gping seems to have been updated (port version: 0.1, new version: 0.2)"
        ],
    )

    assert port.livecheck() == "0.2"


def test_nonindex_category(fake_process: FakeProcess) -> None:
    port = setup_port(fake_process)

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "--category", "gping"],
        stdout=["category: net, something-else"],
    )

    assert port.primary_category() == "net"


def test_failed_finding_checksums(
    fake_process: FakeProcess, session_mocker: MockFixture
) -> None:
    """In the unlikely but possible event that a port is valid but doesn't have any distfiles."""
    port = setup_port(fake_process)

    session_mocker.patch("seaport.portfile.Port.subports", return_value=None)

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "distfiles", "gping"], stdout=[""]
    )

    with pytest.raises(Exception) as excinfo:
        port.checksums()

    assert "port distfiles gping provides no output" == str(excinfo.value)
