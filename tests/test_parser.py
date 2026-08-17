from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from resume_builder.models import ExperienceType
from resume_builder.parser import parse_experience_lines, parse_resume_source
from tests.helpers import RESUME_SOURCE


class ResumeParserTests(unittest.TestCase):
    def test_parses_typed_experience_shapes_and_nested_roles(self) -> None:
        lines = [
            "## Project | Independent | 2026 – Present",
            "<!-- experience: project -->",
            "",
            "First project paragraph.",
            "",
            "Second project paragraph.",
            "",
            "- Shipped it.",
            "",
            "**Tech:** Python",
            "",
            "## Break | 2025",
            "<!-- experience: career_break -->",
            "",
            "Planned time away.",
            "",
            "## Company | London | 2020 – 2024",
            "<!-- experience: employment -->",
            "",
            "Employment context.",
            "",
            "- Parent contribution.",
            "",
            "**Tech:** Parent technology",
            "",
            "### Lead | Brand | 2023 – 2024",
            "",
            "Lead summary.",
            "",
            "- Led work.",
            "",
            "**Tech:** TypeScript",
            "",
            "### Engineer | 2020 – 2023",
            "",
            "Engineer summary.",
            "",
            "**Tech:** React",
            "",
            "### Developer | 2020",
            "",
            "Developer summary.",
            "",
            "- Built it.",
            "",
            "**Tech:** JavaScript",
        ]

        entries = parse_experience_lines(lines)

        self.assertEqual(len(entries), 3)
        project, career_break, employment = entries
        self.assertEqual(project.type, ExperienceType.PROJECT)
        self.assertEqual(project.location, None)
        self.assertEqual(
            project.descriptions,
            ("First project paragraph.", "Second project paragraph."),
        )
        self.assertEqual(career_break.type, ExperienceType.CAREER_BREAK)
        self.assertEqual(career_break.title, "Break")
        self.assertEqual(career_break.organisation, None)
        self.assertEqual(employment.type, ExperienceType.EMPLOYMENT)
        self.assertIsNone(employment.title)
        self.assertEqual(employment.organisation, "Company")
        self.assertEqual(employment.location, "London")
        self.assertEqual(employment.descriptions, ("Employment context.",))
        self.assertEqual(employment.bullets, ("Parent contribution.",))
        self.assertEqual(employment.tech, "Parent technology")
        self.assertEqual(
            [role.title for role in employment.roles], ["Lead", "Engineer", "Developer"]
        )
        self.assertEqual(employment.roles[0].organisation, "Brand")
        self.assertIsNone(employment.roles[1].organisation)
        self.assertEqual(employment.roles[0].tech, "TypeScript")
        self.assertEqual(employment.roles[1].tech, "React")
        self.assertEqual(employment.roles[2].bullets, ("Built it.",))
        self.assertEqual(employment.roles[2].tech, "JavaScript")

    def test_flat_employment_with_location_parses(self) -> None:
        entries = parse_experience_lines(
            [
                "## Engineer | Company | London, UK | 2024",
                "<!-- experience: employment -->",
                "",
                "Summary.",
            ]
        )
        self.assertEqual(entries[0].title, "Engineer")
        self.assertEqual(entries[0].organisation, "Company")
        self.assertEqual(entries[0].location, "London, UK")
        self.assertEqual(entries[0].roles, ())

    def test_missing_invalid_or_duplicate_type_marker_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "missing its type marker"):
            parse_experience_lines(["## Engineer | Company | 2024", "Summary."])
        with self.assertRaisesRegex(ValueError, "invalid type marker"):
            parse_experience_lines(
                ["## Engineer | Company | 2024", "<!-- experience: CONTRACT -->"]
            )
        with self.assertRaisesRegex(ValueError, "only one type marker"):
            parse_experience_lines(
                [
                    "## Engineer | Company | 2024",
                    "<!-- experience: employment -->",
                    "<!-- experience: employment -->",
                ]
            )

    def test_invalid_experience_combinations_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "Malformed project heading"):
            parse_experience_lines(
                ["## Project | 2024", "<!-- experience: project -->", "Summary."]
            )
        with self.assertRaisesRegex(ValueError, "Only employment entries"):
            parse_experience_lines(
                [
                    "## Project | Company | 2024",
                    "<!-- experience: project -->",
                    "### Role | 2024",
                ]
            )
        for invalid_body in (["- Bullet."], ["**Tech:** Python"]):
            with (
                self.subTest(invalid_body=invalid_body),
                self.assertRaisesRegex(ValueError, "career_break may not"),
            ):
                parse_experience_lines(
                    [
                        "## Break | 2024",
                        "<!-- experience: career_break -->",
                        *invalid_body,
                    ]
                )
        with self.assertRaisesRegex(ValueError, "Only employment entries"):
            parse_experience_lines(
                [
                    "## Break | 2024",
                    "<!-- experience: career_break -->",
                    "### Role | 2024",
                ]
            )

    def test_entry_without_an_introduction_warns_but_still_parses(self) -> None:
        stderr = io.StringIO()
        with redirect_stderr(stderr):
            entries = parse_experience_lines(
                [
                    "## Role | Company | 2024 – Present",
                    "<!-- experience: employment -->",
                    "",
                    "- Result.",
                ]
            )
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
        with self.assertRaisesRegex(
            NotADirectoryError, "Resume source must be an existing directory"
        ):
            parse_resume_source(Path("source/does-not-exist"))

    def test_parses_split_resume_source(self) -> None:
        content = parse_resume_source(RESUME_SOURCE)
        self.assertEqual(content.meta.name, "Davi Naizer Santos")
        self.assertEqual(
            {section.value for section in content.present_sections},
            {"summary", "core_skills", "professional_experience", "education"},
        )
        self.assertEqual(len(content.experience[3].roles), 3)
        self.assertIsNone(content.selected_project)
