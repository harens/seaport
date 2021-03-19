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

"""Functions related to the click commands."""

from typing import Any, Callable, TypeVar, Union

import click
from beartype import beartype

from seaport._clipboard.checks import user_path
from seaport._clipboard.format import format_subprocess
from seaport._pep585_constants import LIST_TYPE, TUPLE_TYPE


@beartype
def get_names(
    ctx: Any, args: LIST_TYPE[str], incomplete: str
) -> LIST_TYPE[Union[str, TUPLE_TYPE[str, str]]]:
    """Shell autocompletion for port names.

    Examples:
        >>> from seaport._click_functions import get_names
        >>> # User has typed in py-base9
        >>> get_names("example_ctx", ["example_args"], "py-base9")
        [('py-base91', 'A Python implementation of Base91')]

    Args:
        ctx: The current command context
        args: The list of arguments passed in
        incomplete: The partial word that is being completed

    Returns:
        List[Union[str, Tuple[str, str]]]: The portname and the description
    """
    results = format_subprocess(
        [
            f"{user_path(True)}/port",
            "search",
            "--name",
            "--line",
            "--glob",
            f"{incomplete}*",
        ]
    ).splitlines()
    # Converts to raw string literal to split by backslash
    # See https://stackoverflow.com/a/25047988/10763533
    return [(repr(k).split("\\")[0][1:], repr(k).split("\\")[3][1:-1]) for k in results]


F = TypeVar("F", bound=Callable[..., None])


@beartype
def main_cmd(function: F) -> F:
    """Helps to reduce the number of duplicate decorators.

    See https://stackoverflow.com/a/50061489/10763533
    """
    function = click.argument("name", type=str, autocompletion=get_names)(function)
    function = click.option(
        "--write",
        help="Writes the updated contents to the user's portfile, similar to the original port bump.",
        is_flag=True,
    )(function)
    # Some versions could be v1.2.0-post for example
    function = click.option(
        "--bump",
        help="Manually set the version number to bump it to. By default, it uses the value outputted from the livecheck. This flag can be useful if there's no livecheck available or if you want to override it.",
        type=str,
    )(function)
    function = click.option(
        "--url",
        help="Manually set the url of where to download the new file",
        type=str,
    )(function)
    function = click.option("--test/--no-test", default=False, help="Runs port test.")(
        function
    )
    function = click.option(
        "--install/--no-install",
        default=False,
        help="Installs the port via the updated portfile and allows testing of basic functionality. After this has been completed, the port is uninstalled from the user's system.",
    )(function)
    function = click.option(
        "--lint/--no-lint", default=False, help="Runs port lint --nitpick."
    )(function)
    return function
