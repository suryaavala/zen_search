# script that copies all the data under ./data to ./tests/
import os
from shutil import copyfile


def get_new_name(abs_src):
    rel_path = os.path.relpath(abs_src)
    new_name = f"test_{rel_path}".replace("/", "_")
    return new_name


def cp_file(src, dst):
    print(f"copying from {os.path.join(src)} ---> {os.path.join(dst)} ")
    copyfile(src, dst)
    return


def cp(src, dst):
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)

    if os.path.isfile(src):
        cp_file(src, dst)
        return

    for listing in os.listdir(src):
        if listing.startswith("."):
            continue

        abs_listing = os.path.join(src, listing)

        if os.path.isfile(abs_listing):
            new_name = get_new_name(abs_listing)
            cp_file(abs_listing, os.path.join(dst, new_name))
        elif os.path.isdir(abs_listing):
            cp(abs_listing, dst)
    return


if __name__ == "__main__":
    cp("./data/", "tests/")
