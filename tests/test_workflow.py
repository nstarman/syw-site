"""The publish guard of the docs.yml a paper gets (Principle IV, SC-003)."""

from importlib import resources

import yaml

WORKFLOW = yaml.safe_load((resources.files("syw_site") / "template" / "workflows" / "docs.yml").read_text())
MAIN_PUSH = "github.event_name == 'push' && github.ref == 'refs/heads/main'"


def steps():
    return WORKFLOW["jobs"]["build"]["steps"]


def test_only_the_publish_path_uploads_and_deploys():
    uploads = [s for s in steps() if "upload" in s.get("uses", "")]
    assert len(uploads) == 1
    assert "steps.settings.outputs.publish == 'true'" in uploads[0]["if"] and MAIN_PUSH in uploads[0]["if"]
    assert "!github.event.repository.private" in uploads[0]["if"]
    deploy = WORKFLOW["jobs"]["deploy"]
    assert "needs.build.outputs.publish == 'true'" in deploy["if"] and MAIN_PUSH in deploy["if"]
    assert "!github.event.repository.private" in deploy["if"]
    for name, job in WORKFLOW["jobs"].items():
        for s in job.get("steps", []):
            if s.get("uses", "").startswith(("actions/upload", "actions/deploy")):
                assert s.get("if") or job.get("if"), f"{name}: an unguarded upload or deploy"


def test_private_repo_guard_runs_before_upload():
    names = [s.get("name", "") for s in steps()]
    guard = names.index("Refuse to publish from a private repository")
    assert guard < names.index("Upload the site for Pages")
    assert "github.event.repository.private" in steps()[guard]["if"]
    assert "exit 1" in steps()[guard]["run"]


def test_tokens_and_timeout():
    build = WORKFLOW["jobs"]["build"]
    assert build["timeout-minutes"] <= 180
    step = next(s for s in build["steps"] if s.get("name") == "Build the paper and its docs site")
    assert step["env"] == {"SANDBOX_TOKEN": "${{ secrets.SANDBOX_TOKEN }}"}
    assert "OVERLEAF_TOKEN" not in str(WORKFLOW)  # a docs build never syncs with Overleaf


def test_checkout_brings_submodules_and_history():
    (checkout,) = [s for s in steps() if s.get("uses", "").startswith("actions/checkout")]
    assert checkout["with"] == {"fetch-depth": 0, "submodules": "recursive"}


CARD = yaml.safe_load((resources.files("syw_site") / "template" / "workflows" / "card.yml").read_text())


def test_card_refresh_is_weekly_and_by_hand_and_never_deploys():
    on = CARD.get("on") or CARD.get(True)
    assert "schedule" in on and "workflow_dispatch" in on
    text = (resources.files("syw_site") / "template" / "workflows" / "card.yml").read_text()
    assert "deploy" not in text.replace("never builds or deploys", "")
    assert "scripts/card.mjs" in text
