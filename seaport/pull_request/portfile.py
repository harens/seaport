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
from typing import Tuple

import click

from seaport.clipboard.checks import user_path
from seaport.clipboard.format import format_subprocess


def new_contents() -> Tuple[str, str]:
    """Determines the new contents and version number of a portfile.

    Returns:
        (str, str): The contents of the new portfile and the new version number
    """
    # Determine the output of the clip function from clipboard
    # Newline added since clipboard removes it
    contents = format_subprocess(["pbpaste"]) + "\n"

    if "port" not in contents:
        click.secho("Cannot retrieve portfile contents from clipboard", fg="red")
        sys.exit(1)

    # Get updated version number from clip
    # Separate var to get mypy to work
    # This is since os.getenv is Optional[str]
    env_variable = os.getenv("BUMP")

    if env_variable is None:
        click.secho(
            "Cannot determine version number from env variable `bump`", fg="red"
        )
        sys.exit(1)

    return contents, env_variable


def determine_category(name: str) -> str:
    """Given the name of a port, output the category.

    Args:
        name: The name of the port

    Returns:
        str: The category of the port
    """
    # Category determined so as to know where to put the portfile
    # e.g. macports-ports/category/name/Portfile
    category_list = format_subprocess(
        [f"{user_path(True)}/port", "info", "--category", name]
    ).split(" ")

    # Remove comma, and only take the first category
    return category_list[1][:-1] if len(category_list) > 2 else category_list[1]
