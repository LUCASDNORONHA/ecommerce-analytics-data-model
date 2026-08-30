from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from unittest.mock import patch

from scripts.maintenance import clean


class CleanupTests(TestCase):
    def test_collects_only_known_workspace_artifacts(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            workspace_cache = root / "database" / "__pycache__"
            environment_cache = root / ".venv" / "lib" / "__pycache__"
            latex_file = root / "docs" / "report.aux"
            output_file = root / "outputs" / "report.json"
            for path in (workspace_cache, environment_cache):
                path.mkdir(parents=True)
            for path in (latex_file, output_file):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.touch()

            with patch.object(clean, "ROOT", root):
                targets = clean.collect_targets()

            self.assertIn(workspace_cache, targets)
            self.assertIn(latex_file, targets)
            self.assertIn(root / "outputs", targets)
            self.assertNotIn(environment_cache, targets)

    def test_refuses_target_containing_tracked_file(self) -> None:
        root = Path("/repository")
        with (
            patch.object(clean, "ROOT", root),
            patch.object(clean, "tracked_paths", return_value={"outputs/report.json"}),
        ):
            with self.assertRaisesRegex(RuntimeError, "arquivo versionado"):
                clean.ensure_untracked([root / "outputs"])
