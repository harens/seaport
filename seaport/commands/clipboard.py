"""The main CLI function, which the user runs."""

import os
import subprocess
import sys
import tempfile
from typing import Optional

import click

from seaport.additional import perform_lint
from seaport.checks import preliminary_checks, user_path
from seaport.clean import clean
from seaport.commands.autocomplete import get_names
from seaport.format import format_subprocess
from seaport.portfile.checksums import current_checksums, new_checksums
from seaport.portfile.portfile_numbers import new_version, undo_revision


@click.command()
@click.argument("name", type=str, autocompletion=get_names)
# Some versions could be v1.2.0-post for example
@click.option("--bump", help="The new version number", type=str)
@click.option("--test/--no-test", default=False, help="Runs port test")
@click.option("--lint/--no-lint", default=False, help="Runs port lint --nitpick")
@click.option(
    "--install/--no-install",
    default=False,
    help="Installs the port and allows testing of basic functionality",
)
# Some parameters are not used
# They are only here since the pr function sends them
def clip(
    name: str,
    bump: str,
    test: bool,
    lint: bool,
    install: bool,
    location: Optional[str] = None,
    new: Optional[bool] = None,
) -> None:
    """Bumps the version number and checksum of NAME, and copies the result to your clipboard."""
    # Tasks that require sudo
    sudo = test or lint or install

    preliminary_checks(name, location)

    current_version = format_subprocess(
        [f"{user_path(True)}/port", "info", "--version", name]
    ).split(" ")[1]

    # Determine new version
    bump = new_version(name, bump, current_version)

    click.secho(f"👍 New version is {bump}", fg="green")

    # Allows pr function to get the version number
    os.environ["BUMP"] = bump

    # Where to download the new file + old checksums
    new_website, old_size, old_sha256, old_rmd160 = current_checksums(
        name, current_version, bump
    )

    click.secho(f"🔻 Downloading from {new_website}", fg="cyan")
    new_sha256, new_rmd160, new_size = new_checksums(new_website)

    click.secho("🔎 Checksums:", fg="cyan")
    click.echo(f"Old rmd160: {old_rmd160}")
    click.echo(f"New rmd160: {new_rmd160}")
    click.echo(f"Old sha256: {old_sha256}")
    click.echo(f"New sha256: {new_sha256}")
    click.echo(f"Old size: {old_size}")
    click.echo(f"New size: {new_size}")

    # Add the new checksums, and take a backup of the original
    file_location = (
        subprocess.check_output([f"{user_path(True)}/port", "file", name])
        .decode("utf-8")
        .strip()
    )

    with click.open_file(file_location) as file:
        # Backup of the original contents
        original = file.read()

    # Bump revision numbers to 0
    new_contents = undo_revision(original)

    # Replace first instances only
    new_contents = new_contents.replace(current_version, bump, 1)
    new_contents = new_contents.replace(old_sha256, new_sha256, 1)
    new_contents = new_contents.replace(old_rmd160, new_rmd160, 1)
    new_contents = new_contents.replace(old_size, new_size, 1)

    if sudo:

        # Temporary files created to get around sudo write problem
        tmp_version = tempfile.NamedTemporaryFile(mode="w")
        tmp_version.write(new_contents)
        tmp_version.seek(0)

        click.secho("💾 Editing local portfile repo, sudo required", fg="cyan")
        click.echo("Changes will be reverted after completion")
        subprocess.run(
            [f"{user_path()}/sudo", "cp", tmp_version.name, file_location], check=True
        )

        if test:
            click.secho(f"🧪 Testing {name}", fg="cyan")
            subprocess.run(
                [f"{user_path()}/sudo", f"{user_path(True)}/port", "test", name],
                check=True,
            )
        if lint:
            # If the lint is not successful
            if not perform_lint(name):
                clean(original, file_location, name)
                sys.exit(1)

        if install:
            click.secho(f"🏗️ Installing {name}", fg="cyan")
            subprocess.run(
                [
                    f"{user_path()}/sudo",
                    f"{user_path(True)}/port",
                    "-vst",
                    "install",
                    name,
                ],
                check=True,
            )
            click.secho(
                "Paused to allow user to test basic functionality in a different terminal",
                fg="cyan",
            )
            click.pause("Press any key to continue ")
            click.secho(f"🗑 Uninstalling {name}", fg="cyan")
            subprocess.run(
                [f"{user_path()}/sudo", f"{user_path(True)}/port", "uninstall", name],
                check=True,
            )

        clean(original, file_location, name)

        subprocess.run(
            f"{user_path()}/pbcopy",
            universal_newlines=True,
            input=new_contents,
            check=True,
        )

    click.secho(
        "📋 The contents of the portfile have been copied to your clipboard!",
        fg="cyan",
    )
