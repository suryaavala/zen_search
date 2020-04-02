from zensearch.entity_engine import Entity
from zensearch.utils import (
    get_entity_relationships,
    get_setup_entities,
    strtobool,
    get_user_input,
    get_entity_titile,
)
from zensearch.config import (
    MESSAGE_HOME,
    MESSAGE_SELECT_ENTITY,
    MESSAGE_SELECT_TERM,
    MESSAGE_SELECT_VALUE,
    MESSAGE_INVALID_SELECTION,
    MESSAGE_DASHED_LINE,
    SLEEP_TIMER,
)
import sys
from time import sleep


class ZendeskSearch:
    def __init__(
        self, entity_names, data_dir,
    ):
        self.entities_dict = get_setup_entities(entity_names, data_dir)
        self.entity_selection_to_name = {
            "1": "user",
            "2": "ticket",
            "3": "organization",
        }
        self.valid_choices = {"home": ["1", "2"], "entity": ["1", "2", "3"]}

    def cli(self):
        while True:
            home_selection = get_user_input(MESSAGE_HOME)
            if self._is_valid_input_or_quit(home_selection, self.valid_choices["home"]):
                if home_selection == "1":
                    self._select_entity()
                elif home_selection == "2":
                    self._print_searchable_fields()
            else:
                print(MESSAGE_INVALID_SELECTION)
                sleep(SLEEP_TIMER)

        return

    def _select_entity(self):
        entity_selection = get_user_input(MESSAGE_SELECT_ENTITY)
        if self._is_valid_input_or_quit(
            entity_selection, self.entity_selection_to_name.keys()
        ):
            self._select_term(self.entity_selection_to_name[entity_selection])
        else:
            print(MESSAGE_INVALID_SELECTION)
            sleep(SLEEP_TIMER)
        return

    def _select_term(self, entity_name):
        search_term_selection = get_user_input(MESSAGE_SELECT_TERM)
        if self._is_valid_input_or_quit(
            search_term_selection,
            self.entities_dict[entity_name].get_searchable_fields(),
        ):
            self._select_value(entity_name, search_term_selection)
        else:
            print(MESSAGE_INVALID_SELECTION)
            sleep(SLEEP_TIMER)
        return

    def _select_value(self, entity_name, search_term):
        search_value_selection = get_user_input(MESSAGE_SELECT_VALUE)
        if self._is_valid_input_or_quit(search_value_selection, "*"):
            matches = self.entities_dict[entity_name].search(
                search_term, strtobool(search_value_selection)
            )
            self.__search_related_and_print(entity_name, matches)
        else:
            print(MESSAGE_INVALID_SELECTION)
            sleep(SLEEP_TIMER)
        return

    def __search_related_and_print(self, entity_name, matches):
        for match in matches:
            self.__print_a_match(match)
            self.__search_related_from_match(entity_name, match)
        return

    def __search_related_from_match(self, entity_name, match):
        relationships_with_other_entities = get_entity_relationships(entity_name)
        for related_entity in relationships_with_other_entities:
            for relationship in relationships_with_other_entities[related_entity]:
                search_term = relationship["search_key_in_dependant"]
                search_value = match[relationship["search_key_in_current"]]
                matches = self.entities_dict[related_entity].search(
                    search_term, strtobool(search_value)
                )
                self.__print_dependant_matches(
                    matches,
                    related_entity,
                    default_field_phrase=relationship["output_phrase"],
                )
        return

    def __print_dependant_matches(self, matches, current_entity, default_field_phrase):
        title_field = get_entity_titile(current_entity)
        for m_number, match in enumerate(matches):
            # empty_spaces = 28 - len(str(m_number))
            if m_number != 0:
                print_field_phrase = f"{default_field_phrase}_{m_number+1}"
            else:
                print_field_phrase = default_field_phrase
            print("{0:28}  {1}".format(print_field_phrase, match[title_field]))
        return

    def __print_a_match(self, match):
        for field in match:
            print("{0:28}  {1}".format(field, match[field]))
        return

    def _print_searchable_fields(self):
        for entity_name in self.entities_dict:
            print(MESSAGE_DASHED_LINE)
            print(f"Search {entity_name.title()}s with")
            print("\n".join(self.entities_dict[entity_name].get_searchable_fields()))
            print("\n")
        return

    def _is_valid_input_or_quit(self, selected, choices):
        if selected == "quit":
            sys.exit("Bye!")
        elif selected in choices:
            return True
        elif choices == "*":
            return True
        else:
            return False
