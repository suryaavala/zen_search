# import json

# from zensearch.entity_engine import Entity

# with open(
#     "/Users/surya/Development/surya/zen_search/specs/users.json", "r"
# ) as user_file:
#     data = json.load(user_file)

# users = Entity("user")

# users._build_indices(data)

# idz = users.indices

# with open(
#     "/Users/surya/Development/surya/zen_search/data/out/user_update_index.json", "w",
# ) as f:
#     json.dump(idz, f)

from zensearch.zensearch import ZendeskSearch


def main(*args, **kwargs):
    zen = ZendeskSearch(data_dir="./data/import/")
    zen.cli()
    return


if __name__ == "__main__":
    main()
