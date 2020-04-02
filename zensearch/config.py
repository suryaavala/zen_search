RELATIONSHIPS = {
    "user": {
        "organization": [
            {
                "search_key_in_dependant": "_id",
                "search_key_in_current": "organization_id",
                "output_phrase": "organization_name",
            },
        ],
        "ticket": [
            {
                "search_key_in_dependant": "assignee_id",
                "search_key_in_current": "_id",
                "output_phrase": "assigned_ticket",
            },
            {
                "search_key_in_dependant": "submitter_id",
                "search_key_in_current": "_id",
                "output_phrase": "submitted_ticket",
            },
        ],
    },
    "ticket": {
        "organization": [
            {
                "search_key_in_dependant": "_id",
                "search_key_in_current": "organization_id",
                "output_phrase": "organization_name",
            },
        ],
        "user": [
            {
                "search_key_in_dependant": "assignee_id",
                "search_key_in_current": "_id",
                "output_phrase": "assigned_ticket",
            },
            {
                "search_key_in_dependant": "submitter_id",
                "search_key_in_current": "_id",
                "output_phrase": "submitted_ticket",
            },
        ],
    },
    "organization": {
        "user": [
            {
                "search_key_in_dependant": "organization_id",
                "search_key_in_current": "_id",
                "output_phrase": "user",
            },
        ],
        "ticket": [
            {
                "search_key_in_dependant": "organization_id",
                "search_key_in_current": "_id",
                "output_phrase": "ticket",
            },
        ],
    },
}


MESSAGE_HOME = """-------------------------------------------------
Welcome to Zendesk Search
Type 'quit' to exit at any time, Press 'Enter' to continue


        Select search options:
         * Press 1 to search Zendesk
         * Press 2 to view a list of searchable fields
         * Type 'quit' to exit

"""

MESSAGE_SELECT_ENTITY = """Select 1) Users or 2) Tickets or 3) Organizations
"""

MESSAGE_SELECT_TERM = """Enter search term
"""

MESSAGE_SELECT_VALUE = """Enter search value
"""

MESSAGE_INVALID_SELECTION = """Invalid selection, try again!


"""
MESSAGE_DASHED_LINE = """-------------------------------------------------"""


SLEEP_TIMER = 0
