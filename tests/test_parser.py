from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from resume_builder.parser import parse_experience_lines, parse_resume_source
from tests.helpers import RESUME_SOURCE


class ResumeParserTests(unittest.TestCase):
    def test_role_entry_without_an_introduction_warns_but_still_parses(self) -> None:
        lines = [
            "## Role | Company | 2024 – Present",
            "",
            "- Result.",
        ]

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            entries = parse_experience_lines(lines)

        self.assertEqual(entries[0].descriptions, ())
        self.assertEqual(entries[0].bullets, ("Result.",))
        self.assertIn("Warning:", stderr.getvalue())

    def test_single_file_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "resume.md"
            source.write_text("---\nname: Test\n---\n", encoding="utf-8")

            with self.assertRaisesRegex(
                NotADirectoryError, "Resume source must be an existing directory"
            ):
                parse_resume_source(source)

    def test_missing_source_directory_is_rejected(self) -> None:
        source = Path("source/does-not-exist")

        with self.assertRaisesRegex(
            NotADirectoryError, "Resume source must be an existing directory"
        ):
            parse_resume_source(source)

    def test_parses_split_resume_source(self) -> None:
        content = parse_resume_source(RESUME_SOURCE)

        self.assertEqual(content.meta.name, "Davi Naizer Santos")
        self.assertEqual(
            {section.value for section in content.present_sections},
            {"summary", "core_skills", "professional_experience", "education"},
        )
        self.assertIsNone(content.selected_project)
