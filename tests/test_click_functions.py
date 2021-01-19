from typing import Optional

import click
from click.testing import CliRunner

from seaport.click_functions import main_cmd


@click.command()
@main_cmd
def example(
    name: str,  # Parameters from decorators required
    bump: str,
    test: bool,
    lint: bool,
    install: bool,
    location: Optional[str] = None,
    new: bool = False,
) -> None:
    """An example click command for testing."""
    click.echo(name)


def test_name() -> None:
    runner = CliRunner()
    # clip used to get 100% cov in init file
    result = runner.invoke(example, ["hello"])
    assert result.exit_code == 0
    assert result.output == "hello\n"


def test_help() -> None:
    runner = CliRunner()
    # clip used to get 100% cov in init file
    result = runner.invoke(example, ["--help"])
    assert result.exit_code == 0
    assert "Show this message and exit" in result.output
