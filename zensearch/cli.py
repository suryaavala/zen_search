from zensearch.zensearch import ZendeskSearch
from zensearch.utils import (
    get_user_input,
    get_entity_title,
)
from zensearch.config import (
    MESSAGE_HOME,
    MESSAGE_SELECT_ENTITY,
    MESSAGE_SELECT_TERM,
    MESSAGE_SELECT_VALUE,
    MESSAGE_INVALID_SELECTION,
    MESSAGE_DASHED_LINE,
    MESSAGE_BYE,
    SLEEP_TIMER,
)
import sys
from time import sleep
from itertools import count, chain


class CLI(ZendeskSearch):
    def __init__(self, entity_names, data_dir):
        self.entity_selection_to_name = {
            "1": "user",
            "2": "ticket",
            "3": "organization",
        }
        self.valid_choices = {
            "home": ["1", "2"],
            "entity": list(self.entity_selection_to_name.keys()),
        }
        super().__init__(entity_names=entity_names, data_dir=data_dir)

    def run(self, nb_iterations=-1):
        self._cli_home(nb_iterations)
        return

    def _cli_home(self, nb_iterations=-1):
        for current_iter in count():
            if nb_iterations == current_iter:
                break
            selected_home = get_user_input(MESSAGE_HOME)
            if self._is_valid_input_or_quit(selected_home, self.valid_choices["home"]):
                if selected_home == "1":
                    self._cli_select_entity()
                elif selected_home == "2":
                    self._print_searchable_fields()
            else:
                print(MESSAGE_INVALID_SELECTION)
                sleep(SLEEP_TIMER)

        return

    def _cli_select_entity(self):
        selected_entity = get_user_input(MESSAGE_SELECT_ENTITY)
        if self._is_valid_input_or_quit(selected_entity, self.valid_choices["entity"]):
            self._cli_select_term(self.entity_selection_to_name[selected_entity])
        else:
            print(MESSAGE_INVALID_SELECTION)
            sleep(SLEEP_TIMER)
        return

    def _cli_select_term(self, selected_entity):
        selected_term = get_user_input(MESSAGE_SELECT_TERM)
        if self._is_valid_input_or_quit(
            selected_term, super()._get_entity_searchable_fields(selected_entity),
        ):
            self._cli_select_value(selected_entity, selected_term)
        else:
            print(MESSAGE_INVALID_SELECTION)
            sleep(SLEEP_TIMER)
        return

    def _cli_select_value(self, selected_entity, selected_term):
        selected_value = get_user_input(MESSAGE_SELECT_VALUE)
        if self._is_valid_input_or_quit(selected_value, "*"):
            all_matches = super().get_all_matches(
                selected_entity, selected_term, selected_value
            )
            self._print_matches(all_matches)

        # else:
        #     print(MESSAGE_INVALID_SELECTION)
        #     sleep(SLEEP_TIMER)
        return

    def _is_valid_input_or_quit(self, selected, choices):
        if selected == "quit":
            print(MESSAGE_BYE)
            sys.exit(0)
        elif choices == "*":
            return True
        elif selected in choices:
            return True
        else:
            return False

    def _print_searchable_fields(self):
        names_fields = super()._get_searchable_fields()
        for entity_name in names_fields:
            print(MESSAGE_DASHED_LINE)
            print(f"Search {entity_name.title()}s with")
            print("\n".join(names_fields[entity_name]))
            print("\n")
        return

    def _print_matches(self, matches):
        try:
            first_match = next(matches)
        except StopIteration:
            print("No results found")
            return
        else:
            all_matches = chain([first_match], matches)
            for match in all_matches:
                for field in match:
                    print("{0:28}  {1}".format(field, match[field]))
            return
