from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

import frontmatter
from frontmatter.default_handlers import YAMLHandler

from resume_builder.models import SectionKind
from resume_builder.registry import SECTION_DEFINITIONS, SectionDefinition


@dataclass(frozen=True, slots=True)
class LoadedSection:
    kind: SectionKind
    canonical_title: str
    title: str
    content: str


@dataclass(frozen=True, slots=True)
class ResumeSource:
    metadata: dict
    sections: tuple[LoadedSection, ...]

    @property
    def content(self) -> str:
        return "\n\n".join(
            f"# {section.title}\n\n{section.content}" for section in self.sections
        )


def _load_frontmatter_file(path: Path) -> frontmatter.Post:
    text = path.read_text(encoding="utf-8")
    handler = YAMLHandler()
    if not handler.detect(text):
        raise ValueError(f"Markdown file must start with YAML front matter: {path}")
    return frontmatter.loads(text, handler=handler)


def _ordered_section_definitions(metadata: dict) -> tuple[SectionDefinition, ...]:
    sections = metadata.get("sections")
    if sections is None:
        return SECTION_DEFINITIONS
    if not isinstance(sections, list) or not sections:
        raise ValueError(
            "Front matter field 'sections' is required to be a non-empty list of section kinds"
        )

    definitions_by_kind = {
        definition.kind: definition for definition in SECTION_DEFINITIONS
    }
    ordered_definitions: list[SectionDefinition] = []
    seen_kinds: set[str] = set()

    for item in sections:
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                "Front matter field 'sections' must contain only non-empty section kind strings"
            )
        try:
            kind = SectionKind(item.strip())
        except ValueError as exc:
            raise ValueError(
                f"Unknown section kind in front matter field 'sections': {item!r}"
            ) from exc
        if kind in seen_kinds:
            raise ValueError(
                f"Duplicate section kind in front matter field 'sections': {item!r}"
            )
        definition = definitions_by_kind.get(kind)
        if definition is None:
            raise ValueError(
                f"No canonical section definition exists for kind: {item!r}"
            )
        ordered_definitions.append(definition)
        seen_kinds.add(kind)

    return tuple(ordered_definitions)


def load_resume_directory(path: Path) -> ResumeSource:
    meta_path = path / "meta.md"
    if not meta_path.is_file():
        raise FileNotFoundError(f"Resume metadata file not found: {meta_path}")

    meta = _load_frontmatter_file(meta_path)
    sections_path = path / "sections"
    loaded_sections: list[LoadedSection] = []

    for definition in _ordered_section_definitions(meta.metadata):
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

    return ResumeSource(metadata=meta.metadata, sections=tuple(loaded_sections))
