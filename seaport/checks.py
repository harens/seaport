"""Defensive programming functions."""

import subprocess
import sys
from shutil import which
from typing import Optional

import click

from seaport.format import format_subprocess


def user_path(port: bool = False, third_party: bool = False) -> str:
    """Determines the path to prevent starting a process with a partial executable path.

    Args:
        port: Whether to output the path of the port cmd
        third_party: Whether the dependency isn't installed by default

    Returns:
        A string representing the path

    Path to run system commands (e.g. git)
    See https://bandit.readthedocs.io/en/latest/plugins/b607_start_process_with_partial_path.html
    """
    # no forward slash at end for Bandit B607

    port_path = format_subprocess(["/usr/bin/which", "port"])
    port_prefix = port_path.split("bin")[0] + "bin"

    if port:
        return port_prefix

    if third_party:
        # Cannot use port_path in case not installed by MacPorts (e.g. Homebrew)
        seaport_path = format_subprocess(["/usr/bin/which", "seaport"])

        if "Python" not in seaport_path and "virtualenvs" not in seaport_path:
            # Can't run system commands from python path
            return seaport_path.split("bin")[0] + "bin"

        # Default to standard MacPorts prefix
        return port_prefix

    return "/usr/bin"


def cmd_check(name: str) -> bool:
    """Checks whether a command is installed.

    Args:
        name: Name of the port

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
        [f"{user_path(True)}/port", "info", name],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    ):
        click.secho(f"❌ {name} is not a port", fg="red")
        sys.exit(1)


def preliminary_checks(port: str, pull_request: Optional[str]) -> None:
    """Checks to run before carrying out updating process.

    Args:
        port: Name of the port
        pull_request: Path of where to clone the macports-ports repo
    """
    if not cmd_check("port"):
        click.secho("❌ MacPorts not installed", fg="red")
        click.echo("It can be installed from https://www.macports.org/")
        sys.exit(1)
    elif pull_request and not cmd_check("gh"):
        # gh only required if sending pr
        click.secho("❌ Github CLI not installed", fg="red")
        if not click.confirm("Do you want to install this via MacPorts?"):
            sys.exit(1)
        subprocess.run(
            [f"{user_path()}/sudo", f"{user_path(True)}/port", "install", "gh"],
            check=True,
        )
    exists(port)
