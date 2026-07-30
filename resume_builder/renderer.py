from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import cast

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.shared import Inches, Pt
from docx.styles.style import ParagraphStyle

from resume_builder.docx_utils import (
    add_body_paragraph,
    add_education_entry,
    add_role_entry,
    add_section_heading,
    add_skill_line,
    add_title_block,
    clear_document,
    configure_paragraph_style,
    hex_color,
    set_style_font,
)
from resume_builder.models import ResumeContent, SectionKind
from resume_builder.parser import parse_resume_source
from resume_builder.registry import SECTION_DEFINITIONS
from resume_builder.sections import load_resume_directory
from resume_builder.theme import DEFAULT_THEME, ResumeTheme


def render_summary_section(
    document: DocumentType, content: ResumeContent, theme: ResumeTheme = DEFAULT_THEME
) -> None:
    add_section_heading(document, content.section_titles.summary, theme)
    for idx, paragraph in enumerate(content.summary):
        add_body_paragraph(
            document,
            paragraph,
            theme,
            after=theme.summary_after
            if idx < len(content.summary) - 1
            else theme.summary_last_after,
        )


def render_core_skills_section(
    document: DocumentType, content: ResumeContent, theme: ResumeTheme = DEFAULT_THEME
) -> None:
    add_section_heading(document, content.section_titles.core_skills, theme)
    for skill in content.skills:
        add_skill_line(document, skill.label, skill.value, theme)


def render_professional_experience_section(
    document: DocumentType, content: ResumeContent, theme: ResumeTheme = DEFAULT_THEME
) -> None:
    add_section_heading(document, content.section_titles.professional_experience, theme)
    for entry in content.experience:
        add_role_entry(
            document,
            entry.heading_left,
            entry.date_right,
            entry.description,
            entry.bullets,
            entry.tech,
            theme,
        )


def render_selected_project_section(
    document: DocumentType, content: ResumeContent, theme: ResumeTheme = DEFAULT_THEME
) -> None:
    if content.selected_project is None:
        return
    add_section_heading(document, content.section_titles.selected_project, theme)
    add_role_entry(
        document,
        content.selected_project.heading_left,
        content.selected_project.date_right,
        content.selected_project.description,
        content.selected_project.bullets,
        content.selected_project.tech,
        theme,
    )


def render_education_section(
    document: DocumentType, content: ResumeContent, theme: ResumeTheme = DEFAULT_THEME
) -> None:
    add_section_heading(document, content.section_titles.education, theme)
    for item in content.education:
        add_education_entry(document, item.heading_left, item.date_right, item.school, theme)


SECTION_RENDERERS: dict[
    SectionKind, Callable[[DocumentType, ResumeContent, ResumeTheme], None]
] = {
    SectionKind.SUMMARY: render_summary_section,
    SectionKind.CORE_SKILLS: render_core_skills_section,
    SectionKind.PROFESSIONAL_EXPERIENCE: render_professional_experience_section,
    SectionKind.SELECTED_PROJECT: render_selected_project_section,
    SectionKind.EDUCATION: render_education_section,
}


def _require_string(metadata: dict, key: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            f"Front matter field '{key}' is required and must be a non-empty string"
        )
    return value.strip()


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


def build_markdown_from_source(source_path: Path) -> str:
    source = load_resume_directory(source_path)
    metadata = source.metadata
    name = _require_string(metadata, "name")
    title = _require_string(metadata, "title")
    tagline = _require_string(metadata, "tagline")
    contact_lines = _require_string_list(metadata, "contact_lines")

    lines: list[str] = [
        "---",
        f"name: {name}",
        f"title: {title}",
        f"tagline: {tagline}",
        "contact_lines:",
    ]
    lines.extend(f"  - {line}" for line in contact_lines)
    lines.extend([
        "---",
        "",
        f"# {name}",
        "",
        f"**{title}**",
        "",
        tagline,
        "",
    ])
    lines.extend(contact_lines)
    lines.append("")

    for section in source.sections:
        lines.extend((f"# {section.title}", "", section.content, ""))

    return "\n".join(lines).rstrip() + "\n"


def build_doc_from_source(
    source_path: Path, theme: ResumeTheme = DEFAULT_THEME
) -> DocumentType:
    content = parse_resume_source(source_path)
    doc = Document()
    clear_document(doc)

    section = doc.sections[0]
    section.page_width = Inches(theme.page_width)
    section.page_height = Inches(theme.page_height)
    margin = Inches(theme.margin)
    section.top_margin = margin
    section.bottom_margin = margin
    section.left_margin = margin
    section.right_margin = margin
    section.header_distance = Inches(theme.header_distance)
    section.footer_distance = Inches(theme.footer_distance)

    core_props = doc.core_properties
    core_props.title = f"{content.meta.name} Resume"
    core_props.subject = "Resume"
    core_props.author = content.meta.name

    normal = cast(ParagraphStyle, doc.styles["Normal"])
    set_style_font(
        normal, theme, size=theme.body_size, color=hex_color(theme.primary_text_color)
    )
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    normal.paragraph_format.line_spacing = theme.body_line_spacing

    configure_paragraph_style(
        cast(ParagraphStyle, doc.styles["Title"]),
        theme,
        size=theme.title_size,
        bold=True,
        color=hex_color(theme.ink),
        before=0,
        after=theme.title_after,
        line_spacing=theme.single_line_spacing,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        cast(ParagraphStyle, doc.styles["Subtitle"]),
        theme,
        size=theme.subtitle_size,
        bold=True,
        color=hex_color(theme.blue),
        before=0,
        after=theme.subtitle_after,
        line_spacing=theme.single_line_spacing,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        cast(ParagraphStyle, doc.styles["Heading 1"]),
        theme,
        size=theme.section_heading_size,
        bold=True,
        color=hex_color(theme.blue),
        before=theme.section_before,
        after=theme.section_after,
        line_spacing=theme.single_line_spacing,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        cast(ParagraphStyle, doc.styles["Heading 2"]),
        theme,
        size=theme.heading2_size,
        bold=True,
        color=hex_color(theme.primary_text_color),
        before=0,
        after=theme.heading2_after,
        line_spacing=theme.heading2_line_spacing,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        cast(ParagraphStyle, doc.styles["Heading 3"]),
        theme,
        size=theme.skill_label_size,
        bold=True,
        color=hex_color(theme.blue),
        before=0,
        after=theme.skill_after,
        line_spacing=theme.compact_line_spacing,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        cast(ParagraphStyle, doc.styles["Normal"]),
        theme,
        size=theme.body_size,
        color=hex_color(theme.primary_text_color),
        before=0,
        after=0,
        line_spacing=theme.body_line_spacing,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        cast(ParagraphStyle, doc.styles["List Bullet"]),
        theme,
        size=theme.body_size,
        color=hex_color(theme.primary_text_color),
        before=0,
        after=0,
        line_spacing=theme.compact_line_spacing,
        left_indent=Inches(theme.list_bullet_left_indent),
        first_line_indent=Inches(theme.list_bullet_first_line_indent),
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )

    add_title_block(doc, content.meta, theme)

    for definition in SECTION_DEFINITIONS:
        if definition.kind not in content.present_sections:
            continue
        renderer = SECTION_RENDERERS.get(definition.kind)
        if renderer is not None:
            renderer(doc, content, theme)

    return doc
