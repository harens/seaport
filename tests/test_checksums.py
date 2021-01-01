import pytest
from pytest_mock import MockFixture

from seaport.checksums import current_checksums, new_checksums


def test_current_checksums(fake_process) -> None:

    distfiles = (
        "https://files.pythonhosted.org/packages/source/c/commitizen/commitizen-2.12.2.tar.gz",
        "30070",
        "96d5ebf5a5ec4e2b7190611faaaff0b87246d753d933994b29a0125a939dd682",
        "c1b78851fc66295a3f5ccda10aeeaeb65a95dd22",
    )

    # Valid port entry with no subports

    fake_process.register_subprocess(
        ["port", "distfiles", "commitizen"],
        stdout=[
            "--->  Distfiles for commitizen\n[commitizen-2.12.1.tar.gz] /opt/local/var/macports/distfiles/commitizen/commitizen-2.12.1.tar.gz\n rmd160: c1b78851fc66295a3f5ccda10aeeaeb65a95dd22\n sha256: 96d5ebf5a5ec4e2b7190611faaaff0b87246d753d933994b29a0125a939dd682\n size: 30070\n  https://files.pythonhosted.org/packages/source/c/commitizen/commitizen-2.12.1.tar.gz\n  http://aarnet.au.distfiles.macports.org/pub/macports/distfiles/commitizen/commitizen-2.12.1.tar.gz\n \n"
        ],
        occurrences=3,
    )

    assert current_checksums("commitizen", "2.12.1", "2.12.2") == distfiles

    # Invalid entry + no subports

    fake_process.register_subprocess(
        ["port", "distfiles", "example"],
        stdout=["--->  Distfiles for example\n"],
        occurrences=3,
    )
    fake_process.register_subprocess(
        ["port", "info", "example"], stdout=["example things\n"]
    )

    with pytest.raises(SystemExit):
        current_checksums("example", "1.0", "2.0")

    # Subports available (subport in this scenario is commitizen)

    fake_process.register_subprocess(
        ["port", "info", "example"],
        stdout=[
            "example @1.0 (devel)\nSub-ports:            example1, commitizen\n\nDescription:\n"
        ],
    )

    assert current_checksums("example", "2.12.1", "2.12.2") == distfiles

    # Single subport availble

    fake_process.register_subprocess(
        ["port", "info", "example"],
        stdout=[
            "example @1.0 (devel)\nSub-ports:            commitizen\n\nDescription:\n"
        ],
    )

    assert current_checksums("example", "2.12.1", "2.12.2") == distfiles
