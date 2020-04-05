from main import main
import pytest
from unittest.mock import patch
from zensearch.config import MESSAGE_BYE
from zensearch.cli import CLI
import os


def get_quit_sequences():
    return [
        [1, "quit"],
        [1, 1, "quit"],
        [1, 1, 1, "quit"],
        [1, 1, 1, "_id", "quit"],
        [1, 1, 2, "quit"],
        [1, 1, 2, "_id", "quit"],
        [1, 1, 3, "quit"],
        [1, 1, 3, "_id", "quit"],
    ]


@pytest.fixture
def test_data_dir():
    return f"{os.path.dirname(os.path.abspath(__file__))}/test_data/"


@pytest.fixture
def cli(test_data_dir):
    return CLI(entity_names=["user", "ticket", "organization"], data_dir=test_data_dir)


def test_cli_happy_path(cli, capsys):
    with patch("builtins.input", side_effect=[1, 1, "_id", 71]):
        cli.run(1)
    out, err = capsys.readouterr()
    assert (
        out
        == "_id                           71\nurl                           http://initech.zendesk.com/api/v2/users/71.json\nexternal_id                   c972bb41-94aa-4f20-bc93-e63dbfe8d9ca\nname                          Prince Hinton\nalias                         Miss Dana\ncreated_at                    2016-04-18T11:05:43 -10:00\nactive                        True\nverified                      False\nshared                        False\nlocale                        zh-CN\ntimezone                      Samoa\nlast_login_at                 2013-05-01T01:18:48 -10:00\nemail                         danahinton@flotonic.com\nphone                         9064-433-892\nsignature                     Don't Worry Be Happy!\norganization_id               121\ntags                          ['Davenport', 'Cherokee', 'Summertown', 'Clinton']\nsuspended                     False\nrole                          agent\norganization_name             Hotcâkes\nticket_assigned               A Catastrophe in Sierra Leone\nsubmitted_ticket              A Catastrophe in Micronesia\nsubmitted_ticket_2            A Drama in Wallis and Futuna Islands\nsubmitted_ticket_3            A Drama in Australia\n-------------------------------------------------\n"
    )


class TestCliCore:
    @pytest.mark.parametrize("data_set", get_quit_sequences())
    def test_quit(self, data_set, capsys):
        with patch("builtins.input", side_effect=data_set[1:]):
            with pytest.raises(SystemExit) as sys_exit:
                main(data_set[0])

        out, err = capsys.readouterr()
        print(out, err)
        assert sys_exit.value.code == 0
        assert out.strip() == MESSAGE_BYE

    def test_cli_struct(self, cli):
        """Test to see if cli instantiates with 
                entity_selection_to_name
                valid_choices
                run
                _cli_home
                _cli_select_term
                _cli_select_value
                _is_valid_input_or_quit
                _print_searchable_fields
                _print_matches
        """
        assert hasattr(cli, "entity_selection_to_name")
        assert hasattr(cli, "valid_choices")
        assert hasattr(cli, "run")
        assert hasattr(cli, "_cli_home")
        assert hasattr(cli, "_cli_select_term")
        assert hasattr(cli, "_cli_select_value")
        assert hasattr(cli, "_is_valid_input_or_quit")
        assert hasattr(cli, "_print_searchable_fields")
        assert hasattr(cli, "_print_matches")

    def test_cli_run_terminates(self, capsys, cli):
        for nb_iterations in range(10):
            with patch("builtins.input", side_effect=[5] * nb_iterations):
                cli.run(nb_iterations)
            out, err = capsys.readouterr()

            assert (
                out.replace("\n", "").split("!")[:-1]
                == ["Invalid selection, try again"] * nb_iterations
            )


class TestCliHome:
    def test_cli_home_terminates(self, capsys, cli):
        for nb_iterations in range(10):
            with patch("builtins.input", side_effect=[5] * nb_iterations):
                cli._cli_home(nb_iterations)
            out, err = capsys.readouterr()

            assert (
                out.replace("\n", "").split("!")[:-1]
                == ["Invalid selection, try again"] * nb_iterations
            )

    def test_cli_home_searchable_fields(self, capsys, cli):
        for nb_iterations in range(10):
            with patch("builtins.input", side_effect=[2]):
                cli._cli_home(1)
            out, err = capsys.readouterr()
            fields = [
                "-------------------------------------------------",
                "Search Users with",
                "_id",
                "organization_id",
                "active",
                "suspended",
                "shared",
                "email",
                "url",
                "signature",
                "external_id",
                "phone",
                "last_login_at",
                "tags",
                "verified",
                "timezone",
                "alias",
                "created_at",
                "role",
                "locale",
                "name",
                "-------------------------------------------------",
                "Search Tickets with",
                "_id",
                "external_id",
                "subject",
                "organization_id",
                "tags",
                "priority",
                "submitter_id",
                "due_at",
                "created_at",
                "has_incidents",
                "status",
                "via",
                "description",
                "type",
                "assignee_id",
                "url",
                "-------------------------------------------------",
                "Search Organizations with",
                "_id",
                "external_id",
                "shared_tickets",
                "details",
                "created_at",
                "tags",
                "url",
                "name",
                "domain_names",
            ]
            outlist = list(
                filter(
                    lambda x: x.strip() not in [None, "\n", " ", ""], out.split("\n"),
                )
            )
            outlist.sort()
            fields.sort()
            assert outlist == fields


class TestInvalidSelections:
    def test_cli_home_invalid_selection(self, capsys, cli):
        with patch("builtins.input", side_effect=[5]):
            cli._cli_home(1)
        out, err = capsys.readouterr()
        assert out.replace("\n", "").split("!")[:-1] == ["Invalid selection, try again"]

    def test_cli_select_entity_invalid_selection(self, capsys, cli):
        with patch("builtins.input", side_effect=[5]):
            cli._cli_select_entity()
        out, err = capsys.readouterr()
        assert out.replace("\n", "").split("!")[:-1] == ["Invalid selection, try again"]

    def test_cli_select_term_invalid_selection(self, capsys, cli):
        with patch("builtins.input", side_effect=[5]):
            cli._cli_select_term("user")
        out, err = capsys.readouterr()
        assert out.replace("\n", "").split("!")[:-1] == ["Invalid selection, try again"]

    def test_cli_select_value_no_invalid_selection(self, capsys, cli):
        with patch("builtins.input", side_effect=[""]):
            cli._cli_select_value("user", "_id")
        out, err = capsys.readouterr()
        assert out == "No results found\n"
