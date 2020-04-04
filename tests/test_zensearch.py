from zensearch.zensearch import ZendeskSearch
from zensearch.config import (
    MESSAGE_HOME,
    MESSAGE_SELECT_ENTITY,
    MESSAGE_SELECT_TERM,
    MESSAGE_SELECT_VALUE,
)
from zensearch.entity_engine import Entity
import pytest
import os
import json


@pytest.fixture
def test_data_dir():
    return f"{os.path.dirname(os.path.abspath(__file__))}/test_data/"


@pytest.fixture
def entity_names():
    return ["user", "ticket", "organization"]


@pytest.fixture
def app(test_data_dir):
    return ZendeskSearch(
        entity_names=["user", "ticket", "organization"], data_dir=test_data_dir
    )


@pytest.fixture
def test_data_from_files(test_data_dir, entity_names):
    entity_data = {}

    for entity in entity_names:
        with open(f"{test_data_dir}test_data_import_{entity}s.json", "r") as f:
            entity_data[entity] = json.load(f)
    return entity_data


class TestAppInit:
    def test_app_valid_init(self):
        data_dir = f"{os.path.dirname(os.path.abspath(__file__))}/test_data"
        zdsearch = ZendeskSearch(
            entity_names=["user", "ticket", "organization"], data_dir=data_dir
        )
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


class TestMiscFunctions:
    def test_get_entity_searchable_fields_match(self, app, test_data_from_files):
        data_key_sets = {e: set() for e in test_data_from_files}
        for entity in test_data_from_files:
            for data_point in test_data_from_files[entity]:
                data_key_sets[entity].update(data_point.keys())
            # print(
            #     app._get_entity_searchable_fields(entity), list(data_key_sets[entity])
            # )
            from_files = list(data_key_sets[entity])
            from_app = app._get_entity_searchable_fields(entity)
            from_files.sort()
            from_app.sort()
            assert from_app == from_files
        return
