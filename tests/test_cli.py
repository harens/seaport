from click.testing import CliRunner

from seaport import __version__
from seaport.init import seaport


def test_version() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["--version"])
    assert result.exit_code == 0
    assert result.output == f"seaport, version {__version__}\n"


def test_help() -> None:
    runner = CliRunner()
    result = runner.invoke(seaport, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output
    assert "Show the version and exit" in result.output
