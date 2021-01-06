"""Functions related to bumping revision and version numbers of a portfile."""

import re
import sys

import click

from seaport.checks import user_path
from seaport.format import format_subprocess


def undo_revision(text: str) -> str:
    """Make version numbers 0.

    Args:
        text: The text of the portfile

    Returns:
        str: The text with version numbers decremented to 0

    """
    click.secho("⏪️ Changing revision numbers", fg="cyan")

    # Counts no. of revision numbers greater than 0
    # Assumes revision number doesn't exceed 9
    need_changed = len(re.findall(r"revision\s*[1-9]", text))
    total = len(re.findall(r"revision\s*", text))

    # If there are no revisions greater than 1, do nothing
    if need_changed == 0:
        click.echo("No changes necessary")
        return text
    # If there are multiple revision numbers, we don't know which one to change
    # If all of the revision numbers are 0, this is accounted for in the last if statement
    if total > 1:
        click.secho(
            "Multiple revision numbers found. Unsure which to reduce to 0", fg="red"
        )
        sys.exit(1)

    # Implies need_changed == 1

    # Takes the original revision as a string
    # We know original_revision will not be of type none (hence mypy ignore)
    # This is ince need_changed is equal to 1
    original_revision = re.search(r"revision\s*[1-9]", text).group(0)  # type: ignore
    # Replaces the number with 0
    new_revision = original_revision[:-1] + "0"
    click.echo("Revision number changed")
    return text.replace(original_revision, new_revision)


def new_version(port: str, stated: str, current: str) -> str:
    """Determines livecheck version, and sees whether already up-to-date.

    Args:
        port: The name of the port
        stated: The user's new version via --bump
        current: The current version of the port

    Returns:
        str: The version number following checks

    """
    # Determines new version number if none manually specified
    if not stated:
        # Take the last word of port livecheck, and then remove the bracket
        stated = format_subprocess(
            [f"{user_path(True)}/port", "livecheck", port]
        ).split(" ")[-1][:-1]

        # version == "" if livecheck doesn't output anything
        # current_version used in output since version = ""
        if stated == "":
            click.secho(
                f"{port}'s either already up-to-date ({current}) or there's no livecheck available",
                fg="red",
            )
            click.secho("Please manually specify the version using --bump", fg="red")
            sys.exit(1)

    if stated == current:
        click.secho(f"{port} is already up-to-date ({current})", fg="red")
        sys.exit(1)

    # Credit to @herbygillot
    # See https://github.com/macports/macports-ports/pull/9589#issuecomment-753309298
    # alpha/beta/rc version detected on a port that isn't -devel
    devel_versions = ["alpha", "beta", "rc", "devel", "dev", "unstable"]
    if "-devel" not in port and any(item in stated for item in devel_versions):
        if not click.confirm(
            f"{port} is not a devel port, but the new version ({stated}) is a devel build. Do you wish to continue?"
        ):
            click.echo("You can specify a different version using --bump")
            sys.exit(1)

    return stated
