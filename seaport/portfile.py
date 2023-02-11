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

"""Python API for MacPorts portfiles."""

import re
import subprocess
import sys
from typing import Optional

from beartype import beartype
from beartype.typing import List, Tuple

from seaport._clipboard.format import format_subprocess

# Don't count code coverage since different python versions
# won't run different parts of code
if sys.version_info >= (3, 8):  # pragma: no cover
    from beartype.typing import Final
else:  # pragma: no cover
    from typing_extensions import Final


# TODO: Set no output (especially for errors)
class Port:
    """Scrapes portfile info for usage in Python modules.

    Examples:
        >>> from seaport.portfile import Port
        >>> port = Port("py-base91")
        >>> port.version
        '1.0.1'

        >>> from seaport.portfile import Port
        >>> port = Port("py-base91")
        >>> port.revision
        0

        >>> from seaport.portfile import Port
        >>> try:
        ...     port = Port("non-existent-port")
        ... except Exception:
        ...     pass
        >>> # This raises an exception

    Attributes:
        name (str): The name of the port e.g. gping
    """

    @beartype
    def __init__(self, name: str) -> None:
        """Set optional attributes and check if port exists."""
        # TODO: Figure out how to find path without subprocess
        # TODO: Refactor this
        # TODO: This also kind of defeats the purpose of that bandit error, so find a better way to determine the path
        # no forward slash at end for Bandit B607
        self.name: Final[str] = name
        self._path: Final[str] = format_subprocess(["/usr/bin/which", "port"]).replace(
            "/port", ""
        )

        try:
            self._info: Final[str] = format_subprocess(
                [f"{self._path}/port", "info", self.name]
            )
        except subprocess.CalledProcessError:
            # TODO: Set a more specific exception
            raise Exception(f"{self.name} doesn't exist, run portindex if port is new")

        self._parsedInfo: Final[List[str]] = self._info[
            self._info.find("@") + 1 :
        ].split()
        versionParse: Final[List[str]] = self._parsedInfo[0].split("_")

        # Parse saved port info, falling back to calling the explicit function
        # As a quick sanity check, see that the first digit of the version number is indeed a digit

        self.version: Final[str] = (
            format_subprocess(
                [f"{self._path}/port", "info", "--version", self.name]
            ).split(" ")[1]
            if len(versionParse) not in (1, 2) or not versionParse[0][0].isdigit()
            else versionParse[0]
        )

        self.revision: Final[int] = (
            int(
                format_subprocess(
                    [f"{self._path}/port", "info", "--revision", self.name]
                ).split(" ")[1]
            )
            if len(versionParse) not in (1, 2) or not versionParse[0][0].isdigit()
            else 0
            if len(versionParse) == 1
            else int(versionParse[1])
        )

    @beartype
    def __str__(self) -> str:
        """Outputs the name and version of the port.

        Examples:
            >>> from seaport.portfile import Port
            >>> print(Port("py-base91"))
            py-base91 1.0.1
        """
        return f"{self.name} {self.version}"

    @beartype
    def __repr__(self) -> str:
        """Outputs the attributes that a port was defined with.

        Examples:
            >>> from seaport.portfile import Port
            >>> Port("py-base91")
            Port(name=py-base91)
        """
        return f"Port(name={self.name})"

    # TODO: These livecheck tests will fail when I least expect it
    @beartype
    def livecheck(self) -> str:
        """Runs port livecheck to check for any new versions.

        If no livecheck is available or the portfile is already the latest version, the current version is outputted.
        Note that this can be slow, since it's scraping `port livecheck`.

        Examples:
            >>> from seaport.portfile import Port
            >>> port = Port("py-base91")
            >>> port.livecheck()
            '1.0.1'

            >>> from seaport.portfile import Port
            >>> port = Port("py39-base91")
            >>> port.livecheck()
            '1.0.1'

        Returns:
            A string representing the latest version.
        """
        # Take the last word of port livecheck, and then remove the bracket
        update = format_subprocess(
            [f"{self._path}/port", "livecheck", self.name]
        ).split(" ")[-1][:-1]

        # If there's no livecheck output, fallback to subport
        # Convoluted if statement to make mypy happy
        if update == "":
            # Makes mypy happy since a function could theoretically change to be None
            subports = self.subports()
            if subports is not None:
                update = format_subprocess(
                    [f"{self._path}/port", "livecheck", subports[-1]]
                ).split(" ")[-1][:-1]

        # If there's no livecheck output again, fallback to current version
        # Implies no livecheck available or already up-to-date
        # N.B. str is required for py 3.7 type checking
        return update if update != "" else str(self.version)

    @beartype
    def subports(self) -> Optional[List[str]]:
        """Determines a list of subports of a port.

        If there are no subports available, None is outputted.

        Examples:
            >>> # Subports available
            >>> from seaport.portfile import Port
            >>> port = Port("py-base91")
            >>> port.subports()
            ['py38-base91', 'py39-base91']

            >>> # Subports not available
            >>> from seaport.portfile import Port
            >>> port = Port("folderify")
            >>> print(port.subports())
            None

        Returns:
            A list representing all the subports of the port.
        """
        # Split subport section by colon and comma
        # This needs to be made more efficient
        # TODO: Refactor so that as soon as a line containing sub-ports is found, don't bother
        # with other iterations in for list comprehension
        return (
            None
            if "Sub-ports" not in self._info
            else [
                i.replace(" ", "")
                for i in re.split(
                    "[:,]",
                    " ".join([s for s in self._info.splitlines() if "Sub-ports" in s]),
                )
                if i != "Sub-ports"
            ]
        )

    @beartype
    def checksums(self, _name: Optional[str] = None) -> Tuple[str, str, str, str]:
        """Determines the current checksums of a portfile.

        For python ports, their pyXY- subport is used to determine the checksums.
        Note that this method only works for ports with the standard rmd/sha/size setup (not the older format), and it can also be
        quite slow since it's scraping `port distfiles NAME`

        Examples:
            >>> # Determines rmd160/sha256/size/website
            >>> from seaport.portfile import Port
            >>> port = Port("py-base91")
            >>> port.checksums()
            ('c1bd97759a8d7bfdb95cd76ada05efa9e9d99f28', '5b284a2ba3c97be1eb9473f3af94a9bf141d61005d836e75e645d2798da58799', '2331', 'https://files.pythonhosted.org/packages/source/b/base91/base91-1.0.1.tar.gz')


        Returns:
            rmd160, sha256, size and the website that provided the distfile.
        """
        # Name is used if recursion required for subports
        _name = self.name if _name is None else _name
        distfiles = (
            format_subprocess([f"{self._path}/port", "distfiles", _name])
            .replace("\n ", "")
            .split(" ")
        )
        try:
            # We're only interested in the first result
            # Credit to https://stackoverflow.com/a/9868665/10763533
            website: Final[str] = next(
                s for s in distfiles if "http://" in s or "https://" in s
            )
        except StopIteration:
            # Tries to determine the subport
            # This is since the distfiles cmd only works for subports
            subports = self.subports()
            if subports is None:
                raise Exception(f"port distfiles {_name} provides no output")
            # Repeat the process with the subport
            return self.checksums(subports[-1])

        website_index: Final[int] = distfiles.index(website)

        # rmd, sha, size, download website
        # TODO: This will not work for the old format
        return (
            distfiles[website_index - 3][:-7],
            distfiles[website_index - 2][:-5],
            distfiles[website_index - 1],
            website,
        )

    @beartype
    def primary_category(self) -> str:
        """Determines the first category of a port.

        This is useful to determine which folder of the macports repo the port would reside in.

        Examples:
            >>> from seaport.portfile import Port
            >>> port = Port("gping")
            >>> port.primary_category()
            'net'

        Returns:
            The category of the port e.g. sysutils.
        """
        # Remove leftmost bracket and rightmost comma (if multiple categories) or bracket (if only one)
        if self._parsedInfo[1][0] != "(" or self._parsedInfo[1][-1] not in (
            ")",
            ",",
        ):
            category_list: Final[List[str]] = format_subprocess(
                [f"{self._path}/port", "info", "--category", self.name]
            ).split(" ")
            # Remove comma, and only take the first category
            # N.B. str seems to be required for py37 type checking
            return (
                str(category_list[1][:-1])
                if len(category_list) > 2
                else str(category_list[1])
            )
        else:
            # N.B. str is required for python type checking
            return str(self._parsedInfo[1][1:-1])
