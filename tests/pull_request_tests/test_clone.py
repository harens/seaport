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

import subprocess

from beartype import beartype
from pytest_mock import MockFixture
from pytest_subprocess import FakeProcess
from pytest_subprocess.core import FakePopen

from seaport._pull_request.clone import pr_variables, sync_fork


@beartype
def test_new_contents(fake_process: FakeProcess, session_mocker: MockFixture) -> None:
    # There's not really much to test here
    # TODO: Properly test this

    # default path
    session_mocker.patch(
        "seaport._pull_request.clone.user_path", return_value="/some/path"
    )

    session_mocker.patch("os.chdir", return_value=None)

    fake_process.register_subprocess(
        ["/some/path/git", "fetch", "upstream"],
        stdout=["Fetching upstream\n"],
    )

    fake_process.register_subprocess(
        ["/some/path/git", "checkout", "-f", "master"],
        stdout=["Checking out\n"],
    )

    fake_process.register_subprocess(
        ["/some/path/git", "merge", "upstream/master"],
        stdout=["Merging\n"],
    )

    fake_process.register_subprocess(
        ["/some/path/git", "push"],
        stdout=["Pushing\n"],
    )

    sync_fork("~/Desktop")


@beartype
def callback_info(process: FakePopen) -> None:
    """`xcodebuild` output if xcode isn't installed"""
    process.returncode = 1
    raise subprocess.CalledProcessError(1, cmd="xcodebuild -version")


@beartype
def test_pr_variables(fake_process: FakeProcess, session_mocker: MockFixture) -> None:
    # default path
    session_mocker.patch(
        "seaport._pull_request.clone.user_path", return_value="/some/path"
    )

    # If everything works

    fake_process.register_subprocess(
        ["/some/path/sw_vers", "-productVersion"], stdout=["10.15.6\n"], occurrences=2
    )

    fake_process.register_subprocess(
        ["/some/path/sw_vers", "-buildVersion"], stdout=["19G73\n"], occurrences=2
    )

    fake_process.register_subprocess(
        ["/some/path/xcodebuild", "-version"],
        stdout=["Xcode 12.3\nBuild version 12C33\n"],
    )

    assert pr_variables() == ("10.15.6 19G73", "Xcode 12.3 12C33")

    # If Xcode isn't installed

    fake_process.register_subprocess(
        ["/some/path/xcodebuild", "-version"],
        callback=callback_info,
    )

    fake_process.register_subprocess(
        ["/some/path/xcode-select", "--version"],
        stdout=["xcode-select version 2373.\n"],
    )

    assert pr_variables() == ("10.15.6 19G73", "xcode-select version 2373.")
