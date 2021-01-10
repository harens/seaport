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

"""Defensive programming functions."""

import subprocess
import sys
from shutil import which
from typing import Optional

import click

from seaport.clipboard.format import format_subprocess


def user_path(port: bool = False, third_party: bool = False) -> str:
    """Determines the path to prevent starting a process with a partial executable path.

    Args:
        port: Whether to output the path of the port cmd
        third_party: Whether the dependency isn't installed by default

    Returns:
        A string representing the path

    Path to run system commands (e.g. git)
    See https://bandit.readthedocs.io/en/latest/plugins/b607_start_process_with_partial_path.html
    """
    # no forward slash at end for Bandit B607

    port_path = format_subprocess(["/usr/bin/which", "port"])
    port_prefix = port_path.split("bin")[0] + "bin"

    if port:
        return port_prefix

    if third_party:
        # Cannot use port_path in case not installed by MacPorts (e.g. Homebrew)
        seaport_path = format_subprocess(["/usr/bin/which", "seaport"])

        if "Python" not in seaport_path and "virtualenvs" not in seaport_path:
            # Can't run system commands from python path
            return seaport_path.split("bin")[0] + "bin"

        # Default to standard MacPorts prefix
        return port_prefix

    return "/usr/bin"


def cmd_check(name: str) -> bool:
    """Checks whether a command is installed.

    Args:
        name: Name of the port

    Returns:
        bool: Whether the command is active
    """
    # Credit to https://stackoverflow.com/a/34177358/10763533
    return which(name) is not None


def exists(name: str) -> None:
    """Checks whether the port exists.

    Args:
        name: Name of the port
    """
    # Hide output
    if subprocess.call(
        [f"{user_path(True)}/port", "info", name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    ):
        click.secho(f"❌ {name} is not a port", fg="red")
        sys.exit(1)


def preliminary_checks(port: str, pull_request: Optional[str]) -> None:
    """Checks to run before carrying out updating process.

    Args:
        port: Name of the port
        pull_request: Path of where to clone the macports-ports repo
    """
    if not cmd_check("port"):
        click.secho("❌ MacPorts not installed", fg="red")
        click.echo("It can be installed from https://www.macports.org/")
        sys.exit(1)
    elif pull_request and not cmd_check("gh"):
        # gh only required if sending pr
        click.secho("❌ Github CLI not installed", fg="red")
        if not click.confirm("Do you want to install this via MacPorts?"):
            sys.exit(1)
        subprocess.run(
            [f"{user_path()}/sudo", f"{user_path(True)}/port", "install", "gh"],
            check=True,
        )
    exists(port)
