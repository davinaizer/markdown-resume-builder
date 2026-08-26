from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from docx import Document

from resume_builder.cli import main, resolve_output_path, resolve_source_path
from tests.helpers import RESUME_SOURCE


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

    def test_defaults_to_ats_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "resume.md"
            with patch.object(
                sys,
                "argv",
                ["build-resume", str(RESUME_SOURCE), "-o", str(output)],
            ):
                main()

            markdown = output.read_text(encoding="utf-8")
            experience = markdown.split("# Professional Experience", 1)[1].split(
                "# Education", 1
            )[0]

        self.assertIn(
            "## **Frontend Tech Lead | Bally's Interactive | London, UK | 11/2022 – 11/2023**",
            experience,
        )
        self.assertNotIn("### ", experience)

    def test_accepts_grouped_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "resume.md"
            with patch.object(
                sys,
                "argv",
                [
                    "build-resume",
                    str(RESUME_SOURCE),
                    "-o",
                    str(output),
                    "--profile",
                    "grouped",
                ],
            ):
                main()

            markdown = output.read_text(encoding="utf-8")
            experience = markdown.split("# Professional Experience", 1)[1].split(
                "# Education", 1
            )[0]

        self.assertIn("## **Gamesys → Bally's Interactive", experience)
        self.assertIn("### **Frontend Tech Lead", experience)

    def test_passes_ats_profile_to_docx_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "resume.docx"
            with patch.object(
                sys,
                "argv",
                [
                    "build-resume",
                    str(RESUME_SOURCE),
                    "-o",
                    str(output),
                    "--profile",
                    "ats",
                ],
            ):
                main()

            document = Document(str(output))
            headings = [
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.style.name == "Heading 2"
                and "Frontend Tech Lead" in paragraph.text
            ]

        self.assertEqual(
            headings,
            [
                "Frontend Tech Lead | Bally's Interactive | London, UK | 11/2022\N{NO-BREAK SPACE}–\N{NO-BREAK SPACE}11/2023"
            ],
        )

    def test_rejects_unknown_profile(self) -> None:
        with (
            patch.object(
                sys,
                "argv",
                ["build-resume", str(RESUME_SOURCE), "--profile", "website"],
            ),
            self.assertRaises(SystemExit),
        ):
            main()
