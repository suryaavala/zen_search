"""Profiler script that was used to generate pstat report under ./docs/performance
After commenting relevant sections this can be run as `python3 -m cProfile -o <reportname> profiler_scripty.py` from root dir of the repo
"""
from unittest.mock import patch

from zensearch.cli import CLI
from zensearch.zensearch import ZendeskSearch

cli_10000 = CLI(entity_names=["user", "ticket", "organization"], data_dir="./data/gen")
with patch("builtins.input", side_effect=[1, 1, "signature", "Don't Worry Be Happy!"]):
    cli_10000.run(1)


cli_75 = CLI(entity_names=["user", "ticket", "organization"], data_dir="./data/gen")
with patch("builtins.input", side_effect=[1, 1, "signature", "Don't Worry Be Happy!"]):
    cli_75.run(1)


zen_10000 = ZendeskSearch(
    entity_names=["user", "ticket", "organization"], data_dir="./data/import"
)
matches_10000 = zen_10000.get_all_matches("user", "signature", "Don't Worry Be Happy!")
matches_list_10000 = list(matches_10000)

zen_75 = ZendeskSearch(
    entity_names=["user", "ticket", "organization"], data_dir="./data/gen"
)
matches_75 = zen_75.get_all_matches("user", "signature", "Don't Worry Be Happy!")
matches_list_75 = list(matches_75)
