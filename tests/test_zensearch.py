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
import ujson


@pytest.fixture
def test_data_dir():
    return f"{os.path.dirname(os.path.abspath(__file__))}/test_data/"


@pytest.fixture
def entity_names():
    return ["user", "ticket", "organization"]


@pytest.fixture
def zen(test_data_dir):
    return ZendeskSearch(
        entity_names=["user", "ticket", "organization"], data_dir=test_data_dir
    )


@pytest.fixture
def test_data_from_files(test_data_dir, entity_names):
    entity_data = {}

    for entity in entity_names:
        with open(f"{test_data_dir}test_data_import_{entity}s.json", "r") as f:
            entity_data[entity] = ujson.load(f)
    return entity_data


class TestAppInit:
    def test_app_valid_init(self):
        data_dir = f"{os.path.dirname(os.path.abspath(__file__))}/test_data"
        zdsearch = ZendeskSearch(
            entity_names=["user", "ticket", "organization"], data_dir=data_dir
        )
        for entity in zdsearch._entities_dict:
            if entity == "user":
                assert len(zdsearch._entities_dict[entity]._indices) == 19
            elif entity == "organization":
                assert len(zdsearch._entities_dict[entity]._indices) == 9
            elif entity == "ticket":
                assert len(zdsearch._entities_dict[entity]._indices) == 16
            else:
                assert False

            assert isinstance(zdsearch._entities_dict[entity], Entity)


class TestMiscFunctions:
    def test_get_entity_searchable_entity_fields_match(self, zen, test_data_from_files):
        data_key_sets = {e: set() for e in test_data_from_files}
        for entity in test_data_from_files:
            for data_point in test_data_from_files[entity]:
                data_key_sets[entity].update(data_point.keys())
            from_files = list(data_key_sets[entity])
            from_app = zen._get_entity_searchable_fields(entity)
            from_files.sort()
            from_app.sort()
            assert from_app == from_files
        return

    def test_get_entity_searchable_fields_match(self, zen, test_data_from_files):
        data_key_sets = {e: set() for e in test_data_from_files}
        searchable_fields_dict = zen._get_searchable_fields()
        for entity in test_data_from_files:
            for data_point in test_data_from_files[entity]:
                data_key_sets[entity].update(data_point.keys())
            from_files = list(data_key_sets[entity])
            from_app = searchable_fields_dict[entity]
            from_files.sort()
            from_app.sort()
            assert from_app == from_files
        return


class TestHelperFunctions:
    def test_update_match_with_related_invalid_matches(self, zen):
        matches = [[], 1, -1, None, True]
        related_match = [{"_id": 1}]
        for m in matches:
            with pytest.raises(TypeError) as error:
                zen._update_match_with_related(m, related_match, "user", "test")
            assert (
                "Match should be of type dict() (data point from data in entity)"
                in str(error.value)
            )
        assert True

    def test_update_match_with_related_no_fields_related_match(self, zen):
        match = {}
        related_matches = [[{"d": 1}], [{"id": 1}], [{1: 1}]]
        for rm in related_matches:
            with pytest.raises(KeyError) as error:
                zen._update_match_with_related(match, rm, "user", "test")
            assert "'_id'" == str(error.value)
        assert True

    def test_update_match_with_related_happy_paths(self, zen):
        match = {}
        link_string = "linking"
        related_matches = [
            [{"_id": 55}],
            [{"name": "test name"}],
            [{"name": "name", "_id": 1}],
        ]
        expected_updated_matches = [
            {link_string: 55},
            {link_string: "test name"},
            {link_string: "name"},
        ]

        for rel, exp in zip(related_matches, expected_updated_matches):
            zen._update_match_with_related(match, rel, "user", link_string)
            assert match == exp
            match = {}
        assert True

    def test_get_match_in_entity(self, zen):
        searches = [
            ["user", "_id", "1"],
            ["ticket", "_id", 2],
            ["organization", "_id", 2],
        ]
        for search in searches:
            assert list(zen._get_matches_in_entity(*search)) == list(
                zen._entities_dict[search[0]].search(*search[1:])
            )
        assert True

    def test_get_match_in_entity_invalid_entity(self, zen):
        searches = [
            ["user", "_id", "1"],
            ["ticket", "_id", 2],
            ["organization", "_id", 2],
        ]
        for search in searches:
            assert list(zen._get_matches_in_entity(*search)) == list(
                zen._entities_dict[search[0]].search(*search[1:])
            )
        assert True

    def test_get_match_in_entity_not_found(self, zen):
        entites = ["tree", None, 1, 0, False]
        for e in entites:
            with pytest.raises(KeyError) as error:
                zen._get_matches_in_entity(e, "_id", "1")
            assert "Entity not found" in str(error.value)
        assert True


class TestRelatedMatches:
    def test_get_all_matches_invalid_entity(self, zen):
        invalid_query = ["not_an_entity", "_id", "1"]
        with pytest.raises(KeyError) as error:
            list(zen.get_all_matches(*invalid_query))
        assert "Entity not found" in str(error.value)

    def test_get_all_matches_invalid_field(self, zen):
        invalid_query = ["user", "not_a_field", "1"]
        assert list(zen.get_all_matches(*invalid_query)) == []

    def test_get_all_matches_invalid_value(self, zen):
        invalid_query = ["user", "_id", "not_a_value"]
        assert list(zen.get_all_matches(*invalid_query)) == []

    def test_find_update_related_matches_invalid_entity(self, zen):
        with pytest.raises(KeyError) as error:
            zen._find_update_related_matches("not_an_entity", {})
        assert (
            "Entity name not found in Relationships. Look at RELATIONSHIPS in config.py"
            in str(error.value)
        )

    def test_find_update_related_matches_invalid_matches(self, zen):
        invalid_matches = [[], "not_a_match", 1, -1, 0, False, True, (), {1}]

        for inv in invalid_matches:
            with pytest.raises(TypeError) as error:
                zen._find_update_related_matches("user", inv)
            assert (
                "Invalid match object. match should be a data point of type dict()"
                in str(error.value)
            )

    def test_find_update_related_matches_empty_match(self, zen):
        """If the match is empty or doesn't have a search key that links it to other entities, then we should get the same match back
        """
        matches = [{}, {"name": "1"}, {"not_id": 5}]
        for match in matches:
            inp_match = ujson.loads(ujson.dumps(match))
            assert zen._find_update_related_matches("user", match) == inp_match
        assert True

    def test_find_update_related_matches_valid(self, zen):
        """If the match is empty or doesn't have a search key that links it to other entities, then we should get the same match back
        """
        matches = [
            {},
            {"_id": 1, "organization_id": "101", "assignee_id": "5"},
            {"_id": 5},
        ]
        exp_out = [
            {},
            {
                "_id": 1,
                "organization_id": "101",
                "assignee_id": "5",
                "organization_name": "Enthaze",
                "ticket_assigned": "A Problem in Russian Federation",
                "ticket_assigned_2": "A Problem in Malawi",
                "submitted_ticket": "A Nuisance in Kiribati",
                "submitted_ticket_2": "A Nuisance in Saint Lucia",
            },
            {
                "_id": 5,
                "ticket_assigned": "A Drama in Saudi Arabia",
                "ticket_assigned_2": "A Drama in Botswana",
                "ticket_assigned_3": "A Drama in Cameroon",
                "ticket_assigned_4": "A Drama in Gabon",
                "submitted_ticket": "A Drama in Georgia",
                "submitted_ticket_2": "A Catastrophe in Gibraltar",
            },
        ]
        for match, expected in zip(matches, exp_out):
            returned = zen._find_update_related_matches("user", match)
            assert match == expected == returned
        assert True
