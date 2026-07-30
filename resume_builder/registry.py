from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SectionDefinition:
    kind: str
    canonical_title: str
    filename: str
    optional: bool = False


SECTION_DEFINITIONS = (
    SectionDefinition("summary", "Summary", "summary.md"),
    SectionDefinition("core_skills", "Core Skills", "core-skills.md"),
    SectionDefinition(
        "professional_experience",
        "Professional Experience",
        "professional-experience.md",
    ),
    SectionDefinition(
        "selected_project", "Selected Project", "selected-project.md", optional=True
    ),
    SectionDefinition("education", "Education", "education.md"),
)
