from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "tools" / "check_readme_sync.py"


class ReadmeSyncTest(unittest.TestCase):
    def run_checker(self, changed_input: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(CHECKER)],
            cwd=ROOT,
            input=changed_input,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_unrelated_file_only_passes(self) -> None:
        result = self.run_checker("obsidian_wiki/cli.py\n")

        self.assertEqual(result.returncode, 0)

    def test_both_readmes_changed_passes(self) -> None:
        result = self.run_checker("README.md\nREADME_TW.md\nAGENTS.md\n")

        self.assertEqual(result.returncode, 0)

    def test_english_readme_only_fails_with_specific_message(self) -> None:
        result = self.run_checker("README.md\n")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr,
            "README sync check failed: README.md changed without README_TW.md. "
            "Update both files in the same change set.\n",
        )

    def test_traditional_chinese_readme_only_fails_with_specific_message(self) -> None:
        result = self.run_checker("README_TW.md\n")

        self.assertEqual(result.returncode, 1)
        self.assertEqual(
            result.stderr,
            "README sync check failed: README_TW.md changed without README.md. "
            "Update both files in the same change set.\n",
        )


if __name__ == "__main__":
    unittest.main()
