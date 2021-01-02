from pytest_mock import MockFixture

from seaport.clean import clean


def test_clean(fake_process, session_mocker: MockFixture, capfd):
    # Set default path
    # Don't use /opt/local since sudo is also patched
    session_mocker.patch("seaport.clean.user_path", return_value="/some/path")

    # Credit https://stackoverflow.com/a/58310550/10763533
    # Set the tempfile name
    session_mocker.patch(
        "seaport.clean.tempfile.NamedTemporaryFile"
    ).return_value.name = "tempfilename"

    fake_process.register_subprocess(
        ["/some/path/sudo", "cp", "tempfilename", "somewhere"], stdout=["Copied\n"]
    )

    fake_process.register_subprocess(
        ["/some/path/sudo", "/some/path/port", "clean", "--all", "portname"],
        stdout=["Cleaned\n"],
    )

    clean("original contents", "somewhere", "portname")
    out, err = capfd.readouterr()

    assert out == "🧽 Cleanup\n"
