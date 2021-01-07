"""Command to send a PR after updating portfile."""

import os
import subprocess
import sys
import tempfile
from shutil import copyfile
from typing import Any, cast

import click

from seaport.checks import user_path
from seaport.commands.autocomplete import get_names
from seaport.commands.clipboard import clip
from seaport.format import format_subprocess


@click.command()
@click.argument("name", type=str, autocompletion=get_names)
@click.argument(
    "location",
    type=click.Path(exists=True, dir_okay=True, writable=True),
)
# Some versions could be v1.2.0-post for example
@click.option("--bump", help="The new version number", type=str)
@click.option("--test/--no-test", default=False, help="Runs port test")
@click.option("--lint/--no-lint", default=False, help="Runs port lint --nitpick")
@click.option(
    "--install/--no-install",
    default=False,
    help="Installs the port and allows testing of basic functionality",
)
@click.option("--new", is_flag=True, help="Send a PR from the local portfile repo")
@click.pass_context
def pr(
    ctx: Any,
    name: str,
    bump: str,  # bump is used as part of ctx.forward
    location: str,
    test: bool,
    lint: bool,
    install: bool,
    new: bool,
) -> None:
    """Bumps the version number and checksum of NAME, and sends a PR to update it."""
    # Invoke the clipboard cmd
    # That's the command that determines the new contents
    ctx.forward(clip)

    # Determine the output of the clip function from clipboard
    # Newline added since clipboard removes it
    new_contents = format_subprocess(["pbpaste"]) + "\n"

    # Get updated version number from clip
    # Separate var to get mypy to work
    # This is since os.getenv is Optional[str]
    env_variable = os.getenv("BUMP")

    if env_variable is None:
        click.secho(
            "Cannot determine version number from env variable `bump`", fg="red"
        )
        sys.exit(1)

    bump = env_variable

    # Write the new portfile contents to a tempfile
    tmp_version = tempfile.NamedTemporaryFile(mode="w")
    tmp_version.write(new_contents)
    tmp_version.seek(0)

    # Category determined so as to know where to put the portfile
    # e.g. macports-ports/category/name/Portfile
    category_list = format_subprocess(
        [f"{user_path(True)}/port", "info", "--category", name]
    ).split(" ")

    # Remove comma, and only take the first category
    if len(category_list) > 2:
        category = category_list[1][:-1]
    else:
        category = category_list[1]

    click.secho("🚀 Cloning macports/macports-ports", fg="cyan")
    os.chdir(location)
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
    os.chdir(f"{location}/macports-ports")
    subprocess.run([f"{user_path()}/git", "fetch", "upstream"], check=True)
    subprocess.run([f"{user_path()}/git", "merge", "upstream/master"], check=True)
    subprocess.run([f"{user_path()}/git", "push"], check=True)

    # Different titles depending on whether updating
    # or adding new file
    commit_title = f"{name}: new port" if new else f"{name}: update to {bump}"

    subprocess.run(
        [f"{user_path()}/git", "checkout", "-b", f"seaport-{name}-{bump}"],
        check=True,
    )

    # Remove backslash from user macports repo location
    # This allows copyfile to work regardless of whether there's
    # a backslash or not
    location = location.rstrip("/")

    if new:
        # Have to create directories for new portfile
        subprocess.run(
            ["/bin/mkdir", "-p", f"{location}/macports-ports/{category}/{name}"],
            check=True,
        )
        # copyfile not used since cp creates the file automatically
        # IF copyfile was used, touch would also be required
        subprocess.run(
            [
                "/bin/cp",
                tmp_version.name,
                f"{location}/macports-ports/{category}/{name}/Portfile",
            ],
            check=True,
        )
    else:
        copyfile(
            tmp_version.name,
            f"{location}/macports-ports/{category}/{name}/Portfile",
        )

    subprocess.run(
        [f"{user_path()}/git", "add", f"{category}/{name}/Portfile"], check=True
    )
    subprocess.run(
        [f"{user_path()}/git", "commit", "-m", commit_title],
        check=True,
    )
    # Automatically choose to send PR to remote
    # Change to remote.origin.gh-resolved to send to user's fork
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
                commit_title,
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
    # cleanup process
    subprocess.run([f"{user_path()}/git", "checkout", "master"], check=True)
    subprocess.run(
        [f"{user_path()}/git", "branch", "-D", f"seaport-{name}-{bump}"], check=True
    )
