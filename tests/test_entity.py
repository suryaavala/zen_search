import pytest
import isort
import json

import os
from zensearch.entity import Entity


class TestEntity:
    def test_read_module(self):
        with open("tests/test_data_raw_users.json", "r") as user_file:
            users = json.load(user_file)
        assert len(users), 75
