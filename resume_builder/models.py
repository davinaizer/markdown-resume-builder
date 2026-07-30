from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SectionKind(StrEnum):
    SUMMARY = "summary"
    CORE_SKILLS = "core_skills"
    PROFESSIONAL_EXPERIENCE = "professional_experience"
    SELECTED_PROJECT = "selected_project"
    EDUCATION = "education"


@dataclass(frozen=True, slots=True)
class ResumeMeta:
    name: str
    title: str
    tagline: str
    contact_lines: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SkillLine:
    label: str
    value: str


@dataclass(frozen=True, slots=True)
class EntryBlock:
    heading_left: str
    date_right: str
    description: str
    bullets: tuple[str, ...]
    tech: str


@dataclass(frozen=True, slots=True)
class EducationBlock:
    heading_left: str
    date_right: str
    school: str


@dataclass(frozen=True, slots=True)
class SectionTitles:
    summary: str = "Summary"
    core_skills: str = "Core Skills"
    professional_experience: str = "Professional Experience"
    selected_project: str = "Selected Project"
    education: str = "Education"


@dataclass(frozen=True, slots=True)
class ResumeContent:
    meta: ResumeMeta
    summary: tuple[str, ...]
    skills: tuple[SkillLine, ...]
    experience: tuple[EntryBlock, ...]
    selected_project: EntryBlock | None
    education: tuple[EducationBlock, ...]
    section_titles: SectionTitles
    present_sections: frozenset[SectionKind]
    section_order: tuple[SectionKind, ...]
