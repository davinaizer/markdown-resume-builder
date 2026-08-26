from __future__ import annotations

import unittest
from dataclasses import replace

from resume_builder.models import ExperienceEntry, ExperienceRole, ExperienceType
from resume_builder.parser import parse_resume_source
from resume_builder.profiles import (
    OutputProfile,
    coerce_output_profile,
    flatten_experience,
    prepare_content,
    validate_experience,
)
from tests.helpers import RESUME_SOURCE


class OutputProfileTests(unittest.TestCase):
    def test_coerces_supported_profiles_and_rejects_unknown_values(self) -> None:
        self.assertIs(coerce_output_profile("ats"), OutputProfile.ATS)
        self.assertIs(
            coerce_output_profile(OutputProfile.GROUPED), OutputProfile.GROUPED
        )
        with self.assertRaisesRegex(ValueError, "choose from ats, grouped"):
            coerce_output_profile("website")

    def test_flattens_grouped_roles_without_mutating_canonical_content(self) -> None:
        content = parse_resume_source(RESUME_SOURCE)
        grouped_entry = content.experience[3]

        ats_content = prepare_content(content, OutputProfile.ATS)

        self.assertIsNot(ats_content, content)
        self.assertEqual(len(content.experience), 5)
        self.assertEqual(len(grouped_entry.roles), 3)
        self.assertEqual(len(ats_content.experience), 7)
        self.assertEqual(
            [entry.title for entry in ats_content.experience[3:6]],
            ["Frontend Tech Lead", "Senior Frontend Engineer", "Frontend Developer"],
        )
        self.assertEqual(
            [entry.organisation for entry in ats_content.experience[3:6]],
            [
                "Bally's Interactive",
                "Gamesys / Bally's Interactive",
                "Gamesys",
            ],
        )
        self.assertEqual(
            [entry.location for entry in ats_content.experience[3:6]],
            ["London, UK", "London, UK", "London, UK"],
        )
        self.assertEqual(
            [entry.date_right for entry in ats_content.experience[3:6]],
            ["11/2022 – 11/2023", "10/2020 – 11/2022", "03/2019 – 09/2020"],
        )
        self.assertTrue(
            ats_content.experience[3]
            .descriptions[0]
            .startswith("Joined Gamesys as a Frontend Developer")
        )
        self.assertTrue(ats_content.experience[3].tech.startswith("React • TypeScript"))
        self.assertTrue(all(not entry.roles for entry in ats_content.experience))

    def test_grouped_profile_returns_the_canonical_content(self) -> None:
        content = parse_resume_source(RESUME_SOURCE)
        self.assertIs(prepare_content(content, OutputProfile.GROUPED), content)

    def test_flatten_experience_uses_parent_organisation_as_role_fallback(self) -> None:
        parent = ExperienceEntry(
            type=ExperienceType.EMPLOYMENT,
            title=None,
            organisation="Acquiring Organisation",
            location="London, UK",
            date_right="2020 – 2024",
            descriptions=("Parent context.",),
            bullets=(),
            tech="Parent technology",
            roles=(
                ExperienceRole(
                    title="Engineer",
                    organisation=None,
                    date_right="2022 – 2024",
                    descriptions=("Role context.",),
                    bullets=("Delivered work.",),
                    tech="Python",
                ),
            ),
        )

        flattened = flatten_experience((parent,))

        self.assertEqual(len(flattened), 1)
        self.assertEqual(flattened[0].title, "Engineer")
        self.assertEqual(flattened[0].organisation, "Acquiring Organisation")
        self.assertEqual(flattened[0].location, "London, UK")
        self.assertEqual(
            flattened[0].descriptions, ("Parent context.", "Role context.")
        )
        self.assertEqual(flattened[0].bullets, ("Delivered work.",))
        self.assertEqual(flattened[0].tech, "Parent technology • Python")

    def test_rejects_nested_roles_on_non_employment_entries(self) -> None:
        role = ExperienceRole(
            title="Project role",
            organisation=None,
            date_right="2024",
            descriptions=(),
            bullets=(),
            tech="",
        )
        project = ExperienceEntry(
            type=ExperienceType.PROJECT,
            title="Project",
            organisation="Independent",
            location=None,
            date_right="2024",
            descriptions=(),
            bullets=(),
            tech="",
            roles=(role,),
        )

        with self.assertRaisesRegex(ValueError, "Only employment entries"):
            flatten_experience((project,))
        with self.assertRaisesRegex(ValueError, "Only employment entries"):
            validate_experience((project,))

        with self.assertRaisesRegex(ValueError, "Only employment entries"):
            flatten_experience((replace(project, type=ExperienceType.CAREER_BREAK),))
