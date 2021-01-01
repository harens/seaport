"""Functions for cleaning up after completion, such as resetting files to their original state."""

import subprocess
import tempfile

import click

from seaport.checks import user_path


def clean(original_text: str, location: str, port_name: str) -> None:
    """Returns the user's local portfile repo to the original state.

    Args:
        original_text: What the contents of the portfile originally was
        location: Where the portfile is located
        port_name: The name of the portfile

    """
    click.secho("🧽 Cleanup", fg="cyan")
    # Change contents of local portfile back to original
    tmp_original = tempfile.NamedTemporaryFile(mode="w")
    tmp_original.write(original_text)
    tmp_original.seek(0)
    subprocess.run(
        [f"{user_path()}/sudo", "cp", tmp_original.name, location], check=True
    )
    tmp_original.close()

    subprocess.run(
        [f"{user_path()}/sudo", f"{user_path(True)}/port", "clean", "--all", port_name],
        check=True,
    )
