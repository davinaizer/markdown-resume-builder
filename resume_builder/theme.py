from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeTheme:
    font_family: str = "IBM Plex Sans"
    primary_text_color: str = "222222"
    ink: str = "315B96"
    blue: str = "315B96"
    grey: str = "5E6470"
    light_grey: str = "C9D2DF"

    title_size: float = 25.5
    subtitle_size: float = 15
    tagline_size: float = 11
    contact_size: float = 10.5
    section_heading_size: float = 13
    skill_label_size: float = 11
    body_size: float = 11
    role_heading_size: float = 12
    date_size: float = 10.5
    tech_label_size: float = 10.5
    tech_value_size: float = 10.5
    heading2_size: float = 11
    heading2_line_spacing: float = 1.0
    heading2_after: float = 0
    summary_after: float = 4
    summary_last_after: float = 5
    skill_after: float = 2

    title_after: float = 2
    subtitle_after: float = 0
    tagline_after: float = 6
    section_before: float = 10
    section_after: float = 4
    body_after: float = 3
    contact_after: float = 7
    role_description_before: float = 2
    role_description_after: float = 3
    role_description_line_spacing: float = 1.15
    role_bullet_after: float = 0
    role_tech_before: float = 1
    role_tech_after: float = 7
    education_school_after: float = 8

    body_line_spacing: float = 1.14
    compact_line_spacing: float = 1.12
    single_line_spacing: float = 1.0
    list_bullet_left_indent: float = 0.22
    list_bullet_first_line_indent: float = -0.18
    nested_role_left_indent: float = 0.18

    section_border_size: str = "4"

    page_width: float = 8.5
    page_height: float = 11
    margin: float = 0.55
    header_distance: float = 0.35
    footer_distance: float = 0.35


DEFAULT_THEME = ResumeTheme()
