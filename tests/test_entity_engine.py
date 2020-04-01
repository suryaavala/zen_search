import json
import os

import pytest
from zensearch.entity_engine import Entity
from zensearch.exceptions import PrimaryKeyNotFoundError, DuplicatePrimaryKeyError


def write_to_file(content, file_name):
    with open(file_name, "w") as f:
        f.write(str(content))
    return


def get_entity_with_data_indices(entity_name):
    """Instantiates and returns an Entity object of entity_name after loading data (from
    inferred test data file) and building indices
    
    Args:
        entity_name (str): One of user, organization, ticket
    
    Returns:
        Entity(): entity object of name entity_name, with test data loaded and incdices built
    """
    data_file_name = f"tests/test_data/test_data_import_{entity_name}s.json"
    entity = Entity(entity_name)
    entity.load_data_build_indices_from_file(data_file_name)
    return entity


def get_all_entities(entity_names=["user", "ticket", "organization"]):
    entities = {
        entity_name: get_entity_with_data_indices(entity_name)
        for entity_name in entity_names
    }
    return entities


def get_entity_from_formatted_data(entity_name, data):
    entity = Entity(entity_name)
    entity._build_indices(data)
    return entity


class TestEntityEngine:
    def test_entity_struct(self):
        """Test to see if Entity instantiates with 
                a primary key
                alteast an index on primary key
                _build_indices 
                load_data_build_indices_from_file
                search
        """
        entity = Entity("user")

        assert entity.primary_key == "_id"
        assert entity.indices == {"_id": {}}
        assert hasattr(entity, "_build_indices")
        assert hasattr(entity, "load_data_build_indices_from_file")
        assert hasattr(entity, "search")


class TestEntityEngineLoadData:
    def test_entity_invalid_file(self):
        """Test for a FileNotFoundError when an empty string or invalid path to file is given
        """
        entity = Entity("user")

        with pytest.raises(FileNotFoundError) as error:
            entity.load_data_build_indices_from_file("nofile.txt")
        assert "[Errno 2] No such file or directory:" in str(error.value)

    def test_entity_invalid_json_structure(self, tmpdir):
        """Invalid json in any of the entity files should throw a Json Decode Error
        """
        for invalid_json in ["{", "[}]", '{"_id":1 "2":2}', "", " ", "[", "nothing"]:
            tmp_file_name = f"{tmpdir}/invalid_json.json"
            write_to_file(invalid_json, tmp_file_name)

            entity = Entity("user")

            with pytest.raises(json.decoder.JSONDecodeError):
                entity.load_data_build_indices_from_file(tmp_file_name)

            assert True

    def test_entity_missing_mandatory_key(self, tmpdir):
        """Missing '_id' in ANY data point should throw a ValueError
        """

        for empty_data in [
            "{}",
            "[{}]",
            json.dumps({"url": "https://test.com"}),
            json.dumps([{"_id": 1}, {"url": "https://test.com"}]),
        ]:
            tmp_file_name = f"{tmpdir}/missing_id.json"
            write_to_file(empty_data, tmp_file_name)

            entity = Entity("user")

            with pytest.raises(PrimaryKeyNotFoundError) as error:
                entity.load_data_build_indices_from_file(tmp_file_name)
            assert "Cannot find _id in the data point:" in str(error.value)

        assert True

    def test_entity_valid_data(self, tmpdir):
        """Testing with valid data should result in expected output, empty data [] should result in empty index
        {} is not valid as it doesn't have the primary key in it
        """
        test_io = {
            "[]": {"_id": {}},
            '{"_id": 1}': {"_id": {"1": {"_id": 1}}},
            '[{"_id": 1}]': {"_id": {"1": {"_id": 1}}},
            '[{"_id": 1, "d": 2}]': {"_id": {"1": {"_id": 1, "d": 2}}, "d": {2: [1]}},
        }
        for in_data in test_io:
            tmp_file_name = f"{tmpdir}/invalid_json.json"
            write_to_file(in_data, tmp_file_name)

            entity = Entity("user")

            entity.load_data_build_indices_from_file(tmp_file_name)

            assert test_io[in_data] == entity.indices

        assert True

    def test_custom_primary_key(self, tmpdir):
        """Custom primary key should use the given custom primary key
        """

        tmp_file_name = f"{tmpdir}/custom_prim_key.json"
        test_data = '[{"cid": 1}]'
        test_primary_key = "cid"

        expected_index = {"cid": {"1": {"cid": 1}}}

        write_to_file(test_data, tmp_file_name)
        entity = Entity("user", "cid")
        entity.load_data_build_indices_from_file(tmp_file_name)

        assert test_primary_key == entity.primary_key
        assert expected_index == entity.indices


class TestEntityEngineBuildIndices:
    def test_build_index_nonlist_data(self):
        """Valid data = [], [{"primary_key": }]
        Invalid data should throw a value error
        """
        invalid_input_data = [1, "a", {}, (), True, None, Entity("user")]

        for invalid_data_point in invalid_input_data:
            entity = Entity("ticket")
            with pytest.raises(ValueError) as error:
                entity._build_indices(invalid_data_point)
            assert (
                "Invalid entity data give found while trying to build indices. Data given to build indices should be a list() of dict()"
                == str(error.value)
            )
        assert True

    def test_build_index_missing_primary_key(self):
        """Missing primary key should throw an error
        """
        no_pkey_data = [[{}], [{"url": "https://test.com"}]]

        for no_pkey in no_pkey_data:
            entity = Entity("ticket")
            with pytest.raises(PrimaryKeyNotFoundError):
                entity._build_indices(no_pkey)
        assert True

    def test_build_index_valid_data(self):
        """Valid data should return valid indices
        if the data is
            - [] it should result in vanilla index
        """
        test_ticket_in_data = [
            [],
            [{"_id": 1, "name": "surya"}],
            [{"_id": 1, "name": "surya"}, {"_id": 2, "name": "surya"}],
            [
                {
                    "_id": "436bf9b0-1147-4c0a-8439-6f79833bff5b",
                    "url": "http://initech.zendesk.com/api/v2/tickets/436bf9b0-1147-4c0a-8439-6f79833bff5b.json",
                    "external_id": "9210cdc9-4bee-485f-a078-35396cd74063",
                }
            ],
        ]
        test_ticket_out_data = [
            {"_id": {}},
            {"_id": {"1": {"_id": 1, "name": "surya"}}, "name": {"surya": [1]}},
            {
                "_id": {
                    "1": {"_id": 1, "name": "surya"},
                    "2": {"_id": 2, "name": "surya"},
                },
                "name": {"surya": [1, 2]},
            },
            {
                "_id": {
                    "436bf9b0-1147-4c0a-8439-6f79833bff5b": {
                        "_id": "436bf9b0-1147-4c0a-8439-6f79833bff5b",
                        "url": "http://initech.zendesk.com/api/v2/tickets/436bf9b0-1147-4c0a-8439-6f79833bff5b.json",
                        "external_id": "9210cdc9-4bee-485f-a078-35396cd74063",
                    },
                },
                "url": {
                    "http://initech.zendesk.com/api/v2/tickets/436bf9b0-1147-4c0a-8439-6f79833bff5b.json": [
                        "436bf9b0-1147-4c0a-8439-6f79833bff5b"
                    ]
                },
                "external_id": {
                    "9210cdc9-4bee-485f-a078-35396cd74063": [
                        "436bf9b0-1147-4c0a-8439-6f79833bff5b"
                    ]
                },
            },
        ]

        for inp, out in zip(test_ticket_in_data, test_ticket_out_data):
            entity = Entity("ticket")
            entity._build_indices(inp)

            assert out == entity.indices

        assert True

    def test_build_index_blank_values(self):
        """Testing for corner cases, empty strings, spaces, empty lists as values in data fields
        """

        test_in_data = [
            [{"_id": ""}],
            [{"_id": " "}],
            [{"_id": 1, "tags": []}],
            [{"_id": "", "name": "surya"}],
        ]
        test_out_data = [
            {"_id": {"": {"_id": ""}}},
            {"_id": {" ": {"_id": " "}}},
            {"_id": {"1": {"_id": 1, "tags": []}}, "tags": {"": [1]}},
            {"_id": {"": {"_id": "", "name": "surya"}}, "name": {"surya": [""]}},
        ]

        for inp, out in zip(test_in_data, test_out_data):
            entity = Entity("organization")
            entity._build_indices(inp)
            assert out == entity.indices
        assert True

    def test_build_index_tags(self):
        """Test that when the data point has values that are a list we flatten them 
        """
        test_in_data = [
            [{"_id": 1, "tags": ["tag1", "tag2"]}],
            [{"_id": 1, "tags": []}],
        ]
        test_out_data = [
            {
                "_id": {"1": {"_id": 1, "tags": ["tag1", "tag2"]}},
                "tags": {"tag1": [1], "tag2": [1]},
            },
            {"_id": {"1": {"_id": 1, "tags": []}}, "tags": {"": [1]}},
        ]

        for inp, out in zip(test_in_data, test_out_data):
            entity = Entity("ticket")
            entity._build_indices(inp)
            assert out == entity.indices

        assert True

    def test_build_index_unhashable(self):
        """Unhashable values in data point's fields should throw TypeErrors
        """
        test_in_data = [
            [{"_id": 1, "unhash": set()}],
            [{"_id": 1, "tags": {}}],
        ]

        for inp in test_in_data:
            print(inp)
            entity = Entity("ticket")
            with pytest.raises(TypeError) as error:
                entity._build_indices(inp)
            assert "Unhashable value" in str(error.value)

        assert True

    def test_duplicate_primary_key(self):
        """Duplicate Primary Key throw an error
        """
        test_in_data = [{"_id": 1}, {"_id": 1}]
        for dup in test_in_data:
            entity = Entity("user")
            with pytest.raises(DuplicatePrimaryKeyError) as error:
                entity._build_indices(test_in_data)
                assert "Duplicate primary key value: " in str(error.value)
        assert True


class TestEntityEngineDataFromPrimaryKeys:
    def test_entity_match_list_primary_keys(self):
        users = [
            {"_id": 1, "name": "one"},
            {"_id": 2, "name": "two"},
            {"_id": 3, "name": "three"},
        ]
        entity = get_entity_from_formatted_data("user", users)
        assert users == list(entity.get_data_from_primary_keys([1, 2, 3]))
        assert users[:-1] == list(entity.get_data_from_primary_keys([1, 2]))

    def test_entity_no_match_list_primary_keys(self):
        users = [
            {"_id": 1, "name": "one"},
            {"_id": 2, "name": "two"},
            {"_id": 3, "name": "three"},
        ]
        entity = get_entity_from_formatted_data("user", users)
        assert [] == list(entity.get_data_from_primary_keys([0, -1, 99, "test", "1"]))

    def test_entity_match_single_primary_keys(self):
        users = [
            {"_id": 1, "name": "one"},
            {"_id": 2, "name": "two"},
            {"_id": 3, "name": "three"},
        ]
        entity = get_entity_from_formatted_data("user", users)
        assert [users[0]] == list(entity.get_data_from_primary_keys(1))
        assert [users[-1]] == list(entity.get_data_from_primary_keys(3))

    def test_entity_no_match_single_primary_keys(self):
        users = [
            {"_id": 1, "name": "one"},
            {"_id": 2, "name": "two"},
            {"_id": 3, "name": "three"},
        ]
        entity = get_entity_from_formatted_data("user", users)
        assert [] == list(entity.get_data_from_primary_keys(0))

    def test_entity_match_python_equality_paradox(self):
        """1.00 is treated same as 1.0 in python so having both of them in the code would raise an error
        TODO: Should we support this functionality
        """
        users = [
            {"_id": 1, "name": "one"},
            {"_id": 1.0, "name": "two"},
            {"_id": True, "name": "three"},
            {"_id": 1.01, "name": "four"},
        ]
        same = [1, 1.0, True, 1.01]
        entity = get_entity_from_formatted_data("user", users)

        for search_term, expected_out in zip(same, users):
            print(search_term)
            assert [expected_out] == list(
                entity.get_data_from_primary_keys(search_term)
            )

        assert True

    def test_entity_match_get_empty(self):
        users = [
            {"_id": 1, "name": "one"},
            {"_id": 2, "name": "two"},
            {"_id": 3, "name": "three"},
        ]

        entity = get_entity_from_formatted_data("user", users)

        assert [] == list(entity.get_data_from_primary_keys([]))
        assert [] == list(entity.get_data_from_primary_keys([None]))
        assert [] == list(entity.get_data_from_primary_keys(""))
        assert [] == list(entity.get_data_from_primary_keys(None))


class TestEntityEngineSearch:
    def test_entity_search(self):
        users = [
            {"_id": 1, "name": "one"},
            {"_id": 2, "name": "two"},
            {"_id": 3, "name": "three"},
        ]
        entity = get_entity_from_formatted_data("user", users)

        assert [] == list(entity.search("name", "2"))
        assert [users[1]] == list(entity.search("name", "two"))
        assert [] == list(entity.search("foo_index", "zero"))
        assert [users[2]] == list(entity.search("_id", 3))

    def test_entity_multi_search(self):
        users = [
            {"_id": 1, "name": "one"},
            {"_id": 2, "name": "two"},
            {"_id": 3, "name": "three"},
        ]
        entity = get_entity_from_formatted_data("user", users)

        assert [] == list(entity.search("name", "2"))
        assert [users[1]] == list(entity.search("name", "two"))
