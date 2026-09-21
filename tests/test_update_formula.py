import copy
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("update_formula", ROOT / "scripts/update_formula.py")
updater = importlib.util.module_from_spec(spec)
spec.loader.exec_module(updater)


class UpdateTests(unittest.TestCase):
    def setUp(self):
        self.source = (ROOT / "Formula/bend.rb").read_text()
        current = updater.re.search(r'/download/v(\d+\.\d+\.\d+)/', self.source)[1]
        major, minor, patch_version = map(int, current.split("."))
        self.version = f"{major}.{minor}.{patch_version + 1}"
        self.release = {
            "tag_name": "v" + self.version,
            "draft": False,
            "prerelease": False,
            "assets": [
                {
                    "name": f"bend-{self.version}-darwin-{arch}.tar.gz",
                    "browser_download_url": f"{updater.RELEASES}/v{self.version}/bend-{self.version}-darwin-{arch}.tar.gz",
                    "digest": "sha256:" + digit * 64,
                }
                for arch, digit in (("arm64", "a"), ("x64", "b"))
            ],
        }
        self.digest = Mock(side_effect=["a" * 64, "b" * 64])

    def test_updates_both_platforms_and_preserves_install_logic(self):
        result = updater.update(self.source, self.release, self.digest)
        self.assertIn(f"/download/v{self.version}/", result)
        for asset in self.release["assets"]:
            self.assertIn(asset["browser_download_url"], result)
            self.assertIn(asset["digest"][7:], result)
        self.assertEqual(self.source.split("  def install", 1)[1], result.split("  def install", 1)[1])
        self.assertEqual(self.digest.call_count, 2)

    def test_current_release_is_noop_without_download(self):
        updated = updater.update(self.source, self.release, self.digest)
        digest = Mock(side_effect=AssertionError("Unexpected download"))
        self.assertEqual(updater.update(updated, self.release, digest), updated)

    def test_verify_current_checks_both_archives(self):
        updated = updater.update(self.source, self.release, self.digest)
        digest = Mock(side_effect=["a" * 64, "b" * 64])
        self.assertEqual(updater.update(updated, self.release, digest, True), updated)
        self.assertEqual(digest.call_count, 2)

    def test_rejects_replaced_assets_for_same_version(self):
        updated = updater.update(self.source, self.release, self.digest)
        self.release["assets"][0]["digest"] = "sha256:" + "c" * 64
        with self.assertRaisesRegex(ValueError, "Published assets changed"):
            updater.update(updated, self.release, Mock(side_effect=["c" * 64, "b" * 64]), True)

    def test_rejects_checksum_mismatch(self):
        with self.assertRaisesRegex(ValueError, "Checksum mismatch"):
            updater.update(self.source, self.release, lambda _: "0" * 64)

    def test_rejects_missing_or_duplicate_assets(self):
        for assets in (self.release["assets"][:1], self.release["assets"] * 2):
            with self.subTest(assets=assets), self.assertRaisesRegex(ValueError, "exactly one asset"):
                updater.update(self.source, dict(self.release, assets=assets), lambda _: "a" * 64)

    def test_rejects_bad_release_metadata(self):
        changes = [{"draft": True}, {"prerelease": True}, {"tag_name": "v3.0.0"},
                   {"tag_name": "v2.1.0-rc1"}, {"tag_name": "v2.0.0"}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                updater.update(self.source, dict(self.release, **change), self.digest)
        self.digest.assert_not_called()

    def test_rejects_unexpected_urls_and_missing_digests(self):
        for field, value in (("browser_download_url", "https://example.com/file"), ("digest", None)):
            release = copy.deepcopy(self.release)
            release["assets"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                updater.update(self.source, release, self.digest)
        self.digest.assert_not_called()

    def test_fails_if_formula_layout_changes(self):
        with self.assertRaisesRegex(ValueError, "formula URL/checksum pair"):
            updater.update(self.source.replace("      sha256", "    sha256"), self.release, self.digest)

    def test_main_does_not_write_after_validation_failure(self):
        formula = Mock()
        formula.read_text.return_value = self.source
        with patch.object(updater, "FORMULA", formula), \
             patch.object(updater, "latest_release", return_value=self.release), \
             patch.object(updater, "update", side_effect=ValueError("Checksum mismatch")), \
             patch("sys.argv", ["update_formula.py"]):
            with self.assertRaises(ValueError):
                updater.main()
        formula.write_text.assert_not_called()


if __name__ == "__main__":
    unittest.main()
