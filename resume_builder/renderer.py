from __future__ import annotations

from pathlib import Path
from typing import cast

from docx import Document
from docx.document import Document as DocumentType
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.styles.style import ParagraphStyle
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

from resume_builder.models import ResumeMeta
from resume_builder.parser import parse_resume_source
from resume_builder.theme import DEFAULT_THEME, ResumeTheme


def hex_color(value: str) -> RGBColor:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected 6-digit hex color, got {value!r}")
    return RGBColor(int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def set_font(run, theme: ResumeTheme = DEFAULT_THEME, *, name: str | None = None,
             size: float | None = None, bold: bool = False, italic: bool = False,
             color: RGBColor | None = None) -> None:
    name = name or theme.font_family
    run.font.name = name
    run.font.bold = bold
    run.font.italic = italic
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color


def set_style_font(style: ParagraphStyle, theme: ResumeTheme = DEFAULT_THEME, *, name: str | None = None,
                   size: float = 11, bold: bool = False,
                   color: RGBColor | None = None, italic: bool = False) -> None:
    name = name or theme.font_family
    style.font.name = name
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    if color is not None:
        style.font.color.rgb = color


def configure_paragraph_style(style: ParagraphStyle, theme: ResumeTheme = DEFAULT_THEME, *, size: float,
                              bold: bool = False, color: RGBColor | None = None,
                              italic: bool = False, before: float = 0,
                              after: float = 0, line_spacing: float = 1.2,
                              left_indent: Inches | None = None,
                              first_line_indent: Inches | None = None,
                              alignment: WD_ALIGN_PARAGRAPH | None = None) -> None:
    set_style_font(style, theme, size=size, bold=bold, color=color, italic=italic)
    style.paragraph_format.space_before = Pt(before)
    style.paragraph_format.space_after = Pt(after)
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    style.paragraph_format.line_spacing = line_spacing
    if left_indent is not None:
        style.paragraph_format.left_indent = left_indent
    if first_line_indent is not None:
        style.paragraph_format.first_line_indent = first_line_indent
    if alignment is not None:
        style.paragraph_format.alignment = alignment


def set_paragraph_spacing(paragraph, *, before: float = 0, after: float = 0,
                          line_spacing: float = 1.2) -> None:
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    fmt.line_spacing = line_spacing


def set_keep_with_next(paragraph) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    keep = OxmlElement("w:keepNext")
    ppr.append(keep)


def add_bottom_border(paragraph, color: str = DEFAULT_THEME.light_grey, size: str = DEFAULT_THEME.section_border_size) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    p_bdr = ppr.find(qn("w:pBdr"))
    if p_bdr is None:
        p_bdr = OxmlElement("w:pBdr")
        ppr.append(p_bdr)
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), size)
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    p_bdr.append(bottom)


def clear_document(document: DocumentType) -> None:
    body = document._element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def set_table_fixed_width(table, widths: list[Inches]) -> None:
    table.autofit = False
    tbl_pr = table._tbl.tblPr
    tbl_layout = tbl_pr.find(qn("w:tblLayout"))
    if tbl_layout is None:
        tbl_layout = OxmlElement("w:tblLayout")
        tbl_pr.append(tbl_layout)
    tbl_layout.set(qn("w:type"), "fixed")
    grid = table._tbl.tblGrid
    for idx, width in enumerate(widths):
        if idx < len(grid.gridCol_lst):
            grid.gridCol_lst[idx].set(qn("w:w"), str(int(width.inches * 1440)))
    for row in table.rows:
        for idx, cell in enumerate(row.cells):
            cell.width = widths[idx]
            tc_pr = cell._tc.get_or_add_tcPr()
            tc_w = tc_pr.find(qn("w:tcW"))
            if tc_w is None:
                tc_w = OxmlElement("w:tcW")
                tc_pr.append(tc_w)
            tc_w.set(qn("w:type"), "dxa")
            tc_w.set(qn("w:w"), str(int(widths[idx].inches * 1440)))


def remove_table_borders(table) -> None:
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = borders.find(qn(f"w:{edge}"))
        if el is None:
            el = OxmlElement(f"w:{edge}")
            borders.append(el)
        el.set(qn("w:val"), "nil")


def set_cell_margins(cell, *, top=80, start=80, bottom=80, end=80) -> None:
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for name, val in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{name}"))
        if node is None:
            node = OxmlElement(f"w:{name}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")


def add_section_heading(document: DocumentType, text: str, theme: ResumeTheme = DEFAULT_THEME):
    paragraph = document.add_paragraph(style="Heading 1")
    run = paragraph.add_run(text.upper())
    set_font(run, theme, size=theme.section_heading_size, bold=True, color=hex_color(theme.blue))
    set_paragraph_spacing(paragraph, before=theme.section_before, after=theme.section_after, line_spacing=theme.single_line_spacing)
    set_keep_with_next(paragraph)
    add_bottom_border(paragraph, color=theme.light_grey, size=theme.section_border_size)
    return paragraph


def add_body_paragraph(document: DocumentType, text: str, theme: ResumeTheme = DEFAULT_THEME,
                       *, style_name: str = "Normal", before: float = 0, after: float | None = None,
                       color: RGBColor | None = None):
    paragraph = document.add_paragraph(style=style_name)
    run = paragraph.add_run(text)
    set_font(run, theme, size=theme.body_size, color=color or hex_color(theme.primary_text_color))
    set_paragraph_spacing(paragraph, before=before, after=theme.body_after if after is None else after, line_spacing=theme.body_line_spacing)
    return paragraph


def add_contact_line(document: DocumentType, line: str, theme: ResumeTheme = DEFAULT_THEME, *, is_last: bool = False):
    paragraph = document.add_paragraph(style="Normal")
    run = paragraph.add_run(line)
    set_font(run, theme, size=theme.contact_size, color=hex_color(theme.grey))
    set_paragraph_spacing(
        paragraph,
        before=0,
        after=theme.contact_after if is_last else 0,
        line_spacing=theme.single_line_spacing,
    )


def add_contact_block(document: DocumentType, lines: list[str], theme: ResumeTheme = DEFAULT_THEME) -> None:
    for idx, line in enumerate(lines):
        add_contact_line(document, line, theme, is_last=idx == len(lines) - 1)


def add_title_block(document: DocumentType, meta: ResumeMeta, theme: ResumeTheme = DEFAULT_THEME) -> None:
    p = document.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(meta.name)
    set_font(r, theme, size=theme.title_size, bold=True, color=hex_color(theme.ink))
    set_paragraph_spacing(p, before=0, after=theme.title_after, line_spacing=theme.single_line_spacing)
    set_keep_with_next(p)

    p = document.add_paragraph(style="Subtitle")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(meta.title)
    set_font(r, theme, size=theme.subtitle_size, bold=True, color=hex_color(theme.blue))
    set_paragraph_spacing(p, before=0, after=theme.subtitle_after, line_spacing=theme.single_line_spacing)
    set_keep_with_next(p)

    p = document.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(meta.tagline)
    set_font(r, theme, size=theme.tagline_size, color=hex_color(theme.grey))
    set_paragraph_spacing(p, before=0, after=theme.tagline_after, line_spacing=theme.single_line_spacing)

    add_contact_block(document, meta.contact_lines, theme)


def add_skill_line(document: DocumentType, label: str, text: str, theme: ResumeTheme = DEFAULT_THEME) -> None:
    p = document.add_paragraph(style="Heading 3")
    r1 = p.add_run(label)
    set_font(r1, theme, size=theme.skill_label_size, bold=True, color=hex_color(theme.blue))
    r2 = p.add_run(f": {text}")
    set_font(r2, theme, size=theme.skill_label_size, color=hex_color(theme.primary_text_color))
    set_paragraph_spacing(p, before=0, after=theme.skill_after, line_spacing=theme.compact_line_spacing)


def add_role_entry(document: DocumentType, heading_left: str, date_right: str, description: str,
                   bullets: list[str], tech: str, theme: ResumeTheme = DEFAULT_THEME) -> None:
    table = document.add_table(rows=1, cols=2)
    set_table_fixed_width(
        table,
        [Inches(theme.role_table_left_width), Inches(theme.role_table_right_width)],
    )
    remove_table_borders(table)

    left, right = table.rows[0].cells
    set_cell_margins(left, top=0, start=0, bottom=0, end=0)
    set_cell_margins(right, top=0, start=0, bottom=0, end=0)

    p_left = left.paragraphs[0]
    p_left.style = "Heading 2"
    p_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_left.paragraph_format.space_before = Pt(0)
    p_left.paragraph_format.space_after = Pt(0)
    p_left.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    r_left = p_left.add_run(heading_left)
    set_font(r_left, theme, size=theme.role_heading_size, bold=True, color=hex_color(theme.primary_text_color))

    p_right = right.paragraphs[0]
    p_right.style = "Normal"
    p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_right.paragraph_format.space_before = Pt(0)
    p_right.paragraph_format.space_after = Pt(0)
    p_right.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    r_right = p_right.add_run(date_right)
    set_font(r_right, theme, size=theme.date_size, color=hex_color(theme.primary_text_color))

    desc = document.add_paragraph(style="Normal")
    r = desc.add_run(description)
    set_font(r, theme, size=theme.body_size, color=hex_color(theme.primary_text_color))
    tail_after = theme.role_tech_after if not bullets and not tech.strip() else theme.role_description_after
    set_paragraph_spacing(
        desc,
        before=theme.role_description_before,
        after=tail_after,
        line_spacing=theme.role_description_line_spacing,
    )

    for bullet in bullets:
        p = document.add_paragraph(style="List Bullet")
        r = p.add_run(bullet)
        set_font(r, theme, size=theme.body_size, color=hex_color(theme.primary_text_color))
        set_paragraph_spacing(p, before=0, after=theme.role_bullet_after, line_spacing=theme.compact_line_spacing)

    if tech.strip():
        tech_p = document.add_paragraph(style="Normal")
        t1 = tech_p.add_run("Tech:")
        set_font(t1, theme, size=theme.tech_label_size, italic=True, color=hex_color(theme.grey))
        t2 = tech_p.add_run(f" {tech}")
        set_font(t2, theme, size=theme.tech_value_size, color=hex_color(theme.grey))
        set_paragraph_spacing(tech_p, before=theme.role_tech_before, after=theme.role_tech_after, line_spacing=theme.single_line_spacing)


def add_education_entry(document: DocumentType, heading_left: str, date_right: str, school: str,
                        theme: ResumeTheme = DEFAULT_THEME) -> None:
    table = document.add_table(rows=1, cols=2)
    set_table_fixed_width(
        table,
        [Inches(theme.role_table_left_width), Inches(theme.role_table_right_width)],
    )
    remove_table_borders(table)
    left, right = table.rows[0].cells
    set_cell_margins(left, top=0, start=0, bottom=0, end=0)
    set_cell_margins(right, top=0, start=0, bottom=0, end=0)

    p_left = left.paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_left = p_left.add_run(heading_left)
    set_font(r_left, theme, size=theme.role_heading_size, bold=True, color=hex_color(theme.primary_text_color))
    p_left.paragraph_format.space_after = Pt(0)
    p_left.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    p_right = right.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_right = p_right.add_run(date_right)
    set_font(r_right, theme, size=theme.date_size, color=hex_color(theme.primary_text_color))
    p_right.paragraph_format.space_after = Pt(0)
    p_right.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    p_school = document.add_paragraph(style="Normal")
    r_school = p_school.add_run(school)
    set_font(r_school, theme, size=theme.body_size, color=hex_color(theme.primary_text_color))
    set_paragraph_spacing(p_school, before=2, after=theme.education_school_after, line_spacing=theme.compact_line_spacing)


def add_experience_entry(document: DocumentType, heading_left: str, date_right: str, description: str,
                         bullets: list[str], tech: str, theme: ResumeTheme = DEFAULT_THEME) -> None:
    add_role_entry(document, heading_left, date_right, description, bullets, tech, theme)


def build_doc_from_source(source_path: Path, theme: ResumeTheme = DEFAULT_THEME) -> DocumentType:
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
    set_style_font(normal, theme, size=theme.body_size, color=hex_color(theme.primary_text_color))
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

    add_section_heading(doc, "Summary", theme)
    for idx, paragraph in enumerate(content.summary):
        add_body_paragraph(
            doc,
            paragraph,
            theme,
            after=theme.summary_after if idx < len(content.summary) - 1 else theme.summary_last_after,
        )

    add_section_heading(doc, "Core Skills", theme)
    for skill in content.skills:
        add_skill_line(doc, skill.label, skill.value, theme)

    add_section_heading(doc, "Professional Experience", theme)
    for entry in content.experience:
        add_experience_entry(
            doc,
            entry.heading_left,
            entry.date_right,
            entry.description,
            entry.bullets,
            entry.tech,
            theme,
        )

    if content.selected_project is not None:
        add_section_heading(doc, "Selected Project", theme)
        add_experience_entry(
            doc,
            content.selected_project.heading_left,
            content.selected_project.date_right,
            content.selected_project.description,
            content.selected_project.bullets,
            content.selected_project.tech,
            theme,
        )

    add_section_heading(doc, "Education", theme)
    for item in content.education:
        add_education_entry(doc, item.heading_left, item.date_right, item.school, theme)

    return doc


def build_doc_from_markdown(md_path: Path, theme: ResumeTheme = DEFAULT_THEME) -> DocumentType:
    """Compatibility wrapper for callers using the original file-oriented API."""
    return build_doc_from_source(md_path, theme)
