import os

from zensearch.cli import CLI


def main(nb_iterations=-1, data_dir="./data/import/", *args, **kwargs):
    cli = CLI(
        entity_names=["user", "ticket", "organization"],
        data_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), data_dir),
    )
    cli.run(nb_iterations)
    return


if __name__ == "__main__":
    import argparse

    argp = argparse.ArgumentParser(
        prog="zensearch",
        description="Searches through ticketing data (user, organization and ticket data) to find relevant matches as per the search selection",
    )
    argp.add_argument(
        "-d",
        "--datadir",
        required=False,
        default="./data/import/",
        help="Relative Path (relative to this main.py file) to data directory containing data files (*user*.json, *ticket*.json, *organization*.json), default './data/import/'",
    )
    argp.add_argument(
        "-n",
        "--number",
        required=False,
        default=-1,
        help="Number of interations to run the program/search for, default is forever(-1) - (invalid selection is also counted as  an interation)",
    )

    options = argp.parse_args()
    main(
        nb_iterations=int(options.number), data_dir=options.datadir,
    )
