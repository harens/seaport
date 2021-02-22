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

from pytest_mock import MockFixture

from seaport._clipboard.user import clean


def test_clean(fake_process, session_mocker: MockFixture, capfd) -> None:
    # Set default path
    # Don't use /opt/local since sudo is also patched
    session_mocker.patch("seaport._clipboard.user.user_path", return_value="/some/path")

    # Credit https://stackoverflow.com/a/58310550/10763533
    # Set the tempfile name
    session_mocker.patch(
        "seaport._clipboard.user.tempfile.NamedTemporaryFile"
    ).return_value.name = "tempfilename"

    fake_process.register_subprocess(
        ["/some/path/sudo", "cp", "tempfilename", "somewhere"], stdout=["Copied\n"]
    )

    fake_process.register_subprocess(
        ["/some/path/sudo", "/some/path/port", "clean", "--all", "portname"],
        stdout=["Cleaned\n"],
        occurrences=2,
    )

    clean("original contents", "somewhere", "portname")
    out, err = capfd.readouterr()

    assert out == "🧽 Cleanup\n"
    assert not err

    # If writing to local portfile (basically only do the port clean)
    clean("original contents", "somewhere", "portname", True)
