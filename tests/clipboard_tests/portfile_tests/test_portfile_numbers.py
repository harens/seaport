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

import pytest
from pytest_mock import MockFixture

from seaport.clipboard.portfile.portfile_numbers import new_version, undo_revision


def test_undo_revision(capfd) -> None:

    # If there are no revision numbers to change
    assert undo_revision("No revision numbers here") == "No revision numbers here"
    out, err = capfd.readouterr()
    assert out == "⏪️ Changing revision numbers\nNo changes necessary\n"
    assert not err

    # If there's one revision
    assert (
        undo_revision("name   example\n revision    1\n version      1.0")
        == "name   example\n revision    0\n version      1.0"
    )
    out, err = capfd.readouterr()
    assert out == "⏪️ Changing revision numbers\nRevision number changed\n"
    assert not err

    # If there's multiple revision numbers with 0
    assert (
        undo_revision("name   example\n revision    0\n revision      0")
        == "name   example\n revision    0\n revision      0"
    )
    out, err = capfd.readouterr()
    assert out == "⏪️ Changing revision numbers\nNo changes necessary\n"
    assert not err

    # If there's multiple revision numbers, with at least one of them 1
    with pytest.raises(SystemExit):
        undo_revision("revision      1\n name     relkjwk\n  revision    1")


def test_new_version(fake_process, session_mocker: MockFixture, capfd) -> None:

    # Manually set new version
    assert new_version("example-port", "4.0", "3.0") == "4.0"
    out, err = capfd.readouterr()
    assert not out
    assert not err

    # Current version is the same as new version
    # Manually set
    with pytest.raises(SystemExit):
        new_version("example-port", "1.0", "1.0")

    # Livecheck where the port is already up-to-date
    # Set default path
    session_mocker.patch(
        "seaport.clipboard.portfile.portfile_numbers.user_path",
        return_value="/opt/local/bin",
    )

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "livecheck", "example-port"], stdout=[""]
    )

    # Already up-to-date by livecheck
    with pytest.raises(SystemExit):
        new_version("example-port", "", "2.0")

    # Livecheck new version
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "livecheck", "example-port"],
        stdout=[
            "example-port seems to have been updated (port version: 2.0, new version: 2.1)\n"
        ],
        occurrences=2,
    )

    assert new_version("example-port", "", "2.0") == "2.1"

    # If devel version is being applied to a standard port
    session_mocker.patch("click.confirm", return_value=False)

    with pytest.raises(SystemExit):
        new_version("example-port", "1.2-devel", "1.1")

    # If devel version is being applied to a devel port
    session_mocker.patch("click.confirm", return_value=True)

    assert new_version("example-port", "1.2-devel", "1.1") == "1.2-devel"

    # If it's a new port (livecheck)

    assert new_version("example-port", "", "2.1", True) == "2.1"

    # If it's a new port (set by --bump)

    assert new_version("example-port", "2.1", "2.1", True) == "2.1"
