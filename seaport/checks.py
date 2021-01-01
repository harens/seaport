"""Defensive programming functions."""

import subprocess
import sys
from pathlib import Path
from shutil import which

import click


def cmd_check(name: str) -> bool:
    """Checks whether a command is installed.

    Args:
        port: Name of the port

    Returns:
        bool: Whether the command is active
    """
    # Credit to https://stackoverflow.com/a/34177358/10763533
    return which(name) is not None


def exists(name: str) -> None:
    """Checks whether the port exists.

    Args:
        name: Name of the port
    """
    # Hide output
    if subprocess.call(
        ["port", "info", name], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    ):
        click.secho(f"❌ {name} is not a port", fg="red")
        sys.exit(1)


def preliminary_checks(port: str, pull_request: Path) -> None:
    """Checks to run before carrying out updating process.

    Args:
        port: Name of the port
        pull_request: Path of where to clone the macports-ports repo
    """
    exists(port)
    if not cmd_check("port"):
        click.secho("❌ MacPorts not installed", fg="red")
        click.echo("It can be installed from https://www.macports.org/")
        sys.exit(1)
    elif pull_request and not cmd_check("gh"):
        # gh only required if sending pr
        click.secho("❌ Github CLI not installed", fg="red")
        if not click.confirm("Do you want to install this via MacPorts?"):
            sys.exit(1)
        subprocess.run(["sudo", "port", "install", "gh"], check=True)
