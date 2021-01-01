from seaport.format import format_subprocess


def test_subprocess() -> None:
    assert format_subprocess(["echo", "hello", "there"]) == "hello there"
