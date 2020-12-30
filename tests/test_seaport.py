from seaport import __version__, console


def test_version():
    assert __version__ == "0.1.1"


def test_subprocess():
    assert console.format_subprocess(["echo", "hello", "there"]) == "hello there"


def test_cmd():
    assert console.cmd_check("fjslfksdjf") == False
    assert console.cmd_check("echo") == True
