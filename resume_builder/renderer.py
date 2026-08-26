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
    add_entry_heading,
    add_nested_role_entry,
    add_role_entry,
    add_section_heading,
    add_skill_line,
    add_title_block,
    clear_document,
    configure_paragraph_style,
    hex_color,
    set_style_font,
)
from resume_builder.models import (
    ExperienceEntry,
    ExperienceType,
    ResumeContent,
    SectionKind,
)
from resume_builder.parser import parse_experience_lines, parse_resume_source
from resume_builder.profiles import (
    OutputProfile,
    coerce_output_profile,
    flatten_experience,
    prepare_content,
    validate_experience,
)
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


def experience_heading(entry: ExperienceEntry) -> str:
    fields = [
        field for field in (entry.title, entry.organisation, entry.location) if field
    ]
    return " | ".join(fields)


def role_heading(role_title: str, role_organisation: str | None) -> str:
    return " | ".join(field for field in (role_title, role_organisation) if field)


def render_career_break(
    document: DocumentType,
    entry: ExperienceEntry,
    theme: ResumeTheme,
    *,
    align_date: bool = True,
) -> None:
    add_entry_heading(
        document,
        experience_heading(entry),
        entry.date_right,
        theme,
        align_date=align_date,
    )
    for index, description in enumerate(entry.descriptions):
        add_body_paragraph(
            document,
            description,
            theme,
            before=theme.role_description_before if index == 0 else 0,
            after=theme.role_tech_after
            if index == len(entry.descriptions) - 1
            else theme.role_description_after,
        )


def render_professional_experience_section(
    document: DocumentType,
    content: ResumeContent,
    theme: ResumeTheme = DEFAULT_THEME,
    *,
    profile: OutputProfile | str = OutputProfile.GROUPED,
) -> None:
    selected_profile = coerce_output_profile(profile)
    prepared_content = prepare_content(content, selected_profile)
    align_date = selected_profile is OutputProfile.GROUPED
    add_section_heading(
        document, prepared_content.section_titles.professional_experience, theme
    )
    for entry in prepared_content.experience:
        if entry.type is ExperienceType.CAREER_BREAK:
            render_career_break(document, entry, theme, align_date=align_date)
            continue
        add_role_entry(
            document,
            experience_heading(entry),
            entry.date_right,
            entry.descriptions,
            entry.bullets,
            entry.tech,
            theme,
            align_date=align_date,
        )
        if selected_profile is OutputProfile.GROUPED:
            for role in entry.roles:
                add_nested_role_entry(
                    document,
                    role_heading(role.title, role.organisation),
                    role.date_right,
                    role.descriptions,
                    role.bullets,
                    role.tech,
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
        content.selected_project.descriptions,
        content.selected_project.bullets,
        content.selected_project.tech,
        theme,
    )


def render_education_section(
    document: DocumentType, content: ResumeContent, theme: ResumeTheme = DEFAULT_THEME
) -> None:
    add_section_heading(document, content.section_titles.education, theme)
    for item in content.education:
        add_education_entry(
            document, item.heading_left, item.date_right, item.school, theme
        )


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


def _markdown_heading(fields: tuple[str | None, ...]) -> str:
    return " | ".join(field for field in fields if field)


def _append_markdown_content(
    lines: list[str],
    descriptions: tuple[str, ...],
    bullets: tuple[str, ...],
    tech: str,
    *,
    allow_details: bool = True,
) -> None:
    for description in descriptions:
        lines.extend((description, ""))
    if not allow_details:
        return
    lines.extend(f"- {bullet}" for bullet in bullets)
    if bullets:
        lines.append("")
    if tech.strip():
        lines.extend((f"**Tech:** {tech}", ""))


def render_experience_markdown(
    entries: tuple[ExperienceEntry, ...],
    *,
    profile: OutputProfile | str = OutputProfile.ATS,
) -> str:
    selected_profile = coerce_output_profile(profile)
    validate_experience(entries)
    prepared_entries = (
        flatten_experience(entries)
        if selected_profile is OutputProfile.ATS
        else entries
    )
    lines: list[str] = []
    for index, entry in enumerate(prepared_entries):
        heading = _markdown_heading(
            (
                entry.title,
                entry.organisation,
                entry.location,
                entry.date_right,
            )
        )
        marker = f"<!-- experience: {entry.type.value} -->"
        lines.extend((f"## **{heading}**", ""))
        if selected_profile is OutputProfile.GROUPED:
            lines.extend((marker, ""))
        _append_markdown_content(
            lines,
            entry.descriptions,
            entry.bullets,
            entry.tech,
            allow_details=entry.type is not ExperienceType.CAREER_BREAK,
        )
        if selected_profile is OutputProfile.GROUPED:
            for role in entry.roles:
                role_heading = _markdown_heading(
                    (role.title, role.organisation, role.date_right)
                )
                lines.extend((f"### **{role_heading}**", ""))
                _append_markdown_content(
                    lines, role.descriptions, role.bullets, role.tech
                )
        if index < len(prepared_entries) - 1:
            lines.extend(("---", ""))
    return "\n".join(lines).rstrip()


def build_markdown_from_source(
    source_path: Path,
    *,
    profile: OutputProfile | str = OutputProfile.ATS,
) -> str:
    selected_profile = coerce_output_profile(profile)
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
    lines.extend(
        [
            "---",
            "",
            f"# {name}",
            "",
            f"**{title}**",
            "",
            tagline,
            "",
        ]
    )
    lines.extend(contact_lines)
    lines.append("")

    for section in source.sections:
        section_content = section.content
        if section.kind is SectionKind.PROFESSIONAL_EXPERIENCE:
            entries = parse_experience_lines(section.content.splitlines())
            section_content = render_experience_markdown(
                entries, profile=selected_profile
            )
        lines.extend((f"# {section.title}", "", section_content, ""))

    return "\n".join(lines).rstrip() + "\n"


def build_doc_from_source(
    source_path: Path,
    theme: ResumeTheme = DEFAULT_THEME,
    *,
    profile: OutputProfile | str = OutputProfile.ATS,
) -> DocumentType:
    selected_profile = coerce_output_profile(profile)
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

    for section_kind in content.section_order:
        renderer = SECTION_RENDERERS.get(section_kind)
        if renderer is None or section_kind not in content.present_sections:
            continue
        if section_kind is SectionKind.PROFESSIONAL_EXPERIENCE:
            render_professional_experience_section(
                doc, content, theme, profile=selected_profile
            )
        else:
            renderer(doc, content, theme)

    return doc
