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

"""Functions for modifying the user's system, such as the _clipboard."""

import subprocess
import tempfile

import click
from beartype import beartype

from seaport._clipboard.checks import user_path


@beartype
def clean(
    original_text: str, location: str, port_name: str, write: bool = False
) -> None:
    """Returns the user's local portfile repo to the original state.

    Args:
        original_text: What the contents of the portfile originally was
        location: Where the portfile is located
        port_name: The name of the portfile
        write: Whether to keep the updated portfile contents

    """
    click.secho("🧽 Cleanup", fg="cyan")

    # Only revert the portfile contents if the user doesn't use --write
    if not write:
        # Change contents of local portfile back to original
        tmp_original = tempfile.NamedTemporaryFile(mode="w")
        tmp_original.write(original_text)
        tmp_original.seek(0)
        subprocess.run(
            [f"{user_path()}/sudo", "cp", tmp_original.name, location], check=True
        )
        tmp_original.close()

    subprocess.run(
        [f"{user_path()}/sudo", f"{user_path(True)}/port", "clean", "--all", port_name],
        check=True,
    )


@beartype
def user_clipboard(new_contents: str) -> None:
    """Copies the new contents of the portfile to the _clipboard.

    Examples:
        >>> from seaport._clipboard.user import user_clipboard
        >>> from seaport._clipboard.format import format_subprocess
        >>> user_clipboard("hello there")
        📋 The contents of the portfile have been copied to your clipboard!
        >>> format_subprocess(["pbpaste"])
        'hello there'

    Args:
        new_contents: What to copy the clipboard
    """
    subprocess.run(
        f"{user_path()}/pbcopy",
        universal_newlines=True,
        input=new_contents,
        check=True,
    )

    click.secho(
        "📋 The contents of the portfile have been copied to your clipboard!",
        fg="cyan",
    )
