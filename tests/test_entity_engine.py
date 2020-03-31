import json
import os

import pytest
from zensearch.entity_engine import Entity
from zensearch.exceptions import PrimaryKeyNotFoundError, DuplicatePrimaryKeyError


def write_to_file(content, file_name):
    with open(file_name, "w") as f:
        f.write(str(content))
    return


class TestEntityEngine:
    def test_entity_struct(self):
        """Test to see if Entity instantiates with 
                a primary key
                alteast an index on primary key
                _build_indices 
                load_data_from_file
                search
        """
        ent = Entity("user")

        assert ent.primary_key == "_id"
        assert ent.indices == {"_id": {}}
        assert hasattr(ent, "_build_indices")
        assert hasattr(ent, "load_data_from_file")
        assert hasattr(ent, "search")


class TestEntityEngineLoadData:
    def test_entity_invalid_file(self):
        """Test for a FileNotFoundError when an empty string or invalid path to file is given
        """
        ent = Entity("user")

        with pytest.raises(FileNotFoundError) as error:
            ent.load_data_from_file("nofile.txt")
        assert "[Errno 2] No such file or directory:" in str(error.value)

    def test_entity_invalid_json_structure(self, tmpdir):
        """Invalid json in any of the entity files should throw a Json Decode Error
        """
        for invalid_json in ["{", "[}]", '{"_id":1 "2":2}', "", " ", "[", "nothing"]:
            tmp_file_name = f"{tmpdir}/invalid_json.json"
            write_to_file(invalid_json, tmp_file_name)

            ent = Entity("user")

            with pytest.raises(json.decoder.JSONDecodeError):
                ent.load_data_from_file(tmp_file_name)

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

            ent = Entity("user")

            with pytest.raises(PrimaryKeyNotFoundError) as error:
                ent.load_data_from_file(tmp_file_name)
            assert "Cannot find _id in the data point:" in str(error.value)

        assert True

    def test_entity_valid_data(self, tmpdir):
        """Testing with valid data should result in expected output, empty data [] should result in empty index
        {} is not valid as it doesn't have the primary key in it
        """
        test_io = {
            "[]": {"_id": {}},
            '{"_id": 1}': {"_id": {1: {"_id": 1}}},
            '[{"_id": 1}]': {"_id": {1: {"_id": 1}}},
            '[{"_id": 1, "d": 2}]': {"_id": {1: {"_id": 1, "d": 2}}, "d": {2: [1]}},
        }
        for in_data in test_io:
            tmp_file_name = f"{tmpdir}/invalid_json.json"
            write_to_file(in_data, tmp_file_name)

            ent = Entity("user")

            ent.load_data_from_file(tmp_file_name)

            assert test_io[in_data] == ent.indices

        assert True

    def test_custom_primary_key(self, tmpdir):
        """Custom primary key should use the given custom primary key
        """

        tmp_file_name = f"{tmpdir}/custom_prim_key.json"
        test_data = '[{"cid": 1}]'
        test_primary_key = "cid"

        expected_index = {"cid": {1: {"cid": 1}}}

        write_to_file(test_data, tmp_file_name)
        ent = Entity("user", "cid")
        ent.load_data_from_file(tmp_file_name)

        assert test_primary_key == ent.primary_key
        assert expected_index == ent.indices


class TestEntityEngineBuildIndices:
    def test_build_index_nonlist_data(self):
        """Valid data = [], [{"primary_key": }]
        Invalid data should throw a value error
        """
        invalid_input_data = [1, "a", {}, (), True, None, Entity("user")]

        for invalid_data_point in invalid_input_data:
            ent = Entity("ticket")
            with pytest.raises(ValueError) as error:
                ent._build_indices(invalid_data_point)
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
            ent = Entity("ticket")
            with pytest.raises(PrimaryKeyNotFoundError):
                ent._build_indices(no_pkey)
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
            {"_id": {1: {"_id": 1, "name": "surya"}}, "name": {"surya": [1]}},
            {
                "_id": {1: {"_id": 1, "name": "surya"}, 2: {"_id": 2, "name": "surya"}},
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
            ent = Entity("ticket")
            ent._build_indices(inp)

            assert out == ent.indices

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
            {"_id": {1: {"_id": 1, "tags": []}}, "tags": {"": [1]}},
            {"_id": {"": {"_id": "", "name": "surya"}}, "name": {"surya": [""]}},
        ]

        for inp, out in zip(test_in_data, test_out_data):
            ent = Entity("organization")
            ent._build_indices(inp)
            assert out == ent.indices
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
                "_id": {1: {"_id": 1, "tags": ["tag1", "tag2"]}},
                "tags": {"tag1": [1], "tag2": [1]},
            },
            {"_id": {1: {"_id": 1, "tags": []}}, "tags": {"": [1]}},
        ]

        for inp, out in zip(test_in_data, test_out_data):
            ent = Entity("ticket")
            ent._build_indices(inp)
            assert out == ent.indices

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
            ent = Entity("ticket")
            with pytest.raises(TypeError) as error:
                ent._build_indices(inp)
            assert "Unhashable value" in str(error.value)

        assert True

    def test_duplicate_primary_key(self):
        """Duplicate Primary Key throw an error
        """
        test_in_data = [{"_id": 1}, {"_id": 1}]
        for dup in test_in_data:
            ent = Entity("user")
            with pytest.raises(DuplicatePrimaryKeyError) as error:
                ent._build_indices(test_in_data)
                assert "Duplicate primary key value: " in str(error.value)
        assert True


class TestEntityEngineSearch:
    def test_entity_search(self):
        assert Entity("user").search("_id", "1") is None
