# Project Plan

## Goal
Refactor the resume builder into a clearer, more maintainable Python package structure and split the resume source into section-based Markdown files with editable section titles.

This plan follows the project-structure guidance from:
- https://docs.python-guide.org/writing/structure/

## Current scope
- Split the monolithic resume generation logic into smaller modules.
- Split `docs/resume-source.md` into separate files:
  - one file for global metadata
  - one file per resume section
- Make each section title editable through frontmatter.
- Allow missing section files to be skipped with a console warning instead of failing the build.

## Implementation status
- Phases 0–4 are complete.
- Phase 3 added editable rendered section titles while preserving canonical section identity and legacy single-file behavior.
- Phase 4 made missing expected section files non-fatal: required files warn and are skipped, explicitly optional files remain silent when absent, and omitted sections render no heading or placeholder.
- The post-Phase 4 layout follow-up is complete: the canonical source lives at `source/canon-resume/`, generated files resolve under ignored `output/`, the README remains at the repository root, and governance handoff files live under `docs/`.
- Phase 5 is next.

## Desired architecture
A small, explicit package with one responsibility per module.

Suggested layout:

```text
markdown-resume-builder/
  README.md
  pyproject.toml
  docs/
    PLAN.md
    PROJECT_STATE.md
  source/
    canon-resume/
      meta.md
      sections/
        summary.md
        core-skills.md
        professional-experience.md
        selected-project.md   # optional
        education.md
  output/                     # generated files, ignored by Git
  resume_builder/
    __init__.py
    cli.py
    models.py
    parser.py
    sections.py
    renderer.py
    theme.py
```

## Module responsibilities
- `cli.py`: command-line entry point and orchestration.
- `models.py`: dataclasses for resume metadata and section content.
- `parser.py`: Markdown/frontmatter parsing logic.
- `sections.py`: section discovery, file loading, ordering, missing-file warnings.
- `renderer.py`: DOCX generation.
- `theme.py`: styling and layout constants.

## Section file format
Each section file should have its own frontmatter, including at least:
- `title`: editable section heading shown in the generated resume

Optional fields can be added later if needed, such as:
- `order`
- `enabled`

## Behavior requirements
- If an expected section file is missing, the build should continue and print a warning.
- Sections explicitly defined as optional, such as `selected-project.md`, may be absent without a warning.
- If a section file exists, its frontmatter `title` should control the visible section heading.
- The build should preserve the current resume output as closely as possible unless a section file is intentionally changed.

## Implementation phases

### Phase 0 — Planning
- Document the target architecture and implementation state.
- No code changes beyond planning/state files.

### Phase 1 — Package extraction
- Move logic out of the main script into a proper package.
- Keep the CLI working with the same `build-resume` command.

### Phase 2 — Resume source split
- Create a shared metadata file for the section-based resume source.
- Split `docs/resume-source.md` into per-section files (now stored under `source/canon-resume/`).
- Preserve the existing content during the split.

### Phase 3 — Editable section titles
- Read section titles from each section file’s frontmatter.
- Remove hard-coded section title strings from the renderer.

### Phase 4 — Optional sections (complete)
- Make missing expected section files non-fatal.
- Emit a warning and continue rendering the remaining sections.
- Keep explicitly optional sections silent when they are absent.

### Phase 5 — Cleanup and documentation
- Update the README with the new structure and workflow.
- Remove obsolete monolithic source assumptions.
- Verify the output DOCX still builds successfully.

## Notes
- Prefer explicit imports and small functions over a large procedural script.
- Avoid circular dependencies by keeping parsing, models, and rendering separated.
- Keep generated DOCX files as outputs, not as the source of truth.
