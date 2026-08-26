from __future__ import annotations

from dataclasses import replace
from enum import StrEnum

from resume_builder.models import (
    ExperienceEntry,
    ExperienceRole,
    ExperienceType,
    ResumeContent,
)


class OutputProfile(StrEnum):
    ATS = "ats"
    GROUPED = "grouped"


def coerce_output_profile(profile: OutputProfile | str) -> OutputProfile:
    try:
        return OutputProfile(profile)
    except ValueError as error:
        choices = ", ".join(item.value for item in OutputProfile)
        raise ValueError(
            f"Unknown output profile {profile!r}; choose from {choices}"
        ) from error


def _merge_technology(parent: str, role: str) -> str:
    parent = parent.strip()
    role = role.strip()
    if parent and role:
        return f"{parent} • {role}"
    return parent or role


def flatten_role(
    entry: ExperienceEntry, role: ExperienceRole, *, include_parent_context: bool
) -> ExperienceEntry:
    descriptions = (
        (*entry.descriptions, *role.descriptions)
        if include_parent_context
        else role.descriptions
    )
    bullets = (
        (*entry.bullets, *role.bullets) if include_parent_context else role.bullets
    )
    tech = (
        _merge_technology(entry.tech, role.tech)
        if include_parent_context
        else role.tech
    )
    return ExperienceEntry(
        type=entry.type,
        title=role.title,
        organisation=role.organisation or entry.organisation,
        location=entry.location,
        date_right=role.date_right,
        descriptions=descriptions,
        bullets=bullets,
        tech=tech,
        roles=(),
    )


def _flatten_grouped_employment(entry: ExperienceEntry) -> tuple[ExperienceEntry, ...]:
    return tuple(
        flatten_role(entry, role, include_parent_context=index == 0)
        for index, role in enumerate(entry.roles)
    )


def validate_experience(experience: tuple[ExperienceEntry, ...]) -> None:
    for entry in experience:
        if entry.roles and entry.type is not ExperienceType.EMPLOYMENT:
            raise ValueError(
                f"Only employment entries may contain nested roles: {entry.title!r}"
            )


def flatten_experience(
    experience: tuple[ExperienceEntry, ...],
) -> tuple[ExperienceEntry, ...]:
    validate_experience(experience)
    flattened: list[ExperienceEntry] = []
    for entry in experience:
        if entry.roles:
            flattened.extend(_flatten_grouped_employment(entry))
        else:
            flattened.append(entry)
    return tuple(flattened)


def prepare_content(
    content: ResumeContent, profile: OutputProfile | str
) -> ResumeContent:
    selected_profile = coerce_output_profile(profile)
    validate_experience(content.experience)
    if selected_profile is OutputProfile.GROUPED:
        return content
    return replace(content, experience=flatten_experience(content.experience))
