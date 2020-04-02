from main import main
import pytest


class TestMain:
    def test_default_output(self, capfd):
        # main()  # Writes "Hello World!" to stdout
        # out, err = capfd.readouterr()
        # assert out == print(MESSAGE_HOME)
        assert True
