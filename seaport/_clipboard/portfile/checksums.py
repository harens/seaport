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

"""Functions related to determining the current and new checksums."""

import hashlib
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path

import click
from beartype import beartype
from beartype.typing import Tuple
from beartype.vale import Is

from seaport._clipboard.portfile.portfile_numbers import undo_revision

# Don't count code coverage since different python versions
# won't run different parts of code
if sys.version_info >= (3, 9):  # pragma: no cover
    from typing import Annotated
else:  # pragma: no cover
    from typing_extensions import Annotated


def new_checksums(
    website: Annotated[str, Is[lambda text: text[:4] == "http"]]
) -> Tuple[str, str, str]:
    """Generate checksums of file downloaded from website.

    Args:
        website: Where to download the new file from

    Examples:
        >>> from seaport._clipboard.portfile.checksums import new_checksums
        >>> new_checksums("https://files.pythonhosted.org/packages/source/r/rich/rich-9.10.0.tar.gz")
        🔻 Downloading from https://files.pythonhosted.org/packages/source/r/rich/rich-9.10.0.tar.gz
        ('e0f2db62a52536ee32f6f584a47536465872cae2b94887cf1f080fb9eaa13eb2', '3f8be5bb8220538ed2f7953a25d829584fa3b379', '172290')
        >>> try:
        ...     new_checksums("I_don't_exist_and_so_will_fail")
        ... except SystemExit:
        ...     pass
        🔻 Downloading from I_don't_exist_and_so_will_fail
        Couldn't determine the new url. Modify the url above and use the --url flag to set it manually

    Returns:
        Tuple[str, str, str]: A tuple of strings representing the new checksums in the order sha256,
            rmd160 and size.
    """
    download_dir = tempfile.TemporaryDirectory()
    download_location = f"{download_dir.name}/download"

    # Download the file from `url` and save it locally under `file_name`:
    # Originally urllib.request.urlretrieve(website, download_location), but this is depreciated
    # Credit https://stackoverflow.com/a/7244263
    click.secho(f"🔻 Downloading from {website}", fg="cyan")
    try:
        with urllib.request.urlopen(website) as response, open(
            download_location, "wb"
        ) as out_file:
            shutil.copyfileobj(response, out_file)
    except (urllib.error.HTTPError, urllib.error.URLError, ValueError):
        click.secho(
            "Couldn't determine the new url. Modify the url above and use the --url flag to set it manually",
            fg="red",
        )
        sys.exit(1)

    size = str(Path(download_location).stat().st_size)

    with open(download_location, "rb") as file:
        data = file.read()
        sha256 = hashlib.sha256(data).hexdigest()
        rmd160 = hashlib.new("ripemd160", data).hexdigest()

    download_dir.cleanup()

    return sha256, rmd160, size


@beartype
def replace_checksums(
    file_contents: str,
    old_sums: Tuple[str, str, str, str],
    new_sums: Tuple[str, str, str, str],
) -> str:
    """Replaces the old checksums with the new ones.

    Args:
        file_contents: The old contents of the file
        old_sums: The old checksums that are in file_contents
        new_sums: The new checksums that will replace the old ones

    Examples:
        >>> from seaport._clipboard.portfile.checksums import replace_checksums
        >>> replace_checksums(
        ... "replace this oldrmd, oldsha, oldsize and oldversion with new ones please",
        ... ("oldrmd", "oldsha", "oldsize", "oldversion"),
        ... ("newrmd", "newsha", "newsize", "newversion"),
        ... )
        ⏪️ Changing revision numbers
        No changes necessary
        'replace this newrmd, newsha, newsize and newversion with new ones please'

    Returns:
        A string representing the portfile contents with the new checksums
    """
    # Bump revision numbers to 0
    new_contents: str = undo_revision(file_contents)

    # Replace first instances only
    # Iterate over Checksums and version number
    for i in range(4):
        new_contents = new_contents.replace(old_sums[i], new_sums[i], 1)

    return new_contents
