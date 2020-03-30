class Entity:
    def __init__(self, primary_key="_id"):
        # indices["_id"] = {1: d, 2: d}
        self.primary_key = primary_key
        self.indices = {self.primary_key: {}}

    def build_indices(self, data):
        for item in data:
            primary_key = item[self.primary_key]
            for field in item:
                if field == self.primary_key:
                    self.indices[field][item[field]] = item
                    continue
                # if field is a list in itself, then we build index on each of those elements - sorta like one hot encoding
                if isinstance(item[field], list) or isinstance(item[field], tuple):
                    for idx, sub_field in enumerate(item[field]):
                        self._index(primary_key, sub_field, item[field][idx])
                else:
                    self._index(primary_key, field, item[field])
        return

    def _index(self, primary_key_value, field, value):
        # if the index exist then look for the value in the index
        if self.indices.get(field, None):
            # if the value in the index exist as well, then append the item to the list
            if self.indices[field].get(value, None):
                self.indices[field][value].append(primary_key_value)
            # if the value in the index DOES NOT exist, then create a new list with value as it's first and only item
            else:
                self.indices[field][value] = [primary_key_value]
        # if the index does not exist, create index and add the item as it's first and only item
        else:
            self.indices[field] = {value: [primary_key_value]}
        return


if __name__ == "__main__":
    import json

    with open(
        "/Users/surya/Development/surya/zen_search/specs/users.json", "r"
    ) as user_file:
        data = json.load(user_file)

    users = Entity()

    users.build_indices(data)

    idz = users.indices

    with open(
        "/Users/surya/Development/surya/zen_search/data/out/user_index.json", "w"
    ) as f:
        json.dump(idz, f)
