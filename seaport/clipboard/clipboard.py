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

"""The main CLI function, which the user runs."""

import os
import subprocess
import sys
import tempfile
from typing import Optional

import click

from seaport.click_functions import main_cmd
from seaport.clipboard.additional import perform_install, perform_lint, perform_test
from seaport.clipboard.checks import preliminary_checks, user_path
from seaport.clipboard.format import format_subprocess
from seaport.clipboard.portfile.checksums import (
    current_checksums,
    new_checksums,
    replace_checksums,
)
from seaport.clipboard.portfile.portfile_numbers import new_version
from seaport.clipboard.user import clean, user_clipboard


@click.command()
@main_cmd
# Some parameters are not used
# They are only here since the pr function sends them
def clip(
    name: str,
    bump: str,
    test: bool,
    lint: bool,
    install: bool,
    location: Optional[str] = None,
    new: bool = False,
) -> None:
    """Bumps the version number and checksum of NAME.

    It then copies the result to your clipboard.
    """
    # Tasks that require sudo
    sudo = test or lint or install

    preliminary_checks(name, location)

    current_version = format_subprocess(
        [f"{user_path(True)}/port", "info", "--version", name]
    ).split(" ")[1]

    # Determine new version
    bump = new_version(name, bump, current_version, new)

    click.secho(f"👍 New version is {bump}", fg="green")

    # Allows pr function to get the version number
    os.environ["BUMP"] = bump

    # Where to download the new file + old checksums
    new_website, old_size, old_sha256, old_rmd160, subport = current_checksums(
        name, current_version, bump
    )

    new_sha256, new_rmd160, new_size = new_checksums(new_website)

    click.secho("🔎 Checksums:", fg="cyan")
    click.echo(f"Old rmd160: {old_rmd160}")
    click.echo(f"New rmd160: {new_rmd160}")
    click.echo(f"Old sha256: {old_sha256}")
    click.echo(f"New sha256: {new_sha256}")
    click.echo(f"Old size: {old_size}")
    click.echo(f"New size: {new_size}")

    # Add the new checksums, and take a backup of the original
    file_location = (
        subprocess.check_output([f"{user_path(True)}/port", "file", name])
        .decode("utf-8")
        .strip()
    )

    with click.open_file(file_location) as file:
        # Backup of the original contents
        original = file.read()

    new_contents = replace_checksums(
        original,
        (old_sha256, old_rmd160, old_size, current_version),
        (new_sha256, new_rmd160, new_size, bump),
    )

    if sudo:

        # Temporary files created to get around sudo write problem
        tmp_version = tempfile.NamedTemporaryFile(mode="w")
        tmp_version.write(new_contents)
        tmp_version.seek(0)

        click.secho("💾 Editing local portfile repo, sudo required", fg="cyan")
        click.echo("Changes will be reverted after completion")
        subprocess.run(
            [f"{user_path()}/sudo", "cp", tmp_version.name, file_location], check=True
        )

        if test:
            # If the tests fail
            if not perform_test(name, subport):
                clean(original, file_location, name)
                sys.exit(1)
        if lint:
            # If the lint is not successful
            if not perform_lint(name):
                clean(original, file_location, name)
                sys.exit(1)

        if install:
            perform_install(name)

        clean(original, file_location, name)

    # Clipboard functions at the very end
    # to reduce the chance of user's clipboard being changed
    # after adding contents
    user_clipboard(new_contents)
