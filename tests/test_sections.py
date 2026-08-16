from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from resume_builder.sections import SECTION_DEFINITIONS, load_resume_directory
from tests.helpers import RESUME_SOURCE, copy_resume_source, read_section_titles


class ResumeDirectoryLoadingTests(unittest.TestCase):
    def test_loads_section_titles(self) -> None:
        source = load_resume_directory(RESUME_SOURCE)
        titles = read_section_titles(RESUME_SOURCE)

        self.assertEqual(
            [(section.kind, section.title) for section in source.sections],
            [
                ("summary", titles["summary"]),
                ("core_skills", titles["core_skills"]),
                ("professional_experience", titles["professional_experience"]),
                ("education", titles["education"]),
            ],
        )

    def test_meta_section_order_controls_loading_order(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = copy_resume_source(temp_dir)
            meta_path = source / "meta.md"
            meta_markdown = meta_path.read_text(encoding="utf-8").replace(
                "sections:\n  - summary\n  - core_skills\n  - professional_experience\n  - education\n",
                "sections:\n  - education\n  - summary\n  - core_skills\n  - professional_experience\n",
                1,
            )
            meta_path.write_text(meta_markdown, encoding="utf-8")

            loaded_source = load_resume_directory(source)

        self.assertEqual(
            [section.kind for section in loaded_source.sections],
            ["education", "summary", "core_skills", "professional_experience"],
        )

    def test_section_files_require_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir)
            (source / "sections").mkdir()
            (source / "meta.md").write_text("---\nname: Test\n---\n", encoding="utf-8")
            (source / "sections" / "summary.md").write_text(
                "No frontmatter", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                ValueError, "must start with YAML front matter"
            ):
                load_resume_directory(source)

    def test_section_files_require_a_title(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = copy_resume_source(temp_dir)
            (source / "sections" / "summary.md").write_text(
                "---\nother: value\n---\n\nSummary.\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(ValueError, "field 'title' is required"):
                load_resume_directory(source)

    def test_missing_metadata_file_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir)
            (source / "sections").mkdir()

            with self.assertRaisesRegex(
                FileNotFoundError, "Resume metadata file not found"
            ):
                load_resume_directory(source)

    def test_each_missing_required_section_warns_once(self) -> None:
        required_definitions = [
            definition for definition in SECTION_DEFINITIONS if not definition.optional
        ]

        for missing_definition in required_definitions:
            with (
                self.subTest(filename=missing_definition.filename),
                tempfile.TemporaryDirectory() as temp_dir,
            ):
                source = copy_resume_source(temp_dir)
                missing_path = source / "sections" / missing_definition.filename
                missing_path.unlink()

                stderr = io.StringIO()
                with redirect_stderr(stderr):
                    loaded_source = load_resume_directory(source)

                warning = stderr.getvalue()
                self.assertEqual(warning.count("Warning:"), 1)
                self.assertIn(str(missing_path), warning)
                self.assertNotIn(
                    missing_definition.kind,
                    [section.kind for section in loaded_source.sections],
                )

    def test_all_missing_required_sections_warn(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = copy_resume_source(temp_dir)
            required_definitions = [
                definition
                for definition in SECTION_DEFINITIONS
                if not definition.optional
            ]
            for definition in required_definitions:
                (source / "sections" / definition.filename).unlink()

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                loaded_source = load_resume_directory(source)

        warning = stderr.getvalue()
        self.assertEqual(warning.count("Warning:"), len(required_definitions))
        for definition in required_definitions:
            self.assertIn(str(source / "sections" / definition.filename), warning)
        self.assertEqual(loaded_source.sections, ())

    def test_missing_optional_section_is_silent_and_not_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = copy_resume_source(temp_dir)

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                loaded_source = load_resume_directory(source)

        self.assertEqual(stderr.getvalue(), "")
        self.assertNotIn(
            "selected_project", [section.kind for section in loaded_source.sections]
        )
