from __future__ import annotations

from dataclasses import dataclass

from resume_builder.models import SectionKind


@dataclass(frozen=True, slots=True)
class SectionDefinition:
    kind: SectionKind
    canonical_title: str
    filename: str
    optional: bool = False


SECTION_DEFINITIONS = (
    SectionDefinition(SectionKind.SUMMARY, "Summary", "summary.md"),
    SectionDefinition(SectionKind.CORE_SKILLS, "Core Skills", "core-skills.md"),
    SectionDefinition(
        SectionKind.PROFESSIONAL_EXPERIENCE,
        "Professional Experience",
        "professional-experience.md",
    ),
    SectionDefinition(
        SectionKind.SELECTED_PROJECT,
        "Selected Project",
        "selected-project.md",
        optional=True,
    ),
    SectionDefinition(SectionKind.EDUCATION, "Education", "education.md"),
)
