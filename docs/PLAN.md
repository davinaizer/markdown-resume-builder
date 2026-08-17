# Project Plan

## Goal

Maintain a clear Python package that builds resumes from canonical section-based Markdown source directories with editable rendered section titles.

This plan follows the project-structure guidance from:
- https://docs.python-guide.org/writing/structure/

## Final status

- Phases 0–6 are complete.
- Resume generation logic lives in the `resume_builder` package.
- The original monolithic `docs/resume-source.md` was migrated into the canonical section-based source at `source/canon-resume/`; it is no longer a current source path.
- The repository root contains `README.md` and the operational `AGENTS.md`; planning and handoff documents live under `docs/`; resume sources live under `source/`; generated DOCX files live under ignored `output/`.
- Editable section titles affect presentation only. `meta.md` controls section ordering; canonical definitions and filenames determine section identity and parsing behavior.
- Missing required section files warn and are skipped. The explicitly optional `selected-project.md` is silently omitted when absent.
- Only section-based source directories are supported.
- Ruff provides the project linting and formatting baseline.

## Final architecture

```text
markdown-resume-builder/
  AGENTS.md
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
        selected-project.md   # optional; absent in canonical source
        education.md
  output/                     # generated files, ignored by Git
  resume_builder/
    __init__.py
    cli.py
    docx_utils.py
    models.py
    parser.py
    registry.py
    sections.py
    renderer.py
    theme.py
  tests/
```

## Module responsibilities

- `cli.py`: command-line parsing, path resolution, and orchestration.
- `models.py`: dataclasses for resume metadata and parsed section content.
- `parser.py`: section-content parsing.
- `registry.py`: canonical section definitions and identities.
- `sections.py`: source loading, ordering, and missing-file warnings.
- `renderer.py`: document composition and output rendering.
- `docx_utils.py`: reusable DOCX styling and layout helpers.
- `theme.py`: styling and layout constants.


## Canonical source contract

A section-based source contains:

- Required `meta.md` with `name`, `title`, `tagline`, and non-empty `contact_lines` frontmatter.
- Normally, a `sections/` directory.
- Required `summary.md`, `core-skills.md`, `professional-experience.md`, and `education.md` section files. In this contract, required means expected and warning-producing when absent, not fatal.
- Explicitly optional `selected-project.md`.

Every present section file requires a non-empty frontmatter `title`. The title controls only the rendered heading. `meta.md` determines order; canonical section definitions and filenames determine identity and section-specific parsing.

Experience and selected-project entries may contain any number of introductory paragraphs. Every paragraph is preserved in rendered output; an entry without an introduction is non-fatal and produces a warning.

Professional Experience is a typed timeline adapter. Each top-level `##` entry must have exactly one following `<!-- experience: employment|project|career_break -->` marker; blank lines before the marker are allowed. Flat employment and projects use `title | organisation [| location] | dates`; career breaks use `title | dates`; grouped employment uses `organisation [| location] | dates` and contains ordered `###` roles using `title [| organisation] | dates`. Parent and role bodies independently preserve paragraphs, bullets, and an optional `**Tech:**` line. Career breaks allow summaries only. The current Markdown grammar is intentionally temporary: a future PKM professional-profile projection will map into the same typed model.

Missing required files produce path-specific warnings and are skipped without an empty heading. If `sections/` itself is absent, each required path produces the same warning. An absent optional file is omitted silently.

## Implementation phases

### Phase 0 — Planning (complete)
- Documented target architecture and implementation state.

### Phase 1 — Package extraction (complete)
- Moved generation logic into the `resume_builder` package.
- Preserved the `build-resume` command.

### Phase 2 — Resume source split (complete)
- Migrated the former `docs/resume-source.md` content into metadata and canonical per-section files, now under `source/canon-resume/`.
- Preserved intended resume content.

### Phase 3 — Editable section titles (complete)
- Added section-file frontmatter titles for rendered headings.
- Preserved canonical filename-based identity and parsing.

### Phase 3b — Section ordering in metadata (complete)
- Added a `sections` list to `source/canon-resume/meta.md` to control ordering.
- Kept the section files content-focused while allowing top-level reordering from a single source of truth.

### Phase 4 — Optional sections (complete)
- Made missing expected section files non-fatal.
- Added warnings for missing required files and silent omission for explicitly optional files.
- Prevented omitted sections from rendering headings or placeholders.

### Phase 5 — Cleanup and documentation (complete)
- Audited code, configuration, tests, examples, and documentation for obsolete monolithic-source and stale layout assumptions.
- Documented the complete source contract, warning behavior, title semantics, CLI path resolution, and generated-output handling in the root `README.md`.
- Completed the validation recorded in `docs/PROJECT_STATE.md`.
- Completed an adversarial final review for behavior changes, inaccurate documentation, stale paths, and unnecessary cleanup churn.
- Removed generated `output/`, `build/`, and `dist/` artifacts.

### Phase 6 — API simplification and development tooling (complete)
- Standardized the application on section-based source directories.
- Removed unsupported entry points, APIs, model defaults, tests, packaging configuration, and documentation.
- Added Ruff as a development dependency and formatted the Python codebase.
- Added a regression test enforcing directory-only sources.

### Phase 7 — Typed Professional Experience timeline (complete)
- Added explicit employment, project, and career-break entries with optional location.
- Added grouped employment with ordered, independently rendered nested roles.
- Retained Markdown as the canonical interim adapter, preserving the boundary for a later PKM professional-profile importer.

## Maintenance guidance

- Treat `source/` Markdown as the source of truth and `output/` DOCX files as disposable build artifacts.
- Add or reorder sections by changing the canonical definitions and all affected parsing, rendering, documentation, and tests together; do not use editable frontmatter titles as identifiers.
- Run Ruff and the full test suite before merging changes.
- Prefer focused changes over broad parser or renderer refactors now that the planned migration is complete.
