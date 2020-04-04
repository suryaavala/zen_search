from zensearch.entity_engine import Entity
from zensearch.utils import (
    get_entity_relationships,
    get_setup_entities,
    strtobool,
    get_user_input,
    get_entity_title,
    get_related_match_string,
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

    def get_all_matches(self, search_entity, search_term, search_value):
        current_entity_matches = self._get_matches_in_entity(
            search_entity, search_term, strtobool(search_value)
        )
        return (
            self._find_update_related_matches(search_entity, match)
            for match in current_entity_matches
        )

    def _get_matches_in_entity(self, search_entity, search_term, search_value):
        return self.entities_dict[search_entity].search(search_term, search_value)

    def _find_update_related_matches(self, current_entity, match):
        relationships_with_other_entities = get_entity_relationships(current_entity)
        for relationship in relationships_with_other_entities:
            search_entity = relationship["related_entity"]
            search_term = relationship["search_key_in_dependant"]
            search_value = match.get(relationship["search_key_in_current"], None)
            related_matches = self._get_matches_in_entity(
                search_entity, search_term, search_value
            )
            self._update_match_with_related(
                match, related_matches, search_entity, relationship["output_phrase"]
            )
        return match

    def _update_match_with_related(
        self, match, related_matches, related_entity, output_phrase
    ):
        title_field = get_entity_title(related_entity)
        for match_number, related_match in enumerate(related_matches):
            match_string = get_related_match_string(output_phrase, match_number)
            if related_match.get(title_field, None) is None:
                match[match_string] = related_match["_id"]
            else:
                match[match_string] = related_match[title_field]

        return

    def _get_searchable_fields(self):
        return {
            entity_name: self.entities_dict[entity_name].get_searchable_fields()
            for entity_name in self.entities_dict
        }

    def _get_entity_searchable_fields(self, entity_name):
        return self.entities_dict[entity_name].get_searchable_fields()
