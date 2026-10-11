"""Small offline tests for source identity checked by public guest smoke."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("basketlens_site_hosted", Path(__file__).with_name("hosted_smoke.py"))
smoke = importlib.util.module_from_spec(spec)
spec.loader.exec_module(smoke)

COMMIT = "a" * 40


def valid_payload():
    return {
        "schema": "basketlens.release-provenance.v1",
        "source": "vercel-git",
        "gitSha": COMMIT,
        "exhibitSha256": smoke.EXPECTED_EXHIBIT_SHA256,
        "ruleCount": 1500,
    }


class FakeResponse:
    status = 200

    def __init__(self, payload):
        self.raw = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        pass

    def read(self, _limit):
        return self.raw


class ReleaseProvenanceTests(unittest.TestCase):
    def test_accepts_exact_git_commit_and_data_fingerprint(self):
        self.assertEqual(smoke.validate_release_provenance(valid_payload(), COMMIT)["status"], "PASS")

    def test_rejects_wrong_git_commit(self):
        with self.assertRaisesRegex(AssertionError, "does not match"):
            smoke.validate_release_provenance(valid_payload(), "b" * 40)

    def test_rejects_bad_commit_shape(self):
        with self.assertRaises(ValueError):
            smoke.validate_release_provenance(valid_payload(), "short")

    def test_rejects_unverified_source(self):
        value = valid_payload()
        value["source"] = "unverified-local"
        with self.assertRaisesRegex(AssertionError, "does not match"):
            smoke.validate_release_provenance(value, COMMIT)

    def test_rejects_modified_data_fingerprint(self):
        value = valid_payload()
        value["exhibitSha256"] = "0" * 64
        with self.assertRaisesRegex(AssertionError, "fingerprint"):
            smoke.validate_release_provenance(value, COMMIT)

    def test_public_manifest_fetch_matches_expected_commit(self):
        with patch.object(smoke, "urlopen", return_value=FakeResponse(valid_payload())) as get:
            result = smoke.verify_deployed_provenance(smoke.DEFAULT_URL, COMMIT, timeout_seconds=0)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(get.call_args[0][0].full_url.endswith("/release.json"))

    def test_public_manifest_mismatch_fails_closed(self):
        value = valid_payload()
        value["gitSha"] = "b" * 40
        with patch.object(smoke, "urlopen", return_value=FakeResponse(value)):
            with self.assertRaisesRegex(AssertionError, "not verified"):
                smoke.verify_deployed_provenance(smoke.DEFAULT_URL, COMMIT, timeout_seconds=0)


if __name__ == "__main__":
    unittest.main()
