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


@dataclass
class ResumeContent:
    meta: ResumeMeta
    summary: list[str]
    skills: list[SkillLine]
    experience: list[EntryBlock]
    selected_project: EntryBlock | None
    education: list[EducationBlock]
