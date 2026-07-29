from __future__ import annotations

from pathlib import Path

import frontmatter
from frontmatter.default_handlers import YAMLHandler

from resume_builder.models import (
    EducationBlock,
    EntryBlock,
    ResumeContent,
    ResumeMeta,
    SectionTitles,
    SkillLine,
)
from resume_builder.sections import load_resume_directory


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


def _require_string(metadata: dict, key: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Front matter field '{key}' is required and must be a non-empty string")
    return clean_md_text(value)


def _require_string_list(metadata: dict, key: str) -> list[str]:
    value = metadata.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Front matter field '{key}' is required and must be a non-empty list of strings")
    cleaned: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"Front matter field '{key}' must contain only non-empty strings")
        cleaned.append(item.strip())
    return cleaned


def parse_resume_source(path: Path) -> ResumeContent:
    if path.is_dir():
        source = load_resume_directory(path)
        metadata = source.metadata
        content = source.content
        titles_by_kind = {section.kind: section.title for section in source.sections}
        section_titles = SectionTitles(**titles_by_kind)
        present_sections = frozenset(titles_by_kind)
    else:
        text = path.read_text(encoding="utf-8")
        handler = YAMLHandler()
        if not handler.detect(text):
            raise ValueError("Resume markdown must start with YAML front matter")

        post = frontmatter.loads(text, handler=handler)
        metadata = post.metadata
        content = post.content
        section_titles = SectionTitles()
        present_sections = frozenset(
            {"summary", "core_skills", "professional_experience", "selected_project", "education"}
        )
    name = _require_string(metadata, "name")
    title = _require_string(metadata, "title")
    tagline = _require_string(metadata, "tagline")
    contact_lines = _require_string_list(metadata, "contact_lines")

    lines = content.splitlines()
    i = 0

    summary: list[str] = []
    skills: list[SkillLine] = []
    experience: list[EntryBlock] = []
    selected_project: EntryBlock | None = None
    education: list[EducationBlock] = []

    def collect_paragraph() -> str:
        nonlocal i
        line, idx = next_content_line(lines, i)
        if line is None:
            raise ValueError("Expected paragraph content")
        i = idx + 1
        return clean_md_text(line)

    while i < len(lines):
        line = lines[i].strip()
        if not line or is_rule(line):
            i += 1
            continue
        if not is_h1(line):
            i += 1
            continue

        section = clean_md_text(line)
        i += 1

        if section == "Summary":
            while i < len(lines) and not is_h1(lines[i]):
                line = lines[i].strip()
                if line and not is_rule(line):
                    summary.append(clean_md_text(line))
                i += 1
        elif section == "Core Skills":
            while i < len(lines) and not is_h1(lines[i]):
                line = lines[i].strip()
                if is_h2(line):
                    label = clean_md_text(line)
                    i += 1
                    value = collect_paragraph()
                    skills.append(SkillLine(label=label, value=value))
                else:
                    i += 1
        elif section == "Professional Experience":
            while i < len(lines) and not is_h1(lines[i]):
                line = lines[i].strip()
                if is_h2(line):
                    heading = clean_md_text(line)
                    heading_left, date_right = split_heading_date(heading)
                    i += 1
                    description = collect_paragraph()
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
                    experience.append(
                        EntryBlock(
                            heading_left=heading_left,
                            date_right=date_right,
                            description=description,
                            bullets=bullets,
                            tech=tech,
                        )
                    )
                else:
                    i += 1
        elif section == "Selected Project":
            while i < len(lines) and not is_h1(lines[i]):
                line = lines[i].strip()
                if is_h2(line):
                    heading = clean_md_text(line)
                    heading_left, date_right = split_heading_date(heading)
                    i += 1
                    description = collect_paragraph()
                    project_bullets: list[str] = []
                    tech = ""
                    while i < len(lines):
                        peek = lines[i].strip()
                        if not peek:
                            i += 1
                            continue
                        if is_rule(peek) or is_h2(peek) or is_h1(peek):
                            break
                        if is_bullet(peek):
                            project_bullets.append(clean_md_text(peek[2:]))
                            i += 1
                            continue
                        if peek.startswith("Tech:"):
                            tech = clean_md_text(peek)[5:].strip()
                            i += 1
                            break
                        i += 1
                    selected_project = EntryBlock(
                        heading_left=heading_left,
                        date_right=date_right,
                        description=description,
                        bullets=project_bullets,
                        tech=tech,
                    )
                else:
                    i += 1
        elif section == "Education":
            while i < len(lines) and not is_h1(lines[i]):
                line = lines[i].strip()
                if is_h2(line):
                    heading = clean_md_text(line)
                    heading_left, date_right = split_heading_date(heading)
                    i += 1
                    school = collect_paragraph()
                    education.append(
                        EducationBlock(
                            heading_left=heading_left,
                            date_right=date_right,
                            school=school,
                        )
                    )
                else:
                    i += 1
        else:
            while i < len(lines) and not is_h1(lines[i]):
                i += 1

    return ResumeContent(
        meta=ResumeMeta(name=name, title=title, tagline=tagline, contact_lines=contact_lines),
        section_titles=section_titles,
        present_sections=present_sections,
        summary=summary,
        skills=skills,
        experience=experience,
        selected_project=selected_project,
        education=education,
    )


def parse_resume_markdown(path: Path) -> ResumeContent:
    """Compatibility wrapper for callers using the original file-oriented API."""
    return parse_resume_source(path)
