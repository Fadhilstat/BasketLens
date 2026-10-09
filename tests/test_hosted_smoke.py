"""Deterministic release smoke guardrail tests."""
import importlib.util
from pathlib import Path
import pytest

SOURCE = Path(__file__).resolve().parents[1] / "scripts" / "hosted_smoke.py"
spec = importlib.util.spec_from_file_location("hosted_smoke", SOURCE)
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)


@pytest.mark.parametrize("url", [
    "https://basketlens-retail.streamlit.app/",
    "https://BASKETLENS-RETAIL.streamlit.app",
])
def test_valid_url(url):
    assert smoke.validate_app_url(url) == "https://basketlens-retail.streamlit.app/"


@pytest.mark.parametrize("url", [
    "http://basketlens-retail.streamlit.app/",
    "https://other.example.com/",
    "https://basketlens-retail.streamlit.app/-/login",
    "https://basketlens-retail.streamlit.app/?payload=secret",
    "https://user:pass@basketlens-retail.streamlit.app/",
    "https://basketlens-retail.streamlit.app:443/",
    "https://basketlens-retail.streamlit.app:bad/",
])
def test_invalid_url(url):
    with pytest.raises(ValueError):
        smoke.validate_app_url(url)


def test_redirect_is_redacted():
    url = "https://basketlens-retail.streamlit.app/-/login?payload=SECRET"
    assert smoke.login_redirect(url)
    assert smoke.sanitized_url(url) == "https://basketlens-retail.streamlit.app/-/login"
    assert not smoke.login_redirect("https://basketlens-retail.streamlit.app/")


def test_layout_fails_closed():
    with pytest.raises(smoke.ReleaseNotReady, match="overlaps"):
        smoke.assert_layout({"x": 10, "y": 0, "height": 100}, {"x": 10, "y": 70})
    with pytest.raises(smoke.ReleaseNotReady, match="misaligned"):
        smoke.assert_layout({"x": 10, "y": 0, "height": 30}, {"x": 100, "y": 40})
    with pytest.raises(smoke.ReleaseNotReady, match="Missing"):
        smoke.assert_layout(None, {"x": 0, "y": 0})
    smoke.assert_layout({"x": 10, "y": 0, "height": 30}, {"x": 11, "y": 40})


def test_runner_never_loads_credentials():
    source = SOURCE.read_text(encoding="utf-8")
    assert "browser.new_page(" in source
    assert "storage_state=" not in source
    assert "page.goto(url" in source
