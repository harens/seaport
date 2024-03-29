#!/usr/bin/env python3

# Copyright (c) 2023, harens
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

import sys
from typing import Any, Callable, Optional, TypeVar

from beartype import beartype

from seaport._clipboard.format import format_subprocess

# Don't count code coverage since different python versions
# won't run different parts of code
if "pytest" in sys.modules:  # pragma: no cover
    # Caching the result breaks tests, so disable caching during testing.

    F = TypeVar("F", bound=Callable[..., Any])

    @beartype
    def cache(func: F) -> F:
        """A decorator that does nothing."""
        return func

elif sys.version_info >= (3, 9):  # pragma: no cover
    from functools import cache
else:  # pragma: no cover
    from functools import lru_cache

    # mypy complains due to the type signature of cache for pytest
    cache = lru_cache(maxsize=None)  # type: ignore[assignment]

# TODO: This will need major refactoring (it's a mess)
# It also kind of defeats the purpose of the bandit error it's meant to solve
# TODO: This test will fail if non-default macports path is used


@cache
@beartype
def user_path(
    port: bool = False, third_party: bool = False, manual: Optional[str] = None
) -> str:
    """Determines the bin path to prevent starting a process with a partial executable path.

    Examples:
        >>> from seaport._clipboard.checks import user_path
        >>> # If it's a port command (e.g. port lint)
        >>> user_path(True)
        '/opt/local/bin'
        >>> # If it's a standard system command
        >>> user_path()
        '/usr/bin'
        >>> # Manually chose a custom path
        >>> user_path(manual="/custom/path/bin/exe")
        '/custom/path/bin'

    Args:
        port: Whether to output the path of the port cmd
        third_party: Whether the dependency isn't installed by default
        manual: Manually select the path to return

    Returns:
        A string representing the path

    Path to run system commands (e.g. git)
    See https://bandit.readthedocs.io/en/latest/plugins/b607_start_process_with_partial_path.html
    """
    # no forward slash at end for Bandit B607

    if manual:
        return manual.split("bin")[0] + "bin"

    # TODO: Run a small check to be certain that this port is the right port
    port_path = format_subprocess(["/usr/bin/which", "port"])
    port_prefix = port_path.split("bin")[0] + "bin"

    if port:
        return port_prefix

    if third_party:
        # Cannot use port_path in case not installed by MacPorts (e.g. Homebrew)
        # TODO: Run a small check to be certain that this is the right seaport
        seaport_path = format_subprocess(["/usr/bin/which", "seaport"])

        if "Python" not in seaport_path and "virtualenvs" not in seaport_path:
            # Can't run system commands from python path
            return seaport_path.split("bin")[0] + "bin"

        # Default to standard MacPorts prefix
        return port_prefix

    return "/usr/bin"
