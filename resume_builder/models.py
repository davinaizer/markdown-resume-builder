from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ResumeMeta:
    name: str
    title: str
    tagline: str
    contact_lines: list[str]


@dataclass
class SkillLine:
    label: str
    value: str


@dataclass
class EntryBlock:
    heading_left: str
    date_right: str
    description: str
    bullets: list[str]
    tech: str


@dataclass
class EducationBlock:
    heading_left: str
    date_right: str
    school: str


@dataclass(frozen=True)
class SectionTitles:
    summary: str = "Summary"
    core_skills: str = "Core Skills"
    professional_experience: str = "Professional Experience"
    selected_project: str = "Selected Project"
    education: str = "Education"


@dataclass
class ResumeContent:
    meta: ResumeMeta
    summary: list[str]
    skills: list[SkillLine]
    experience: list[EntryBlock]
    selected_project: EntryBlock | None
    education: list[EducationBlock]
    section_titles: SectionTitles = SectionTitles()
