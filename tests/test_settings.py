import pytest

from syw_site.settings import SettingsError, parse


def test_minimal(tmp_path):
    s = parse({"repo": "nstarman/x"}, tmp_path)
    assert (s.repo, s.publish, s.webapps, s.paper) == ("nstarman/x", False, (), {})


def test_full(tmp_path):
    (tmp_path / "webapps" / "globe").mkdir(parents=True)
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


def test_figure_icons(tmp_path):
    s = parse({"repo": "a/b", "figures": {"fig:a": {"icon": "top-left"}, "fig:b": {"icon": [0.8, 0.1], "image": 2}, "fig:c": {"icon": "none"}}}, tmp_path)
    assert s.icon("fig:a", "a").places == ("top-left",)
    assert (s.icon("fig:b", "b").places, s.icon("fig:b", "b").image) == (((0.8, 0.1),), 2)
    assert s.icon("fig:c", "c").places == ()
    assert s.icon("fig:zz", "zz").places == ("top-right",)  # the default
    assert s.icon("fig:zz", "zz").alpha == 0.6  # quiet by default


def test_one_portrait_per_panel(tmp_path):
    s = parse({"repo": "a/b", "figures": {"fig:rate": {"icon": ["top-right", [0.55, 0.18]], "alpha": 0.4}}}, tmp_path)
    assert s.icon("fig:rate", "rate").places == ("top-right", (0.55, 0.18))
    assert s.icon("fig:rate", "rate").alpha == 0.4


@pytest.mark.parametrize("spec", [{"icon": "middle"}, {"icon": [1.2, 0]}, {"icon": [0.5]}, {"image": 0}, {"where": "x"}, {"icon": ["top-right", "middle"]}, {"alpha": 0}, {"alpha": 2}])
def test_figure_icons_rejected(tmp_path, spec):
    with pytest.raises(SettingsError):
        parse({"repo": "a/b", "figures": {"fig:a": spec}}, tmp_path)


def test_explore(tmp_path):
    (tmp_path / "webapps" / "globe").mkdir(parents=True)
    s = parse({"repo": "a/b", "webapps": {"globe": {"explore": True, "title": "The globe", "text": "Drag it."}}}, tmp_path)
    assert (s.webapps[0].explore, s.webapps[0].title, s.webapps[0].text) == (True, "The globe", "Drag it.")
    with pytest.raises(SettingsError, match="explore"):
        parse({"repo": "a/b", "webapps": {"globe": {"explore": "yes"}}}, tmp_path)
