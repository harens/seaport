"""The main CLI function, which the user runs."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from shutil import copyfile
from typing import Any, List, Tuple, Union

import click

from seaport import __version__
from seaport.additional import perform_lint
from seaport.checks import preliminary_checks, user_path
from seaport.checksums import current_checksums, new_checksums
from seaport.clean import clean
from seaport.format import format_subprocess
from seaport.portfile_numbers import new_version, undo_revision


# Shell completion for port names
def get_names(
    ctx: Any, args: List[str], incomplete: str
) -> List[Union[str, Tuple[str, str]]]:
    """Shell autocompletion for port names.

    Args:
        ctx: The current command context
        args: The list of arguments passed in
        incomplete: The partial word that is being completed

    Returns:
        List[Union[str, Tuple[str, str]]]: The portname and the description
    """
    results = format_subprocess(
        [
            f"{user_path(True)}/port",
            "search",
            "--name",
            "--line",
            "--glob",
            f"{incomplete}*",
        ]
    ).splitlines()
    # Converts to raw string literal to split by backslash
    # See https://stackoverflow.com/a/25047988/10763533
    return [(repr(k).split("\\")[0][1:], repr(k).split("\\")[3][1:-1]) for k in results]


@click.command()
@click.version_option(__version__)
@click.argument("name", type=str, autocompletion=get_names)
# Some versions could be v1.2.0-post for example
@click.option("--bump", help="The new version number", type=str)
@click.option(
    "--pr",
    type=click.Path(exists=True, dir_okay=True, writable=True),
    help="Location for where to clone the macports-ports repo",
)
@click.option("--test/--no-test", default=False, help="Runs port test")
@click.option("--lint/--no-lint", default=False, help="Runs port lint --nitpick")
@click.option(
    "--install/--no-install",
    default=False,
    help="Installs the port and allows testing of basic functionality",
)
def seaport(
    name: str, bump: str, pr: Path, test: bool, lint: bool, install: bool
) -> None:
    """Bumps the version number and checksum of NAME, and copies the result to your clipboard."""
    # Tasks that require sudo
    sudo = test or lint or install

    preliminary_checks(name, pr)

    current_version = format_subprocess(
        [f"{user_path(True)}/port", "info", "--version", name]
    ).split(" ")[1]

    # Determine new version
    bump = new_version(name, bump, current_version)
    click.secho(f"👍 New version is {bump}", fg="green")

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

    subprocess.run(
        f"{user_path()}/pbcopy", universal_newlines=True, input=new_contents, check=True
    )
    click.secho(
        "📋 The contents of the portfile have been copied to your clipboard!", fg="cyan"
    )

    # Temporary files created to get around sudo write problem
    # Changes made in temparary file, and sudo copied over
    # Outside of sudo block since git requires it
    tmp_version = tempfile.NamedTemporaryFile(mode="w")
    tmp_version.write(new_contents)
    tmp_version.seek(0)

    # Everything below requires sudo

    if sudo:
        click.secho("💾 Editing local portfile repo, sudo required", fg="cyan")
        click.echo("Changes will be reverted after completion")
        subprocess.run(
            [f"{user_path()}/sudo", "cp", tmp_version.name, file_location], check=True
        )

    if test:
        click.secho(f"🧪 Testing {name}", fg="cyan")
        subprocess.run(
            [f"{user_path()}/sudo", f"{user_path(True)}/port", "test", name], check=True
        )
    if lint:
        # If the lint is not successful
        if not perform_lint(name):
            clean(original, file_location, name)
            sys.exit(1)

    if install:
        click.secho(f"🏗️ Installing {name}", fg="cyan")
        subprocess.run(
            [f"{user_path()}/sudo", f"{user_path(True)}/port", "-vst", "install", name],
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

    if pr:

        category_list = format_subprocess(
            [f"{user_path(True)}/port", "info", "--category", name]
        ).split(" ")

        # Remove comma, and only take the first category
        if len(category_list) > 2:
            category = category_list[1][:-1]
        else:
            category = category_list[1]

        click.secho("🚀 Cloning macports/macports-ports", fg="cyan")
        os.chdir(pr)
        # check false if macports-ports already exists (error 127)
        subprocess.run(
            [
                f"{user_path(False, True)}/gh",
                "repo",
                "fork",
                "macports/macports-ports",
                "--clone=true",
                "--remote=true",
            ],
            check=False,
        )

        # Update origin
        os.chdir(f"{pr}/macports-ports")
        subprocess.run([f"{user_path()}/git", "fetch", "upstream"], check=True)
        subprocess.run([f"{user_path()}/git", "merge", "upstream/master"], check=True)
        subprocess.run([f"{user_path()}/git", "push"], check=True)

        subprocess.run(
            [f"{user_path()}/git", "checkout", "-b", f"seaport-{name}-{bump}"],
            check=True,
        )
        copyfile(
            tmp_version.name,
            f"{pr}/macports-ports/{category}/{name}/Portfile",
        )
        subprocess.run(
            [f"{user_path()}/git", "add", f"{category}/{name}/Portfile"], check=True
        )
        subprocess.run(
            [f"{user_path()}/git", "commit", "-m", f"{name}: update to {bump}"],
            check=True,
        )
        # Automatically choose to send PR to remote
        subprocess.run(
            [f"{user_path()}/git", "config", "remote.upstream.gh-resolved", "base"],
            check=True,
        )

        # PR variables
        mac_version = format_subprocess([f"{user_path()}/sw_vers", "-productVersion"])
        xcode_version = format_subprocess(
            [f"{user_path()}/xcodebuild", "-version"]
        ).replace("\nBuild version", "")

        if click.confirm("Does everything look good before sending PR?"):
            subprocess.run(
                [
                    f"{user_path()}/git",
                    "push",
                    "--set-upstream",
                    "origin",
                    f"seaport-{name}-{bump}",
                ],
                check=True,
            )
            subprocess.run(
                [
                    f"{user_path(False, True)}/gh",
                    "pr",
                    "create",
                    "--title",
                    f"{name}: update to {bump}",
                    "--body",
                    f"""#### Description

Created with [seaport](https://github.com/harens/seaport)

###### Type(s)

- [ ] bugfix
- [x] enhancement
- [ ] security fix

###### Tested on
macOS {mac_version}
{xcode_version}

###### Verification <!-- (delete not applicable items) -->
Have you

- [x] followed our [Commit Message Guidelines](https://trac.macports.org/wiki/CommitMessages)?
- [x] squashed and [minimized your commits](https://guide.macports.org/#project.github)?
- [ ] checked that there aren't other open [pull requests](https://github.com/macports/macports-ports/pulls) for the same change?
- [ ] referenced existing tickets on [Trac](https://trac.macports.org/wiki/Tickets) with full URL? <!-- Please don't open a new Trac ticket if you are submitting a pull request. -->
- [{"x" if lint else " "}] checked your Portfile with `port lint`?
- [{"x" if test else " "}] tried existing tests with `sudo port test`?
- [{"x" if install else " "}] tried a full install with `sudo port -vst install`?
- [{"x" if install else " "}] tested basic functionality of all binary files?""",
                ],
                check=True,
            )

        subprocess.run([f"{user_path()}/git", "checkout", "master"], check=True)
        subprocess.run(
            [f"{user_path()}/git", "branch", "-D", f"seaport-{name}-{bump}"], check=True
        )

    if sudo:
        clean(original, file_location, name)
