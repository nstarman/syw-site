import pytest

from syw_site.settings import SettingsError, parse


def test_minimal(tmp_path):
    s = parse({"repo": "nstarman/x"}, tmp_path)
    assert (s.repo, s.publish, s.webapps, s.paper) == ("nstarman/x", False, (), {})


def test_full(tmp_path):
    (tmp_path / "webapps" / "globe").mkdir(parents=True)
    (tmp_path / "data.npz").touch()
    s = parse(
        {"repo": "a/b", "website_id": 2026, "publish": True, "paper": {"arxiv": 2610.1},
         "webapps": {"globe": {"inputs": ["data.npz"], "figure": "fig:a"}}},
        tmp_path,
    )
    assert s.website_id == "2026" and s.publish and s.paper == {"arxiv": "2610.1"}
    assert s.webapps[0].name == "globe" and s.webapps[0].inputs == ("data.npz",) and s.webapps[0].figure == "fig:a"


@pytest.mark.parametrize(
    "raw, match",
    [
        ({}, "repo"),
        ({"repo": "nope"}, "repo"),
        ({"repo": "a/b", "extra": 1}, "unknown keys"),
        ({"repo": "a/b", "publish": "yes"}, "publish"),
        ({"repo": "a/b", "paper": {"isbn": 1}}, "paper"),
        ({"repo": "a/b", "webapps": {"Bad_Name": {}}}, "webapp name"),
        ({"repo": "a/b", "webapps": {"globe": {}}}, "no webapps/globe/"),
    ],
)
def test_rejects(tmp_path, raw, match):
    with pytest.raises(SettingsError, match=match):
        parse(raw, tmp_path)


def test_inputs_may_not_exist_yet(tmp_path):
    (tmp_path / "webapps" / "globe").mkdir(parents=True)
    s = parse({"repo": "a/b", "webapps": {"globe": {"inputs": ["src/data/made_by_a_rule.npz"]}}}, tmp_path)
    assert s.webapps[0].inputs == ("src/data/made_by_a_rule.npz",)
