from io import StringIO

import pytest
from main import main
from zensearch.config import (
    MESSAGE_BYE,
    MESSAGE_DASHED_LINE,
    MESSAGE_HOME,
    MESSAGE_INVALID_SELECTION,
    MESSAGE_SELECT_ENTITY,
    MESSAGE_SELECT_TERM,
    MESSAGE_SELECT_VALUE,
    SLEEP_TIMER,
)


def test_main_loads(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", StringIO("quit"))
    with pytest.raises(SystemExit) as sys_exit:
        main(1)
    out, err = capsys.readouterr()
    assert sys_exit.value.code == 0
    assert out.strip() == MESSAGE_HOME + MESSAGE_BYE
