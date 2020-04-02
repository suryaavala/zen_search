from zensearch.app import ZendeskSearch
from zensearch.config import (
    MESSAGE_HOME,
    MESSAGE_SELECT_ENTITY,
    MESSAGE_SELECT_TERM,
    MESSAGE_SELECT_VALUE,
)
from zensearch.entity_engine import Entity
import pytest
import os


@pytest.fixture
def test_data_dir():
    return f"{os.path.dirname(os.path.abspath(__file__))}/test_data/"


@pytest.fixture
def get_entity_names():
    return ["user", "ticket", "organization"]


@pytest.fixture
def get_app(test_data_dir):
    return ZendeskSearch(data_dir=test_data_dir)


class TestAppInit:
    def test_app_valid_init(self):
        data_dir = f"{os.path.dirname(os.path.abspath(__file__))}/test_data"
        zdsearch = ZendeskSearch(data_dir=data_dir)
        for entity in zdsearch.entities_dict:
            if entity == "user":
                assert len(zdsearch.entities_dict[entity]._indices) == 19
            elif entity == "organization":
                assert len(zdsearch.entities_dict[entity]._indices) == 9
            elif entity == "ticket":
                assert len(zdsearch.entities_dict[entity]._indices) == 16
            else:
                assert False

            assert isinstance(zdsearch.entities_dict[entity], Entity)
