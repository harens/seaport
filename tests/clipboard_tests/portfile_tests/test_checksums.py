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

import pytest
from pytest_mock import MockFixture

from seaport.clipboard.portfile.checksums import current_checksums


def test_current_checksums(fake_process, session_mocker: MockFixture) -> None:
    # Set default path
    session_mocker.patch(
        "seaport.clipboard.portfile.checksums.user_path", return_value="/opt/local/bin"
    )

    distfiles = (
        "https://files.pythonhosted.org/packages/source/c/commitizen/commitizen-2.12.2.tar.gz",
        "30070",
        "96d5ebf5a5ec4e2b7190611faaaff0b87246d753d933994b29a0125a939dd682",
        "c1b78851fc66295a3f5ccda10aeeaeb65a95dd22",
    )

    # Valid port entry with no subports
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "distfiles", "commitizen"],
        stdout=[
            "--->  Distfiles for commitizen\n[commitizen-2.12.1.tar.gz] /opt/local/var/macports/distfiles/commitizen/commitizen-2.12.1.tar.gz\n rmd160: c1b78851fc66295a3f5ccda10aeeaeb65a95dd22\n sha256: 96d5ebf5a5ec4e2b7190611faaaff0b87246d753d933994b29a0125a939dd682\n size: 30070\n  https://files.pythonhosted.org/packages/source/c/commitizen/commitizen-2.12.1.tar.gz\n  http://aarnet.au.distfiles.macports.org/pub/macports/distfiles/commitizen/commitizen-2.12.1.tar.gz\n \n"
        ],
        occurrences=3,
    )

    # No subports
    assert current_checksums("commitizen", "2.12.1", "2.12.2") == (*distfiles, "")

    # Invalid entry + no subports

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "distfiles", "example"],
        stdout=["--->  Distfiles for example\n"],
        occurrences=3,
    )
    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "example"], stdout=["example things\n"]
    )

    with pytest.raises(SystemExit):
        current_checksums("example", "1.0", "2.0")

    # Subports available (subport in this scenario is commitizen)

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "example"],
        stdout=[
            "example @1.0 (devel)\nSub-ports:            example1, commitizen\n\nDescription:\n"
        ],
    )

    assert current_checksums("example", "2.12.1", "2.12.2") == (
        *distfiles,
        "commitizen",
    )

    # Single subport availble

    fake_process.register_subprocess(
        ["/opt/local/bin/port", "info", "example"],
        stdout=[
            "example @1.0 (devel)\nSub-ports:            commitizen\n\nDescription:\n"
        ],
    )

    assert current_checksums("example", "2.12.1", "2.12.2") == (
        *distfiles,
        "commitizen",
    )
