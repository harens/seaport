"""Shell completion for port names."""

from typing import Any, List, Tuple, Union

from seaport.checks import user_path
from seaport.format import format_subprocess


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
