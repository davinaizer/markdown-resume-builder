from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResumeTheme:
    font_family: str = "IBM Plex Sans"
    primary_text_color: str = "222222"
    ink: str = "2F5FA7"
    blue: str = "2F5FA7"
    grey: str = "5E6470"
    light_grey: str = "C9D2DF"

    title_size: float = 27
    subtitle_size: float = 16
    tagline_size: float = 11
    contact_size: float = 10.5
    section_heading_size: float = 13
    skill_label_size: float = 11
    body_size: float = 11
    role_heading_size: float = 12
    date_size: float = 10
    tech_label_size: float = 10.5
    tech_value_size: float = 10.5
    heading2_size: float = 11
    heading2_line_spacing: float = 1.0
    heading2_after: float = 0
    summary_after: float = 2
    summary_last_after: float = 4
    skill_after: float = 2

    title_after: float = 2
    subtitle_after: float = 0
    tagline_after: float = 8
    section_before: float = 12
    section_after: float = 5
    body_after: float = 3
    contact_after: float = 7
    role_description_before: float = 2
    role_description_after: float = 3
    role_description_line_spacing: float = 1.15
    role_bullet_after: float = 0
    role_tech_before: float = 1
    role_tech_after: float = 7
    education_school_after: float = 8

    body_line_spacing: float = 1.18
    compact_line_spacing: float = 1.12
    single_line_spacing: float = 1.0
    list_bullet_left_indent: float = 0.22
    list_bullet_first_line_indent: float = -0.18

    section_border_size: str = "8"

    page_width: float = 8.5
    page_height: float = 11
    margin: float = 0.55
    header_distance: float = 0.35
    footer_distance: float = 0.35


DEFAULT_THEME = ResumeTheme()
