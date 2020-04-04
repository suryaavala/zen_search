from zensearch.cli import CLI
import os


def main(nb_iterations=-1, *args, **kwargs):
    cli = CLI(
        entity_names=["user", "ticket", "organization"],
        data_dir=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "./data/import/"
        ),
    )
    cli.run(nb_iterations)
    return


if __name__ == "__main__":
    main()
