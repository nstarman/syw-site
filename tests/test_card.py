import pytest

from syw_site.card import command
from syw_site.settings import SettingsError, parse


def test_command_runs_the_website_collector(tmp_path):
    assert command(parse({"repo": "a/b", "website_id": "stream-convexity-spatial"}, tmp_path)) == [
        "node", "scripts/card.mjs", "stream-convexity-spatial",
    ]


def test_needs_a_website_id(tmp_path):
    with pytest.raises(SettingsError, match="website_id"):
        command(parse({"repo": "a/b"}, tmp_path))
