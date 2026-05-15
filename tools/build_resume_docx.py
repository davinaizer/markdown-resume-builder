from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


OUT_PATH = Path("docs/my-resume.docx")
FONT = "IBM Plex Sans"
INK = RGBColor(0x10, 0x24, 0x3D)
BLUE = RGBColor(0x1F, 0x3A, 0x5F)
GREY = RGBColor(0x4F, 0x55, 0x63)
LIGHT_GREY = "BFC6D1"


@dataclass
class ResumeMeta:
    name: str
    title: str
    tagline: str
    contact: str


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
    selected_project: EntryBlock
    education: list[EducationBlock]


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


def parse_resume_markdown(path: Path) -> ResumeContent:
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0

    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or not is_h1(lines[i]):
        raise ValueError("Resume markdown must start with a top-level name heading")
    name = clean_md_text(lines[i])
    i += 1

    title, i = next_content_line(lines, i)
    if title is None:
        raise ValueError("Missing title line after name")
    title = clean_md_text(title)
    i += 1

    tagline, i = next_content_line(lines, i)
    if tagline is None:
        raise ValueError("Missing tagline line after title")
    tagline = clean_md_text(tagline)
    i += 1

    contact_lines: list[str] = []
    while i < len(lines):
        line = lines[i].strip()
        if is_rule(line):
            i += 1
            break
        if line:
            contact_lines.append(clean_md_text(line))
        i += 1
    contact = " | ".join(contact_lines)

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
                    if label.startswith("## "):
                        label = label[3:]
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
                    if heading.startswith("## "):
                        heading = heading[3:]
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
                    if heading.startswith("## "):
                        heading = heading[3:]
                    heading_left, date_right = split_heading_date(heading)
                    i += 1
                    description = collect_paragraph()
                    bullets = []
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
                    selected_project = EntryBlock(
                        heading_left=heading_left,
                        date_right=date_right,
                        description=description,
                        bullets=bullets,
                        tech=tech,
                    )
                else:
                    i += 1
        elif section == "Education":
            while i < len(lines) and not is_h1(lines[i]):
                line = lines[i].strip()
                if is_h2(line):
                    heading = clean_md_text(line)
                    if heading.startswith("## "):
                        heading = heading[3:]
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

    if selected_project is None:
        raise ValueError("Selected Project section was not parsed")

    return ResumeContent(
        meta=ResumeMeta(name=name, title=title, tagline=tagline, contact=contact),
        summary=summary,
        skills=skills,
        experience=experience,
        selected_project=selected_project,
        education=education,
    )


def set_font(run, *, name: str = FONT, size: float | None = None, bold: bool = False,
             italic: bool = False, color: RGBColor | None = None) -> None:
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:ascii"), name)
    run._element.rPr.rFonts.set(qn("w:hAnsi"), name)
    run.font.bold = bold
    run.font.italic = italic
    if size is not None:
        run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color


def set_style_font(style, *, name: str = FONT, size: float = 11, bold: bool = False,
                   color: RGBColor = RGBColor(0, 0, 0), italic: bool = False) -> None:
    style.font.name = name
    style._element.rPr.rFonts.set(qn("w:ascii"), name)
    style._element.rPr.rFonts.set(qn("w:hAnsi"), name)
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.italic = italic
    style.font.color.rgb = color


def configure_paragraph_style(style, *, size: float, bold: bool = False,
                              color: RGBColor = RGBColor(0, 0, 0),
                              italic: bool = False, before: float = 0,
                              after: float = 0, line_spacing: float = 1.2,
                              left_indent: Inches | None = None,
                              first_line_indent: Inches | None = None,
                              alignment: WD_ALIGN_PARAGRAPH | None = None) -> None:
    set_style_font(style, size=size, bold=bold, color=color, italic=italic)
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


def set_keep_lines(paragraph) -> None:
    ppr = paragraph._p.get_or_add_pPr()
    keep = OxmlElement("w:keepLines")
    ppr.append(keep)


def add_bottom_border(paragraph, color: str = LIGHT_GREY, size: str = "8") -> None:
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


def clear_document(document: Document) -> None:
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


def add_section_heading(document: Document, text: str):
    paragraph = document.add_paragraph(style="Heading 1")
    run = paragraph.add_run(text.upper())
    set_font(run, size=12.5, bold=True, color=BLUE)
    set_paragraph_spacing(paragraph, before=12, after=5, line_spacing=1.0)
    set_keep_with_next(paragraph)
    add_bottom_border(paragraph)
    return paragraph


def add_body_paragraph(document: Document, text: str, *, style_name: str = "Normal",
                       before: float = 0, after: float = 3, color: RGBColor = RGBColor(0, 0, 0)):
    paragraph = document.add_paragraph(style=style_name)
    run = paragraph.add_run(text)
    set_font(run, size=10.5, color=color)
    set_paragraph_spacing(paragraph, before=before, after=after, line_spacing=1.18)
    return paragraph


def add_contact_line(document: Document, text: str):
    paragraph = document.add_paragraph(style="Normal")
    run = paragraph.add_run(text)
    set_font(run, size=10.0, color=GREY)
    set_paragraph_spacing(paragraph, before=0, after=7, line_spacing=1.0)
    return paragraph


def add_title_block(document: Document, meta: ResumeMeta) -> None:
    p = document.add_paragraph(style="Title")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(meta.name)
    set_font(r, size=23, bold=True, color=INK)
    set_paragraph_spacing(p, before=0, after=2, line_spacing=1.0)
    set_keep_with_next(p)

    p = document.add_paragraph(style="Subtitle")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(meta.title)
    set_font(r, size=13.5, bold=True, color=BLUE)
    set_paragraph_spacing(p, before=0, after=0, line_spacing=1.0)
    set_keep_with_next(p)

    p = document.add_paragraph(style="Normal")
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(meta.tagline)
    set_font(r, size=11.25, color=GREY)
    set_paragraph_spacing(p, before=0, after=8, line_spacing=1.0)

    add_contact_line(document, meta.contact)


def add_skill_line(document: Document, label: str, text: str) -> None:
    p = document.add_paragraph(style="Heading 3")
    r1 = p.add_run(label)
    set_font(r1, size=10.5, bold=True, color=BLUE)
    r2 = p.add_run(f": {text}")
    set_font(r2, size=10.5, color=RGBColor(0, 0, 0))
    set_paragraph_spacing(p, before=0, after=2, line_spacing=1.12)


def add_role_entry(document: Document, heading_left: str, date_right: str, description: str,
                   bullets: list[str], tech: str, left_width: Inches = Inches(5.95),
                   right_width: Inches = Inches(1.45)) -> None:
    table = document.add_table(rows=1, cols=2)
    set_table_fixed_width(table, [left_width, right_width])
    remove_table_borders(table)

    left, right = table.rows[0].cells
    set_cell_margins(left, top=0, start=0, bottom=0, end=0)
    set_cell_margins(right, top=0, start=0, bottom=0, end=0)

    p_left = left.paragraphs[0]
    p_left.style = document.styles["Heading 2"]
    p_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_left.paragraph_format.space_before = Pt(0)
    p_left.paragraph_format.space_after = Pt(0)
    p_left.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    r_left = p_left.add_run(heading_left)
    set_font(r_left, size=10.5, bold=True, color=RGBColor(0, 0, 0))

    p_right = right.paragraphs[0]
    p_right.style = document.styles["Normal"]
    p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_right.paragraph_format.space_before = Pt(0)
    p_right.paragraph_format.space_after = Pt(0)
    p_right.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    r_right = p_right.add_run(date_right)
    set_font(r_right, size=10.5, color=RGBColor(0, 0, 0))

    desc = document.add_paragraph(style="Normal")
    r = desc.add_run(description)
    set_font(r, size=10.5, color=RGBColor(0, 0, 0))
    tail_after = 7 if not bullets and not tech.strip() else 3
    set_paragraph_spacing(desc, before=2, after=tail_after, line_spacing=1.15)

    for bullet in bullets:
        p = document.add_paragraph(style="List Bullet")
        r = p.add_run(bullet)
        set_font(r, size=10.5, color=RGBColor(0, 0, 0))
        set_paragraph_spacing(p, before=0, after=0, line_spacing=1.12)

    if tech.strip():
        tech_p = document.add_paragraph(style="Normal")
        t1 = tech_p.add_run("Tech:")
        set_font(t1, size=10.5, italic=True, color=GREY)
        t2 = tech_p.add_run(f" {tech}")
        set_font(t2, size=10.5, color=GREY)
        set_paragraph_spacing(tech_p, before=1, after=7, line_spacing=1.0)


def add_education_entry(document: Document, heading_left: str, date_right: str, school: str) -> None:
    table = document.add_table(rows=1, cols=2)
    set_table_fixed_width(table, [Inches(5.95), Inches(1.45)])
    remove_table_borders(table)
    left, right = table.rows[0].cells
    set_cell_margins(left, top=0, start=0, bottom=0, end=0)
    set_cell_margins(right, top=0, start=0, bottom=0, end=0)

    p_left = left.paragraphs[0]
    p_left.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_left = p_left.add_run(heading_left)
    set_font(r_left, size=10.5, bold=True, color=RGBColor(0, 0, 0))
    p_left.paragraph_format.space_after = Pt(0)
    p_left.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    p_right = right.paragraphs[0]
    p_right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_right = p_right.add_run(date_right)
    set_font(r_right, size=10.5, color=RGBColor(0, 0, 0))
    p_right.paragraph_format.space_after = Pt(0)
    p_right.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE

    p_school = document.add_paragraph(style="Normal")
    r_school = p_school.add_run(school)
    set_font(r_school, size=10.5, color=RGBColor(0, 0, 0))
    set_paragraph_spacing(p_school, before=2, after=8, line_spacing=1.12)


def add_experience_entry(document: Document, heading_left: str, date_right: str, description: str,
                         bullets: list[str], tech: str) -> None:
    add_role_entry(document, heading_left, date_right, description, bullets, tech)


def build_doc_from_markdown(md_path: Path) -> Document:
    content = parse_resume_markdown(md_path)
    doc = Document()
    clear_document(doc)

    section = doc.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    margin = Inches(0.55)
    section.top_margin = margin
    section.bottom_margin = margin
    section.left_margin = margin
    section.right_margin = margin
    section.header_distance = Inches(0.35)
    section.footer_distance = Inches(0.35)

    core_props = doc.core_properties
    core_props.title = f"{content.meta.name} Resume"
    core_props.subject = "Resume"
    core_props.author = content.meta.name

    normal = doc.styles["Normal"]
    set_style_font(normal, size=10.5, color=RGBColor(0, 0, 0))
    normal.paragraph_format.space_before = Pt(0)
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
    normal.paragraph_format.line_spacing = 1.18

    configure_paragraph_style(
        doc.styles["Title"],
        size=23,
        bold=True,
        color=INK,
        before=0,
        after=2,
        line_spacing=1.0,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        doc.styles["Subtitle"],
        size=13.5,
        bold=True,
        color=BLUE,
        before=0,
        after=0,
        line_spacing=1.0,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        doc.styles["Heading 1"],
        size=12.5,
        bold=True,
        color=BLUE,
        before=12,
        after=5,
        line_spacing=1.0,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        doc.styles["Heading 2"],
        size=10.5,
        bold=True,
        color=RGBColor(0, 0, 0),
        before=0,
        after=0,
        line_spacing=1.0,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        doc.styles["Heading 3"],
        size=10.5,
        bold=True,
        color=BLUE,
        before=0,
        after=2,
        line_spacing=1.12,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        doc.styles["Normal"],
        size=10.5,
        color=RGBColor(0, 0, 0),
        before=0,
        after=0,
        line_spacing=1.18,
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )
    configure_paragraph_style(
        doc.styles["List Bullet"],
        size=10.5,
        color=RGBColor(0, 0, 0),
        before=0,
        after=0,
        line_spacing=1.12,
        left_indent=Inches(0.22),
        first_line_indent=Inches(-0.18),
        alignment=WD_ALIGN_PARAGRAPH.LEFT,
    )

    add_title_block(doc, content.meta)

    add_section_heading(doc, "Summary")
    for idx, paragraph in enumerate(content.summary):
        add_body_paragraph(doc, paragraph, after=2 if idx < len(content.summary) - 1 else 4)

    add_section_heading(doc, "Core Skills")
    for skill in content.skills:
        add_skill_line(doc, skill.label, skill.value)

    add_section_heading(doc, "Professional Experience")
    for entry in content.experience:
        add_experience_entry(
            doc,
            entry.heading_left,
            entry.date_right,
            entry.description,
            entry.bullets,
            entry.tech,
        )

    add_section_heading(doc, "Selected Project")
    add_experience_entry(
        doc,
        content.selected_project.heading_left,
        content.selected_project.date_right,
        content.selected_project.description,
        content.selected_project.bullets,
        content.selected_project.tech,
    )

    add_section_heading(doc, "Education")
    for item in content.education:
        add_education_entry(doc, item.heading_left, item.date_right, item.school)

    return doc


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a resume DOCX from Markdown.")
    parser.add_argument("input_md", nargs="?", default=str(Path("docs/my-resume.md")))
    parser.add_argument("-o", "--output", default=str(OUT_PATH))
    args = parser.parse_args()

    input_md = Path(args.input_md)
    output_docx = Path(args.output)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = build_doc_from_markdown(input_md)
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_docx))
    print(f"Wrote {output_docx}")


if __name__ == "__main__":
    main()
