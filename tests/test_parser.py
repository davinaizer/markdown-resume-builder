from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from resume_builder.models import ResumeContent
from resume_builder.parser import parse_resume_markdown, parse_resume_source
from resume_builder.renderer import build_doc_from_source
from resume_builder.sections import load_resume_directory


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESUME_SOURCE = PROJECT_ROOT / "docs" / "resume"


class ResumeDirectoryParserTests(unittest.TestCase):
    def test_parses_split_resume_source(self) -> None:
        content = parse_resume_source(RESUME_SOURCE)

        self.assertEqual(content.meta.name, "Davi Naizer Santos")
        self.assertEqual(len(content.summary), 3)
        self.assertEqual(len(content.skills), 5)
        self.assertEqual(len(content.experience), 7)
        self.assertIsNone(content.selected_project)
        self.assertEqual(len(content.education), 2)

    def test_loads_section_titles(self) -> None:
        source = load_resume_directory(RESUME_SOURCE)

        self.assertEqual(
            [(section.kind, section.title) for section in source.sections],
            [
                ("summary", "Summary"),
                ("core_skills", "Core Skills"),
                ("professional_experience", "Professional Experience"),
                ("education", "Education"),
            ],
        )

    def test_section_files_require_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir)
            (source / "sections").mkdir()
            (source / "meta.md").write_text("---\nname: Test\n---\n", encoding="utf-8")
            (source / "sections" / "summary.md").write_text("No frontmatter", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "must start with YAML front matter"):
                load_resume_directory(source)

    def test_section_files_require_a_title(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "resume"
            shutil.copytree(RESUME_SOURCE, source)
            (source / "sections" / "summary.md").write_text("---\nother: value\n---\n\nSummary.\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "field 'title' is required"):
                load_resume_directory(source)

    def test_missing_metadata_file_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir)
            (source / "sections").mkdir()

            with self.assertRaisesRegex(FileNotFoundError, "Resume metadata file not found"):
                load_resume_directory(source)

    def test_missing_required_section_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "resume"
            shutil.copytree(RESUME_SOURCE, source)
            (source / "sections" / "summary.md").unlink()

            with self.assertRaisesRegex(FileNotFoundError, "Resume section file not found"):
                load_resume_directory(source)

    def test_selected_project_is_loaded_when_present(self) -> None:
        markdown = """---
title: Selected Work
---

## Project | 2026

Description.

- Result.

Tech: Python
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "resume"
            shutil.copytree(RESUME_SOURCE, source)
            (source / "sections" / "selected-project.md").write_text(markdown, encoding="utf-8")

            loaded_source = load_resume_directory(source)
            content = parse_resume_source(source)

        selected_section = next(section for section in loaded_source.sections if section.kind == "selected_project")
        self.assertEqual(selected_section.title, "Selected Work")
        self.assertEqual(content.section_titles.selected_project, "Selected Work")
        self.assertIsNotNone(content.selected_project)
        assert content.selected_project is not None
        self.assertEqual(content.selected_project.heading_left, "Project")
        self.assertEqual(content.selected_project.bullets, ["Result."])
        self.assertEqual(content.selected_project.tech, "Python")

    def test_editable_title_is_passed_to_model_and_renderer_without_changing_section_type(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "resume"
            shutil.copytree(RESUME_SOURCE, source)
            summary_path = source / "sections" / "summary.md"
            summary_markdown = summary_path.read_text(encoding="utf-8").replace(
                "title: Summary", "title: Professional Profile", 1
            )
            summary_path.write_text(summary_markdown, encoding="utf-8")

            content = parse_resume_source(source)
            document = build_doc_from_source(source)

        self.assertEqual(content.section_titles.summary, "Professional Profile")
        self.assertEqual(len(content.summary), 3)
        headings = [
            paragraph.text
            for paragraph in document.paragraphs
            if getattr(paragraph.style, "name", None) == "Heading 1"
        ]
        self.assertEqual(
            headings,
            ["PROFESSIONAL PROFILE", "CORE SKILLS", "PROFESSIONAL EXPERIENCE", "EDUCATION"],
        )

    def test_resume_content_legacy_constructor_shape_remains_supported(self) -> None:
        parsed = parse_resume_source(RESUME_SOURCE)

        content = ResumeContent(
            parsed.meta,
            parsed.summary,
            parsed.skills,
            parsed.experience,
            parsed.selected_project,
            parsed.education,
        )

        self.assertEqual(content.section_titles.summary, "Summary")
        self.assertEqual(content.summary, parsed.summary)

    def test_single_file_source_remains_supported(self) -> None:
        markdown = """---
name: Test Person
title: Engineer
tagline: Builds things
contact_lines:
  - test@example.com
---

# Summary

A short summary.

# Core Skills

## Languages

Python

# Professional Experience

## Engineer | 2020 – Present

Built things.

# Education

## Computer Science | 2020

Example University
"""
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "resume.md"
            source.write_text(markdown, encoding="utf-8")

            content = parse_resume_markdown(source)
            document = build_doc_from_source(source)

        self.assertEqual(content.summary, ["A short summary."])
        self.assertIsNone(content.selected_project)
        self.assertEqual(len(content.experience), 1)
        headings = [
            paragraph.text
            for paragraph in document.paragraphs
            if getattr(paragraph.style, "name", None) == "Heading 1"
        ]
        self.assertEqual(headings, ["SUMMARY", "CORE SKILLS", "PROFESSIONAL EXPERIENCE", "EDUCATION"])


if __name__ == "__main__":
    unittest.main()
