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
