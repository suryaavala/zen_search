from main import main
import pytest
from zensearch.config import (
    MESSAGE_HOME,
    MESSAGE_SELECT_ENTITY,
    MESSAGE_SELECT_TERM,
    MESSAGE_SELECT_VALUE,
    MESSAGE_INVALID_SELECTION,
    MESSAGE_DASHED_LINE,
    MESSAGE_BYE,
    SLEEP_TIMER,
)
from io import StringIO


def test_main_loads(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", StringIO("quit"))
    with pytest.raises(SystemExit) as sys_exit:
        main(1)
    out, err = capsys.readouterr()
    assert sys_exit.value.code == 0
    assert out.strip() == MESSAGE_HOME + MESSAGE_BYE
