"""Functions related to determining the current and new checksums."""

import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Tuple

import click

from seaport.checks import user_path
from seaport.format import format_subprocess


def new_checksums(website: str) -> Tuple[str, str, str]:
    """Generate checksums of file downloaded from website.

    Args:
        website: Where to download the new file from

    Returns:
        Tuple[str, str, str]: A tuple of strings representing the new checksums
    """
    download_dir = tempfile.TemporaryDirectory()
    download_location = f"{download_dir.name}/download"

    # Download the file from `url` and save it locally under `file_name`:
    # Originally urllib.request.urlretrieve(website, download_location), but this is depreciated
    # Credit https://stackoverflow.com/a/7244263
    with urllib.request.urlopen(website) as response, open(
        download_location, "wb"
    ) as out_file:
        shutil.copyfileobj(response, out_file)

    # sha256 flag added even though it's the default
    # Otherwise sometimes doesn't return sha256
    sha256 = format_subprocess(
        [f"{user_path()}/openssl", "dgst", "-sha256", download_location]
    ).split(" ")[-1]
    rmd160 = format_subprocess(
        [f"{user_path()}/openssl", "dgst", "-rmd160", download_location]
    ).split(" ")[-1]
    size = str(Path(download_location).stat().st_size)

    download_dir.cleanup()

    return sha256, rmd160, size


def current_checksums(port: str, current: str, new: str) -> Tuple[str, str, str, str]:
    """Returns outdated checksums and the website to download the new files from.

    Args:
        port: Name of the port
        current: The current and outdated version number
        new: The new version number

    Returns:
        Tuple[str, str, str, str]: A tuple of strings representing the new website and checksums
    """
    distfiles = (
        format_subprocess([f"{user_path(True)}/port", "distfiles", port])
        .replace("\n ", "")
        .split(" ")
    )

    # There's no output if it's the "skeleton" head port
    try:
        old_website = [s for s in distfiles if "http" in s][0]
    except IndexError:
        # Tries to determine the subport
        # This is since the distfiles cmd only works for subports
        port_info = format_subprocess([f"{user_path(True)}/port", "info", port])
        if "Sub-ports" not in port_info:
            click.secho("Cannot determine distfiles", fg="red")
            sys.exit(1)
        # Takes the last subport of the list
        subport = " ".join(
            [s for s in port_info.splitlines() if "Sub-ports" in s]
        ).split(" ")[-1]
        # Repeat the process with the subport
        return current_checksums(subport, current, new)

    new_website = old_website.replace(current, new)

    website_index = distfiles.index(old_website)

    # This won't work for older portfiles (e.g. if they used md5 and sha1 for example)
    size = distfiles[website_index - 1]
    sha256 = distfiles[website_index - 2][:-5]  # Remove size:
    rmd160 = distfiles[website_index - 3][:-7]  # Remove sha256:

    return new_website, size, sha256, rmd160
