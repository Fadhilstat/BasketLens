"""Publication narrative and relative link regression checks."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
README = (ROOT / "README.md").read_text(encoding="utf-8")
READY = (ROOT / "docs/publication-readiness.md").read_text(encoding="utf-8")
STORY = (ROOT / "docs/social/three-slide-story.md").read_text(encoding="utf-8")
POST = (ROOT / "docs/social/linkedin-post.md").read_text(encoding="utf-8")
RELEASE = (ROOT / "docs/release-notes-v1.0.0.md").read_text(encoding="utf-8")


def test_publication_local_links_resolve():
    paths = [ROOT / "README.md", ROOT / "docs/publication-readiness.md",
             ROOT / "docs/social/three-slide-story.md",
             ROOT / "docs/social/linkedin-post.md",
             ROOT / "docs/release-notes-v1.0.0.md"]
    for file in paths:
        for link in re.findall(r"\]\(([^)]+)\)", file.read_text(encoding="utf-8")):
            if link.startswith(("https://", "http://", "mailto:", "#")):
                continue
            name = link.split("#", 1)[0].split("?", 1)[0]
            if name:
                assert (file.parent / name).resolve().is_file(), (str(file), name)


def test_exact_three_slides_with_correct_research_boundaries():
    assert STORY.count("\n## Slide ") == 3
    for fact in ("1,067,371", "40,280", "1,500", "1,166",
                 "279 of 416", "63.1%", "67.1%", "6.24x", "6.77x"):
        assert fact in STORY
    assert "No causal revenue" in STORY


def test_public_guest_gate_and_release_not_overclaimed():
    assert "incognito" in READY and "login prompt" in READY
    assert "GitHub About" in READY
    assert "Status: DRAFT" in RELEASE
    assert "does not publish a tag" in RELEASE
    assert "That does not prove" in POST
    assert "(docs/publication-readiness.md)" in README


def test_publication_copy_has_no_em_dash():
    for content in (READY, STORY, POST, RELEASE):
        assert "\u2014" not in content
