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

"""Additional checks that aren't provided by default.

e.g. Linting
"""

import subprocess
from typing import Optional

import click
from beartype import beartype

from seaport._clipboard.checks import user_path
from seaport._clipboard.format import format_subprocess


@beartype
def perform_lint(name: str) -> bool:
    """Lints the port and checks output for errors.

    Args:
        name: The name of the port

    Returns:
        bool: Whether the linting was successful or not
    """
    click.secho("🤔 Linting", fg="cyan")
    lint_output = format_subprocess(
        [f"{user_path(True)}/port", "lint", "--nitpick", name]
    )
    click.echo(lint_output)
    output_list = lint_output.split(" ")

    # Finds the no. of errors and warnings
    errors = int(output_list[output_list.index("errors") - 1])
    warnings = int(output_list[output_list.index("warnings") - 1])

    if errors > 1:
        # Fail if there are any errors
        return False
    if warnings > 1:
        # Ask whether the user wishes to continue
        if not click.confirm(
            f"There are {warnings} warnings. Do you wish to continue?"
        ):
            return False
    return True


@beartype
def perform_test(name: str, subport: Optional[str] = None) -> bool:
    """Tests the port and checks output for errors.

    Args:
        name: The name of the port
        subport: The name of one of the subports

    Returns:
        bool: Whether the tet was successful or not
    """
    click.secho(f"🧪 Testing {name}", fg="cyan")
    try:
        subprocess.run(
            [f"{user_path()}/sudo", f"{user_path(True)}/port", "test", name],
            check=True,
        )
    except subprocess.CalledProcessError:
        # For python ports, the tests are in the subport
        # There are no tests in the original port
        if subport:
            click.secho(f"🏗 Trying with subport {subport}", fg="cyan")
            try:
                subprocess.run(
                    [f"{user_path()}/sudo", f"{user_path(True)}/port", "test", subport],
                    check=True,
                )
            except subprocess.CalledProcessError:
                click.secho("❌ Tests failed", fg="red")
                return False
        else:
            click.secho("❌ Tests failed", fg="red")
            return False
    click.secho("✅ Tests passed", fg="green")
    return True


@beartype
def perform_install(name: str) -> None:
    """Runs sudo port -vst install NAME.

    Args:
        name: The name of the port
    """
    click.secho(f"🏗️ Installing {name}", fg="cyan")
    subprocess.run(
        [
            f"{user_path()}/sudo",
            f"{user_path(True)}/port",
            "-vst",
            "install",
            name,
        ],
        check=True,
    )
    click.secho(
        "Paused to allow user to test basic functionality in a different terminal",
        fg="cyan",
    )
    if click.confirm("Do you want to uninstall the port?"):
        click.secho(f"🗑  Uninstalling {name}", fg="cyan")
        subprocess.run(
            [f"{user_path()}/sudo", f"{user_path(True)}/port", "uninstall", name],
            check=True,
        )
