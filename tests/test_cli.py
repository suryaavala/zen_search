from main import main
import pytest
from unittest.mock import patch
from zensearch.config import MESSAGE_BYE


def get_quit_sequences():
    return [
        [1, "quit"],
        [1, 1, "quit"],
        [1, 1, 1, "quit"],
        [1, 1, 1, "_id", "quit"],
        [1, 1, 2, "quit"],
        [1, 1, 2, "_id", "quit"],
        [1, 1, 3, "quit"],
        [1, 1, 3, "_id", "quit"],
    ]


@pytest.mark.parametrize("data_set", get_quit_sequences())
def test_input(data_set, capsys):
    with patch("builtins.input", side_effect=data_set[1:]):
        with pytest.raises(SystemExit) as sys_exit:
            main(data_set[0])

    out, err = capsys.readouterr()
    print(out, err)
    assert sys_exit.value.code == 0
    assert out.strip() == MESSAGE_BYE
