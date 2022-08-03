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

"""Functions related to parsing the portfile."""

import os
import sys

import click
from beartype import beartype
from beartype.typing import Tuple

from seaport._clipboard.format import format_subprocess


@beartype
def new_contents() -> Tuple[str, str, str]:
    """Determines the new contents and version number of a portfile.

    Returns:
        (str, str, str): The contents of the new portfile, version number and category
    """
    # Determine the output of the clip function from clipboard
    # Newline added since clipboard removes it
    contents = format_subprocess(["pbpaste"]) + "\n"

    if "port" not in contents.lower():
        click.secho("Cannot retrieve portfile contents from clipboard", fg="red")
        sys.exit(1)

    # Get updated version number from clip
    # Separate var to get mypy to work
    # This is since os.getenv is Optional[str]
    bump = os.getenv("BUMP")
    category = os.getenv("CATEGORY")

    if bump is None or category is None:
        click.secho("Environment variables overwritten", fg="red")
        sys.exit(1)

    return contents, bump, category
