from zensearch.config import RELATIONSHIPS
from zensearch.utils import (
    get_entity_relationships,
    get_setup_entities,
    _auto_find_file_names,
)
from zensearch.entity_engine import Entity
import pytest
import os


@pytest.fixture
def get_entity_names():
    return ["user", "ticket", "organization"]


class TestSearch:
    def test_entity_relationships(self):
        for entity in RELATIONSHIPS:
            entity_relationship = get_entity_relationships(entity)
            assert RELATIONSHIPS[entity] == entity_relationship
        assert True


class TestSetupEntities:
    def test_setup_entities_valid(self, get_entity_names):
        entity_names = get_entity_names
        entities = get_setup_entities(
            entity_names, f"{os.path.dirname(os.path.abspath(__file__))}/test_data"
        )
        for name in entity_names:
            if name == "user":
                assert len(entities[name]._indices) == 19
            elif name == "organization":
                assert len(entities[name]._indices) == 9
            elif name == "ticket":
                assert len(entities[name]._indices) == 16
            else:
                assert False

            assert isinstance(entities[name], Entity)
            assert name == entities[name].entity_name

    def test_setup_entities_invalid_data_files(self, get_entity_names):
        invalid_data_files = ["not_a_dir", {"1": "not a list"}, None, True, 0]

        for invalid_file in invalid_data_files:
            with pytest.raises(TypeError) as error:
                get_setup_entities(get_entity_names, invalid_file)
            assert (
                "Invalid data_files given. data_files should be a directory path to files or list() of file paths themselves"
                in str(error.value)
            )
        assert True

    def test_setup_entities_names_files_mismatch(self, get_entity_names):
        with pytest.raises(ValueError) as error:
            get_setup_entities(get_entity_names, ["file1.json", "file2.json"])
            assert "Entity names and data files should be of same length" == str(
                error.value
            )
        assert True

    def test_setup_entities_auto_find_files(self, get_entity_names):
        import os

        entity_names = get_entity_names
        datadir = f"{os.path.dirname(os.path.abspath(__file__))}/test_data/"

        files = [
            "test_data_import_users.json",
            "test_data_import_tickets.json",
            "test_data_import_organizations.json",
        ]
        assert files == _auto_find_file_names(entity_names, datadir)

    def test_setup_entities_no_auto_find_files(self, get_entity_names):

        datadir = f"{os.path.dirname(os.path.abspath(__file__))}/"

        with pytest.raises(LookupError) as error:
            _auto_find_file_names(["random"], datadir)
        assert f"File with keyword random not found in dir {datadir}" == str(
            error.value
        )

    def test_setup_entities_multiple_auto_find_files(self, get_entity_names, tmpdir):

        keyword = "user"
        for i in range(2):
            with open(f"{tmpdir}/{keyword}{i}.json", "w") as f:
                f.write(f"{i}")

        with pytest.raises(LookupError) as error:
            _auto_find_file_names(keyword, tmpdir)
        assert f"Multiple files with keyword" in str(error.value)
