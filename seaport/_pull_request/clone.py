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

"""Commands related to managing the clone macports-ports repo."""

import os
import subprocess

import click
from beartype import beartype
from beartype.typing import Tuple

from seaport._clipboard.checks import user_path
from seaport._clipboard.format import format_subprocess


@beartype
def sync_fork(location: str) -> None:
    """Update the cloned repo with upstream.

    Based on https://docs.github.com/en/free-pro-team@latest/github/collaborating-with-issues-and-pull-requests/syncing-a-fork

    Args:
        location: Where the macports-ports repo is located
    """
    os.chdir(f"{location}/macports-ports")
    subprocess.run([f"{user_path()}/git", "checkout", "-f", "master"], check=True)
    subprocess.run([f"{user_path()}/git", "fetch", "upstream"], check=True)
    subprocess.run([f"{user_path()}/git", "merge", "upstream/master"], check=True)
    subprocess.run([f"{user_path()}/git", "push"], check=True)


@beartype
def pr_variables() -> Tuple[str, str]:
    """Determines macOS and Xcode version numbers for pr template.

    If Xcode isn't installed, it outputs the Xcode CLT version.

    Returns:
        Tuple[str, str]: The macOS version and Xcode version
    """
    mac_version = " ".join(
        [
            format_subprocess([f"{user_path()}/sw_vers", "-productVersion"]),
            format_subprocess([f"{user_path()}/sw_vers", "-buildVersion"]),
        ]
    )

    try:
        xcode_version = format_subprocess(
            [f"{user_path()}/xcodebuild", "-version"]
        ).replace("\nBuild version", "")
    except subprocess.CalledProcessError:
        # If Xcode isn't installed
        click.secho("⏩ Using Command Line Tools instead", fg="cyan")
        xcode_version = format_subprocess([f"{user_path()}/xcode-select", "--version"])

    return mac_version, xcode_version
