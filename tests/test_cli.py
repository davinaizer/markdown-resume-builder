from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from resume_builder.cli import resolve_output_path, resolve_source_path


class CliPathResolutionTests(unittest.TestCase):
    def test_resolves_named_sources_and_relative_outputs_under_their_roots(
        self,
    ) -> None:
        self.assertEqual(
            resolve_source_path("canon-resume"), Path("source/canon-resume")
        )
        self.assertEqual(
            resolve_output_path("resume-test.docx"), Path("output/resume-test.docx")
        )

    def test_preserves_existing_source_and_absolute_output_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "resume"
            source.mkdir()
            output = Path(temp_dir) / "resume.docx"

            self.assertEqual(resolve_source_path(source), source)
            self.assertEqual(resolve_output_path(output), output)
