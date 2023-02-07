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
from beartype import beartype
from pytest_mock import MockFixture
from pytest_subprocess import FakeProcess

from seaport._pull_request.portfile import new_contents


@beartype
def test_new_contents(fake_process: FakeProcess, session_mocker: MockFixture) -> None:
    # Capital P since PortGroup is always there
    portfile_contents = "Example Portfile contents"

    # If the new version cannot be found
    fake_process.register_subprocess(
        ["pbpaste"], stdout=[portfile_contents], occurrences=2
    )

    session_mocker.patch("os.getenv", return_value=None)

    with pytest.raises(SystemExit):
        new_contents()

    # If everything works
    session_mocker.patch("os.getenv", return_value="v1.2")

    assert new_contents() == (f"{portfile_contents}\n", "v1.2", "v1.2")

    # If the portfile contents can't be found

    fake_process.register_subprocess(["pbpaste"], stdout=["something else"])

    with pytest.raises(SystemExit):
        new_contents()
