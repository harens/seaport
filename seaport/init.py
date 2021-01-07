"""The main cli module (a facade for the other commands)."""

import click

from seaport import __version__
from seaport.commands.clipboard import clip
from seaport.commands.pull_request import pr


@click.group()
@click.version_option(__version__)
def seaport() -> None:
    """Bumps the version number and checksum of a port.

    For more information, please visit https://github.com/harens/seaport
    """
    click.secho("🌊 Starting seaport...", fg="cyan")


seaport.add_command(clip)
seaport.add_command(pr)
