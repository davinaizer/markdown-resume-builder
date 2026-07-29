from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import frontmatter
from frontmatter.default_handlers import YAMLHandler


@dataclass(frozen=True)
class SectionDefinition:
    kind: str
    canonical_title: str
    filename: str
    optional: bool = False


@dataclass(frozen=True)
class LoadedSection:
    kind: str
    canonical_title: str
    title: str
    content: str


@dataclass(frozen=True)
class ResumeSource:
    metadata: dict
    sections: list[LoadedSection]

    @property
    def content(self) -> str:
        return "\n\n".join(
            f"# {section.canonical_title}\n\n{section.content}"
            for section in self.sections
        )


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


def _load_frontmatter_file(path: Path) -> frontmatter.Post:
    text = path.read_text(encoding="utf-8")
    handler = YAMLHandler()
    if not handler.detect(text):
        raise ValueError(f"Markdown file must start with YAML front matter: {path}")
    return frontmatter.loads(text, handler=handler)


def load_resume_directory(path: Path) -> ResumeSource:
    meta_path = path / "meta.md"
    if not meta_path.is_file():
        raise FileNotFoundError(f"Resume metadata file not found: {meta_path}")

    meta = _load_frontmatter_file(meta_path)
    sections_path = path / "sections"
    loaded_sections: list[LoadedSection] = []

    for definition in SECTION_DEFINITIONS:
        section_path = sections_path / definition.filename
        if not section_path.is_file():
            if not definition.optional:
                print(
                    f"Warning: resume section file not found; skipping: {section_path}",
                    file=sys.stderr,
                )
            continue

        section = _load_frontmatter_file(section_path)
        title = section.metadata.get("title")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(
                f"Front matter field 'title' is required and must be a non-empty string: {section_path}"
            )
        loaded_sections.append(
            LoadedSection(
                kind=definition.kind,
                canonical_title=definition.canonical_title,
                title=title.strip(),
                content=section.content.strip(),
            )
        )

    return ResumeSource(metadata=meta.metadata, sections=loaded_sections)
