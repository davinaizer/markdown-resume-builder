from __future__ import annotations

import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from resume_builder.models import (
    EducationBlock,
    EntryBlock,
    ExperienceEntry,
    ExperienceRole,
    ExperienceType,
    ResumeContent,
    ResumeMeta,
    SectionKind,
    SectionTitles,
    SkillLine,
)
from resume_builder.sections import LoadedSection, load_resume_directory

EXPERIENCE_MARKER = re.compile(r"<!--\s*experience:\s*(.*?)\s*-->")


def clean_md_text(text: str) -> str:
    text = text.strip()
    if text.startswith("### "):
        text = text[4:]
    elif text.startswith("## "):
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


def is_h3(line: str) -> bool:
    return line.lstrip().startswith("### ")


def is_bullet(line: str) -> bool:
    return line.lstrip().startswith("- ")


def split_heading_date(text: str) -> tuple[str, str]:
    parts = [part.strip() for part in text.split("|")]
    if len(parts) < 2 or not parts[-1]:
        raise ValueError(f"Expected heading with date separated by '|': {text}")
    left = " | ".join(parts[:-1]).strip()
    return left, parts[-1]


def heading_parts(text: str, *, context: str) -> tuple[list[str], str]:
    parts = [part.strip() for part in text.split("|")]
    if len(parts) < 2 or any(not part for part in parts):
        raise ValueError(f"Malformed {context} heading: {text}")
    return parts[:-1], parts[-1]


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
    paragraph_lines = [clean_md_text(line)]
    i = idx + 1
    while i < len(lines):
        continuation = lines[i].strip()
        if (
            not continuation
            or is_rule(continuation)
            or is_h1(continuation)
            or is_h2(continuation)
            or is_h3(continuation)
            or is_bullet(continuation)
            or continuation.startswith("**Tech:**")
        ):
            break
        paragraph_lines.append(clean_md_text(continuation))
        i += 1
    return " ".join(paragraph_lines), i


@dataclass(frozen=True, slots=True)
class ContentBlock:
    descriptions: tuple[str, ...]
    bullets: tuple[str, ...]
    tech: str
    has_tech_line: bool


def parse_content_block(
    lines: list[str], start: int, boundary: Callable[[str], bool]
) -> tuple[ContentBlock, int]:
    descriptions: list[str] = []
    bullets: list[str] = []
    tech = ""
    has_tech_line = False
    i = start
    while i < len(lines):
        peek = lines[i].strip()
        if boundary(peek):
            break
        if not peek or is_rule(peek):
            i += 1
            continue
        if is_bullet(peek):
            bullets.append(clean_md_text(peek[2:]))
            i += 1
            continue
        if EXPERIENCE_MARKER.fullmatch(peek):
            raise ValueError("An experience entry may contain only one type marker")
        if peek.startswith("**Tech:**"):
            if has_tech_line:
                raise ValueError(
                    "An experience entry may contain only one **Tech:** line"
                )
            tech = clean_md_text(peek)[5:].strip()
            has_tech_line = True
            i += 1
            continue
        description, i = take_paragraph(lines, i)
        descriptions.append(description)
    return ContentBlock(tuple(descriptions), tuple(bullets), tech, has_tech_line), i


def parse_role_like_entry(lines: list[str], start: int) -> tuple[EntryBlock, int]:
    heading = clean_md_text(lines[start].strip())
    heading_left, date_right = split_heading_date(heading)
    block, i = parse_content_block(
        lines, start + 1, lambda line: is_rule(line) or is_h2(line) or is_h1(line)
    )
    if not block.descriptions:
        print(
            f"Warning: Entry {heading_left!r} has no introductory paragraph",
            file=sys.stderr,
        )
    return (
        EntryBlock(
            heading_left=heading_left,
            date_right=date_right,
            descriptions=block.descriptions,
            bullets=block.bullets,
            tech=block.tech,
        ),
        i,
    )


def parse_education_entry(lines: list[str], start: int) -> tuple[EducationBlock, int]:
    heading = clean_md_text(lines[start].strip())
    heading_left, date_right = split_heading_date(heading)
    school, i = take_paragraph(lines, start + 1)
    return EducationBlock(
        heading_left=heading_left, date_right=date_right, school=school
    ), i


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


def consume_experience_marker(
    lines: list[str], start: int, heading: str
) -> tuple[ExperienceType, int]:
    i = start
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines):
        raise ValueError(f"Experience entry {heading!r} is missing its type marker")
    match = EXPERIENCE_MARKER.fullmatch(lines[i].strip())
    if match is None:
        raise ValueError(f"Experience entry {heading!r} is missing its type marker")
    marker_value = match.group(1).strip()
    try:
        entry_type = ExperienceType(marker_value)
    except ValueError as error:
        raise ValueError(
            f"Experience entry {heading!r} has invalid type marker {marker_value!r}"
        ) from error
    return entry_type, i + 1


def parse_experience_role(lines: list[str], start: int) -> tuple[ExperienceRole, int]:
    heading = clean_md_text(lines[start].strip())
    fields, date_right = heading_parts(heading, context="experience role")
    if len(fields) not in (1, 2):
        raise ValueError(f"Malformed experience role heading: {heading}")
    block, i = parse_content_block(
        lines, start + 1, lambda line: is_h3(line) or is_h2(line)
    )
    if not block.descriptions:
        print(
            f"Warning: Entry {fields[0]!r} has no introductory paragraph",
            file=sys.stderr,
        )
    return (
        ExperienceRole(
            title=fields[0],
            organisation=fields[1] if len(fields) == 2 else None,
            date_right=date_right,
            descriptions=block.descriptions,
            bullets=block.bullets,
            tech=block.tech,
        ),
        i,
    )


def parse_experience_entry(lines: list[str], start: int) -> tuple[ExperienceEntry, int]:
    heading = clean_md_text(lines[start].strip())
    entry_type, content_start = consume_experience_marker(lines, start + 1, heading)
    parent, i = parse_content_block(
        lines, content_start, lambda line: is_h3(line) or is_h2(line)
    )
    roles: list[ExperienceRole] = []
    while i < len(lines) and is_h3(lines[i].strip()):
        if entry_type is not ExperienceType.EMPLOYMENT:
            raise ValueError(
                f"Only employment entries may contain nested roles: {heading}"
            )
        role, i = parse_experience_role(lines, i)
        roles.append(role)

    fields, date_right = heading_parts(heading, context="experience entry")
    if entry_type is ExperienceType.CAREER_BREAK:
        if len(fields) != 1:
            raise ValueError(f"Malformed career_break heading: {heading}")
        if parent.bullets or parent.has_tech_line:
            raise ValueError(
                "A career_break may not contain bullets or a **Tech:** line"
            )
        title, organisation, location = fields[0], None, None
    elif entry_type is ExperienceType.EMPLOYMENT and roles:
        if len(fields) not in (1, 2):
            raise ValueError(f"Malformed grouped employment heading: {heading}")
        title, organisation = None, fields[0]
        location = fields[1] if len(fields) == 2 else None
    else:
        if len(fields) not in (2, 3):
            raise ValueError(f"Malformed {entry_type.value} heading: {heading}")
        title, organisation = fields[0], fields[1]
        location = fields[2] if len(fields) == 3 else None

    if not parent.descriptions:
        print(
            f"Warning: Entry {heading!r} has no introductory paragraph", file=sys.stderr
        )
    return (
        ExperienceEntry(
            type=entry_type,
            title=title,
            organisation=organisation,
            location=location,
            date_right=date_right,
            descriptions=parent.descriptions,
            bullets=parent.bullets,
            tech=parent.tech,
            roles=tuple(roles),
        ),
        i,
    )


def parse_experience_lines(lines: list[str]) -> tuple[ExperienceEntry, ...]:
    experience: list[ExperienceEntry] = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line or is_rule(line):
            i += 1
            continue
        if is_h2(line):
            entry, i = parse_experience_entry(lines, i)
            experience.append(entry)
        elif is_h3(line):
            raise ValueError(
                f"Nested role has no employment parent: {clean_md_text(line)}"
            )
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
    experience: tuple[ExperienceEntry, ...]
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


def _parse_selected_project_section(
    section: LoadedSection, parsed: ParsedSections
) -> None:
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

    parsed = ParsedSections((), (), (), None, ())
    for section in source.sections:
        parser = SECTION_PARSERS.get(section.kind)
        if parser is not None:
            parser(section, parsed)

    return ResumeContent(
        meta=ResumeMeta(name, title, tagline, contact_lines),
        section_titles=section_titles,
        present_sections=present_sections,
        section_order=section_order,
        summary=parsed.summary,
        skills=parsed.skills,
        experience=parsed.experience,
        selected_project=parsed.selected_project,
        education=parsed.education,
    )
