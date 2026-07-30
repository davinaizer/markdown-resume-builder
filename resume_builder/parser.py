from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from resume_builder.models import (
    EducationBlock,
    EntryBlock,
    ResumeContent,
    ResumeMeta,
    SectionKind,
    SectionTitles,
    SkillLine,
)
from resume_builder.sections import LoadedSection, load_resume_directory


def clean_md_text(text: str) -> str:
    text = text.strip()
    if text.startswith("## "):
        text = text[3:]
    elif text.startswith("# "):
        text = text[2:]
    text = text.replace("**", "")
    return text.strip()


def is_rule(line: str) -> bool:
    return line.strip() == "---"


def is_h1(line: str) -> bool:
    return line.lstrip().startswith("# ") and not line.lstrip().startswith("## ")


def is_h2(line: str) -> bool:
    return line.lstrip().startswith("## ")


def is_bullet(line: str) -> bool:
    return line.lstrip().startswith("- ")


def split_heading_date(text: str) -> tuple[str, str]:
    parts = [part.strip() for part in text.split("|")]
    if len(parts) < 2:
        raise ValueError(f"Expected heading with date separated by '|': {text}")
    left = " | ".join(parts[:-1]).strip()
    right = parts[-1].strip()
    return left, right


def next_content_line(lines: list[str], start: int) -> tuple[str | None, int]:
    i = start
    while i < len(lines):
        line = lines[i].strip()
        if line and not is_rule(line):
            return line, i
        i += 1
    return None, len(lines)


def take_paragraph(lines: list[str], start: int) -> tuple[str, int]:
    line, idx = next_content_line(lines, start)
    if line is None:
        raise ValueError("Expected paragraph content")
    return clean_md_text(line), idx + 1


def parse_role_like_entry(lines: list[str], start: int) -> tuple[EntryBlock, int]:
    heading = clean_md_text(lines[start].strip())
    heading_left, date_right = split_heading_date(heading)
    description, i = take_paragraph(lines, start + 1)
    bullets: list[str] = []
    tech = ""
    while i < len(lines):
        peek = lines[i].strip()
        if not peek:
            i += 1
            continue
        if is_rule(peek) or is_h2(peek) or is_h1(peek):
            break
        if is_bullet(peek):
            bullets.append(clean_md_text(peek[2:]))
            i += 1
            continue
        if peek.startswith("Tech:"):
            tech = clean_md_text(peek)[5:].strip()
            i += 1
            break
        i += 1
    return (
        EntryBlock(
            heading_left=heading_left,
            date_right=date_right,
            description=description,
            bullets=tuple(bullets),
            tech=tech,
        ),
        i,
    )


def parse_education_entry(lines: list[str], start: int) -> tuple[EducationBlock, int]:
    heading = clean_md_text(lines[start].strip())
    heading_left, date_right = split_heading_date(heading)
    school, i = take_paragraph(lines, start + 1)
    return (
        EducationBlock(heading_left=heading_left, date_right=date_right, school=school),
        i,
    )


def parse_summary_lines(lines: list[str]) -> tuple[str, ...]:
    summary: list[str] = []
    for line in lines:
        line = line.strip()
        if line and not is_rule(line):
            summary.append(clean_md_text(line))
    return tuple(summary)


def parse_skill_lines(lines: list[str]) -> tuple[SkillLine, ...]:
    skills: list[SkillLine] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or is_rule(line):
            i += 1
            continue
        if is_h2(line):
            label = clean_md_text(line)
            value, i = take_paragraph(lines, i + 1)
            skills.append(SkillLine(label=label, value=value))
        else:
            i += 1
    return tuple(skills)


def parse_experience_lines(lines: list[str]) -> tuple[EntryBlock, ...]:
    experience: list[EntryBlock] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or is_rule(line):
            i += 1
            continue
        if is_h2(line):
            entry, i = parse_role_like_entry(lines, i)
            experience.append(entry)
        else:
            i += 1
    return tuple(experience)


def parse_selected_project_lines(lines: list[str]) -> EntryBlock | None:
    selected_project: EntryBlock | None = None
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or is_rule(line):
            i += 1
            continue
        if is_h2(line):
            selected_project, i = parse_role_like_entry(lines, i)
        else:
            i += 1
    return selected_project


def parse_education_lines(lines: list[str]) -> tuple[EducationBlock, ...]:
    education: list[EducationBlock] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or is_rule(line):
            i += 1
            continue
        if is_h2(line):
            item, i = parse_education_entry(lines, i)
            education.append(item)
        else:
            i += 1
    return tuple(education)


@dataclass(slots=True)
class ParsedSections:
    summary: tuple[str, ...]
    skills: tuple[SkillLine, ...]
    experience: tuple[EntryBlock, ...]
    selected_project: EntryBlock | None
    education: tuple[EducationBlock, ...]


SECTION_PARSERS: dict[SectionKind, Callable[[LoadedSection, ParsedSections], None]] = {}


def _parse_summary_section(section: LoadedSection, parsed: ParsedSections) -> None:
    parsed.summary = parse_summary_lines(section.content.splitlines())


def _parse_core_skills_section(section: LoadedSection, parsed: ParsedSections) -> None:
    parsed.skills = parse_skill_lines(section.content.splitlines())


def _parse_professional_experience_section(
    section: LoadedSection, parsed: ParsedSections
) -> None:
    parsed.experience = parse_experience_lines(section.content.splitlines())


def _parse_selected_project_section(section: LoadedSection, parsed: ParsedSections) -> None:
    parsed.selected_project = parse_selected_project_lines(section.content.splitlines())


def _parse_education_section(section: LoadedSection, parsed: ParsedSections) -> None:
    parsed.education = parse_education_lines(section.content.splitlines())


SECTION_PARSERS.update(
    {
        SectionKind.SUMMARY: _parse_summary_section,
        SectionKind.CORE_SKILLS: _parse_core_skills_section,
        SectionKind.PROFESSIONAL_EXPERIENCE: _parse_professional_experience_section,
        SectionKind.SELECTED_PROJECT: _parse_selected_project_section,
        SectionKind.EDUCATION: _parse_education_section,
    }
)


def _require_string(metadata: dict, key: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Front matter field '{key}' is required and must be a non-empty string"
        )
    return clean_md_text(value)


def _require_string_list(metadata: dict, key: str) -> tuple[str, ...]:
    value = metadata.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(
            f"Front matter field '{key}' is required and must be a non-empty list of strings"
        )
    cleaned: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                f"Front matter field '{key}' must contain only non-empty strings"
            )
        cleaned.append(item.strip())
    return tuple(cleaned)


def parse_resume_source(path: Path) -> ResumeContent:
    if not path.is_dir():
        raise NotADirectoryError(f"Resume source must be an existing directory: {path}")

    source = load_resume_directory(path)
    metadata = source.metadata
    titles_by_kind = {section.kind: section.title for section in source.sections}
    section_titles = SectionTitles(**titles_by_kind)
    present_sections = frozenset(section.kind for section in source.sections)
    section_order = tuple(section.kind for section in source.sections)
    name = _require_string(metadata, "name")
    title = _require_string(metadata, "title")
    tagline = _require_string(metadata, "tagline")
    contact_lines = _require_string_list(metadata, "contact_lines")

    parsed = ParsedSections(
        summary=(),
        skills=(),
        experience=(),
        selected_project=None,
        education=(),
    )
    for section in source.sections:
        parser = SECTION_PARSERS.get(section.kind)
        if parser is not None:
            parser(section, parsed)

    return ResumeContent(
        meta=ResumeMeta(
            name=name, title=title, tagline=tagline, contact_lines=contact_lines
        ),
        section_titles=section_titles,
        present_sections=present_sections,
        section_order=section_order,
        summary=parsed.summary,
        skills=parsed.skills,
        experience=parsed.experience,
        selected_project=parsed.selected_project,
        education=parsed.education,
    )
