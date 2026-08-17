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
    descriptions: tuple[str, ...]
    bullets: tuple[str, ...]
    tech: str


class ExperienceType(StrEnum):
    EMPLOYMENT = "employment"
    PROJECT = "project"
    CAREER_BREAK = "career_break"


@dataclass(frozen=True, slots=True)
class ExperienceRole:
    title: str
    organisation: str | None
    date_right: str
    descriptions: tuple[str, ...]
    bullets: tuple[str, ...]
    tech: str


@dataclass(frozen=True, slots=True)
class ExperienceEntry:
    type: ExperienceType
    title: str | None
    organisation: str | None
    location: str | None
    date_right: str
    descriptions: tuple[str, ...]
    bullets: tuple[str, ...]
    tech: str
    roles: tuple[ExperienceRole, ...]


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
    experience: tuple[ExperienceEntry, ...]
    selected_project: EntryBlock | None
    education: tuple[EducationBlock, ...]
    section_titles: SectionTitles
    present_sections: frozenset[SectionKind]
    section_order: tuple[SectionKind, ...]
