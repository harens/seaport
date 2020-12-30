import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from shutil import copyfile, which
from typing import List

import click

from . import __version__


def format_subprocess(args: List[str]) -> str:
    """Formats the output to remove newlines and decode to utf-8"""
    return subprocess.check_output(args).decode("utf-8").strip()


def exists(name: str) -> None:
    """Checks whether the port exists"""
    # Hide output
    if subprocess.call(
        ["port", "info", name], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT
    ):
        click.secho(f"❌ {name} is not a port", fg="red")
        sys.exit(1)


def cmd_check(name: str) -> bool:
    """Checks whether a command is installed"""
    # Credit to https://stackoverflow.com/a/34177358/10763533
    return which(name) is not None


def clean(original_text: str, location: str, port_name: str) -> None:
    """Returns the user's local portfile repo to the original state"""
    click.secho(f"🧽 Cleanup", fg="cyan")
    # Change contents of local portfile back to original
    tmp_original = tempfile.NamedTemporaryFile(mode="w")
    tmp_original.write(original_text)
    tmp_original.seek(0)
    subprocess.run(["sudo", "cp", tmp_original.name, location])
    tmp_original.close()

    subprocess.run(["sudo", "port", "clean", "--all", port_name])


def undo_revision(text: str):
    """Make version numbers 0"""
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
    if need_changed == 1:
        # Takes the original revision as a string
        # We know original_revision will not be of type none (hence mypy ignore)
        # This is ince need_changed is equal to 1
        original_revision = re.search(r"revision\s*[1-9]", text).group(0)  # type: ignore
        # Replaces the number with 0
        new_revision = original_revision[:-1] + "0"
        click.echo("Revision number changed")
        return text.replace(original_revision, new_revision)


def preliminary_checks(port: str, pull_request: Path) -> None:
    """Checks to run before carrying out updating process"""
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
        subprocess.run(["sudo", "port", "install", "gh"])


def new_version(port: str, stated: str, current: str) -> str:
    """Determines livecheck version, and sees whether already up-to-date"""
    # Determines new version number if none manually specified
    if not stated:
        # Take the last word of port livecheck, and then remove the bracket
        stated = format_subprocess(["port", "livecheck", port]).split(" ")[-1][:-1]

        # version == "" if livecheck doesn't output anything
        # current_version used in output since version = ""
        if stated == "":
            click.secho(
                f"{port} is either already up-to-date ({current}) or there is no livecheck available",
                fg="red",
            )
            click.secho(f"Please manually specify the version using --bump", fg="red")
            sys.exit(1)

    if stated == current:
        click.secho(f"{port} is already up-to-date ({current})", fg="red")
        sys.exit(1)

    return stated


def current_checksums(port: str, current: str, new: str):
    """Returns outdated checksums and the website to download the new files from"""

    distfiles = (
        format_subprocess(["port", "distfiles", port]).replace("\n ", "").split(" ")
    )

    # There's no output if it's the "skeleton" head port
    try:
        old_website = [s for s in distfiles if "http" in s][0]
    except IndexError:
        # Tries to determine the subport
        # This is since the distfiles cmd only works for subports
        port_info = format_subprocess(["port", "info", port])
        if "Sub-ports" not in port_info:
            click.secho(f"Cannot determine distfiles", fg="red")
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


def new_checksums(website: str):
    """Generate checksums of file downloaded from website"""
    download_dir = tempfile.TemporaryDirectory()
    download_location = f"{download_dir.name}/download"

    urllib.request.urlretrieve(website, download_location)

    sha256 = format_subprocess(["openssl", "dgst", download_location]).split(" ")[-1]
    rmd160 = format_subprocess(["openssl", "dgst", "-rmd160", download_location]).split(
        " "
    )[-1]
    size = str(Path(download_location).stat().st_size)

    download_dir.cleanup()

    return sha256, rmd160, size


def new_portfile(
    port: str,
    current: str,
    new: str,
    old_sha: str,
    old_rmd: str,
    old_size: str,
    new_sha: str,
    new_rmd: str,
    new_size: str,
):
    """Replace a portfile's old checksums with the new ones"""
    file = subprocess.check_output(["port", "file", port]).decode("utf-8").strip()

    with click.open_file(file) as f:
        # Backup of the original contents
        original_contents = f.read()

    # Bump revision numbers to 0
    new_contents = undo_revision(original_contents)

    # Replace first instances only
    new_contents = new_contents.replace(current, new, 1)
    new_contents = new_contents.replace(old_sha, new_sha, 1)
    new_contents = new_contents.replace(old_rmd, new_rmd, 1)
    new_contents = new_contents.replace(old_size, new_size, 1)

    return original_contents, new_contents, file


# Shell completion for port names
def get_names(ctx, args, incomplete: str):
    results = format_subprocess(
        ["port", "search", "--name", "--line", "--glob", f"{incomplete}*"]
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
def main(name: str, bump: str, pr: Path, test: bool, lint: bool, install: bool) -> None:
    """Bumps the version number and checksum of NAME, and copies the result to your clipboard"""

    # Tasks that require sudo
    sudo = test or lint or install

    preliminary_checks(name, pr)

    current_version = format_subprocess(["port", "info", "--version", name]).split(" ")[
        1
    ]

    # Determine new version
    bump = new_version(name, bump, current_version)
    click.secho(f"👍 New version is {bump}", fg="green")

    # Where to download the new file + old checksums
    new_website, old_size, old_sha256, old_rmd160 = current_checksums(
        name, current_version, bump
    )

    click.secho(f"🔻 Downloading from {new_website}", fg="cyan")
    new_sha256, new_rmd160, new_size = new_checksums(new_website)

    click.secho(f"🔎 Checksums:", fg="cyan")
    click.echo(f"Old rmd160: {old_rmd160}")
    click.echo(f"New rmd160: {new_rmd160}")
    click.echo(f"Old sha256: {old_sha256}")
    click.echo(f"New sha256: {new_sha256}")
    click.echo(f"Old size: {old_size}")
    click.echo(f"New size: {new_size}")

    # Add the new checksums, and take a backup of the original
    original, new_contents, file_location = new_portfile(
        name,
        current_version,
        bump,
        old_sha256,
        old_rmd160,
        old_size,
        new_sha256,
        new_rmd160,
        new_size,
    )

    subprocess.run("pbcopy", universal_newlines=True, input=new_contents)
    click.secho(
        f"📋 The contents of the portfile have been copied to your clipboard!", fg="cyan"
    )

    # Temporary files created to get around sudo write problem
    # Changes made in temparary file, and sudo copied over
    # Outside of sudo block since git requires it
    tmp_version = tempfile.NamedTemporaryFile(mode="w")
    tmp_version.write(new_contents)
    tmp_version.seek(0)

    # Everything below requires sudo

    if sudo:
        click.secho(f"💾 Editing local portfile repo, sudo required", fg="cyan")
        click.echo("Changes will be reverted after completion")
        subprocess.run(["sudo", "cp", tmp_version.name, file_location])

    if test:
        click.secho(f"🧪 Testing {name}", fg="cyan")
        subprocess.run(["sudo", "port", "test", name])
    if lint:
        click.secho(f"🧐 Linting {name}", fg="cyan")
        subprocess.run(["port", "lint", "--nitpick", name])

    if install:
        click.secho(f"🏗️ Installing {name}", fg="cyan")
        subprocess.run(["sudo", "port", "-vst", "install", name])
        click.secho(
            "Paused to allow user to test basic functionality in a different terminal",
            fg="cyan",
        )
        click.pause("Press any key to continue ")
        click.secho(f"🗑 Uninstalling {name}", fg="cyan")
        subprocess.run(["sudo", "port", "uninstall", name])

    if pr:

        category_list = format_subprocess(["port", "info", "--category", name]).split(
            " "
        )

        # Remove comma, and only take the first category
        if len(category_list) > 2:
            category = category_list[1][:-1]
        else:
            category = category_list[1]

        click.secho(f"🚀 Cloning macports/macports-ports", fg="cyan")
        os.chdir(pr)
        subprocess.run(
            [
                "gh",
                "repo",
                "fork",
                "macports/macports-ports",
                "--clone=true",
                "--remote=true",
            ]
        )

        # Update origin
        os.chdir(f"{pr}/macports-ports")
        subprocess.run(["git", "fetch", "upstream"])
        subprocess.run(["git", "merge", "upstream/master"])
        subprocess.run(["git", "push"])

        subprocess.run(["git", "checkout", "-b", f"seaport-{name}-{bump}"])
        copyfile(
            tmp_version.name,
            f"{pr}/macports-ports/{category}/{name}/Portfile",
        )
        subprocess.run(["git", "add", f"{category}/{name}/Portfile"])
        subprocess.run(["git", "commit", "-m", f"{name}: update to {bump}"])
        # Automatically choose to send PR to remote
        subprocess.run(["git", "config", "remote.upstream.gh-resolved", "base"])

        # PR variables
        mac_version = format_subprocess(["sw_vers", "-productVersion"])
        xcode_version = format_subprocess(["xcodebuild", "-version"]).replace(
            "\nBuild version", ""
        )

        if click.confirm("Does everything look good before sending PR?"):
            subprocess.run(
                ["git", "push", "--set-upstream", "origin", f"seaport-{name}-{bump}"]
            )
            subprocess.run(
                [
                    "gh",
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
                ]
            )

        subprocess.run(["git", "checkout", "master"])
        subprocess.run(["git", "branch", "-D", f"seaport-{name}-{bump}"])

    if sudo:
        clean(original, file_location, name)
