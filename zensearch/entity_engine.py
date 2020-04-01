import json
import collections
from zensearch.exceptions import PrimaryKeyNotFoundError, DuplicatePrimaryKeyError


class Entity:
    """Entity class to represent entities such as users, tickets and organizations
    """

    def __init__(self, entity_name, primary_key="_id"):
        # indices["_id"] = {1: user1, 2: user2}
        self.entity_name = entity_name
        self.primary_key = primary_key
        self._indices = {self.primary_key: {}}
        self._data = []

    def _build_indices(self):
        if self._data == []:
            # return if data is []
            return
        # if not isinstance(self._data, list):
        #     raise ValueError(
        #         f"Invalid entity data give found while trying to build indices. Data given to build indices should be a list() of dict()"
        #     )
        for data_point in self._data:
            self._check_for_mandatory_keys(data_point)
            primary_key = data_point[self.primary_key]

            for field in data_point:
                # if field is primary_key, then we link the data point itself directly to the (primary_key) index key (=data point primary key value)
                if field == self.primary_key:
                    # throw an error if/when a primary key has already been seen
                    if self._indices[field].get(str(data_point[field]), None):
                        raise DuplicatePrimaryKeyError(
                            f"Duplicate primary key value: {data_point[field]} found in the data point. It's been assumed that every entity should have a unique set of primary keys"
                        )
                    self._indices[field][str(data_point[field])] = data_point
                # if the data point's field value is unhashable, then raise an TypeError
                elif not isinstance(
                    data_point[field], collections.abc.Hashable
                ) and not isinstance(data_point[field], list):
                    raise TypeError(
                        f"Unhashable value {data_point[field]} found in field: {field} for data point: {data_point}"
                    )
                # if field is a list in itself, then we flatten it and use each of those item items as a value
                elif isinstance(data_point[field], list) or isinstance(
                    data_point[field], tuple
                ):
                    if len(data_point[field]) == 0:
                        self.__update_non_primary_index(primary_key, field, "")
                    else:
                        for idx, sub_field in enumerate(data_point[field]):
                            self.__update_non_primary_index(
                                primary_key, field, sub_field
                            )
                else:
                    self.__update_non_primary_index(
                        primary_key, field, data_point[field]
                    )
        return

    def __update_non_primary_index(self, primary_key_value, index_name, data_value):
        # if the index_name exist then look for the data_value in the index
        if self._indices.get(index_name, None):
            # if the data_value in the index exist as well, then append the data_point to the list
            if self._indices[index_name].get(data_value, None):
                self._indices[index_name][data_value].append(primary_key_value)
            # if the value in the index DOES NOT exist, then create a new list with value as it's first and only data_point
            else:
                self._indices[index_name][data_value] = [primary_key_value]
        # if the index does not exist, create index and add the data_point as it's first and only data_point
        else:
            self._indices[index_name] = {data_value: [primary_key_value]}

        return

    def search(self, search_key, search_term):
        if search_key == self.primary_key:
            return self.get_data_from_primary_keys(search_term)
        elif self._indices.get(search_key, None) is None:
            return []
        else:
            return self.get_data_from_primary_keys(
                self._indices[search_key].get(search_term, None)
            )

    def load_data_build_indices(self, data_to_load):

        if isinstance(data_to_load, str):
            with open(data_to_load, "r") as f:
                data_red = json.load(f)
            if isinstance(data_red, dict):
                data_red = [data_red]
        # data is a data point
        elif isinstance(data_to_load, dict):
            data_red = [data_to_load]
            # raise SyntaxWarning(
            #     "Recieved a dict, so assuming it is a data point. Data inside the file should be a list of data points(dicts)."
            # )
        elif isinstance(data_to_load, list):
            data_red = data_to_load
        else:
            raise TypeError(
                "Data to load should be one of file path as str(), data point as dict() or data as list of data point()"
            )
        self._data = data_red
        self._build_indices()
        return

    def _check_for_mandatory_keys(self, data_point):
        mandatory_keys = [self.primary_key]

        for key in mandatory_keys:
            if data_point.get(key, None) is None:
                raise PrimaryKeyNotFoundError(
                    f"Cannot find {key} in the data point: {data_point}. Every {self.entity_name} should at least have {mandatory_keys}"
                )
        return

    def get_data_from_primary_keys(self, search_keys):
        if not isinstance(search_keys, list):
            search_keys = [search_keys]
        # matches = []
        # for key in search_keys:

        #     data_point = self._indices[self.primary_key].get(key, None)
        #     print(key, data_point)

        #     if data_point:
        #         matches.append(data_point)
        matches = (
            self._indices[self.primary_key][str(key)]
            for key in search_keys
            if self._indices[self.primary_key].get(str(key), None)
            and self._indices[self.primary_key][str(key)][self.primary_key] == key
        )
        return matches
