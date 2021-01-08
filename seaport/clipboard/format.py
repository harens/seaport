"""Functions for formatting output."""

import subprocess
from typing import List


def format_subprocess(args: List[str]) -> str:
    """Formats the output to remove newlines and decode to utf-8.

    Args:
        args: A list of arguments to run

    Returns:
        str: The formatted output of the result

    """
    return subprocess.check_output(args).decode("utf-8").strip()
