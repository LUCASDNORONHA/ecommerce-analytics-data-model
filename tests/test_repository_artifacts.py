import json
import re
import unittest
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
IGNORED_PARTS = {".git", ".venv", "tmp"}
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def repository_files(pattern):
    return (
        path
        for path in ROOT.rglob(pattern)
        if not IGNORED_PARTS.intersection(path.relative_to(ROOT).parts)
    )


class RepositoryArtifactTests(unittest.TestCase):
    def test_local_markdown_links_resolve(self):
        broken = []
        for document in repository_files("*.md"):
            text = document.read_text(encoding="utf-8")
            for raw_target in MARKDOWN_LINK.findall(text):
                target = raw_target.strip().strip("<>").split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (document.parent / unquote(target)).resolve()
                if not resolved.exists():
                    broken.append(f"{document.relative_to(ROOT)} -> {raw_target}")
        self.assertEqual(broken, [])

    def test_json_and_notebook_files_are_valid_json(self):
        invalid = []
        for pattern in ("*.json", "*.ipynb"):
            for path in repository_files(pattern):
                try:
                    json.loads(path.read_text(encoding="utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as error:
                    invalid.append(f"{path.relative_to(ROOT)}: {error}")
        self.assertEqual(invalid, [])

    def test_versioned_pdfs_have_valid_file_markers(self):
        invalid = []
        for path in repository_files("*.pdf"):
            content = path.read_bytes()
            if not content.startswith(b"%PDF-") or b"%%EOF" not in content[-1024:]:
                invalid.append(str(path.relative_to(ROOT)))
        self.assertEqual(invalid, [])


if __name__ == "__main__":
    unittest.main()
