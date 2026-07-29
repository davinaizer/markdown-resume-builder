# Project Plan

## Goal

Refactor the resume builder into a clear, maintainable Python package and use section-based Markdown sources with editable rendered section titles while preserving legacy single-file Markdown compatibility.

This plan follows the project-structure guidance from:
- https://docs.python-guide.org/writing/structure/

## Final status

- Phases 0–5 are complete.
- Resume generation logic lives in the `resume_builder` package.
- The original monolithic `docs/resume-source.md` was migrated into the canonical section-based source at `source/canon-resume/`; it is no longer a current source path.
- The repository root contains `README.md`; governance and handoff documents live under `docs/`; resume sources live under `source/`; generated DOCX files live under ignored `output/`.
- Editable section titles affect presentation only. Canonical definitions and filenames determine section identity, ordering, and parsing behavior.
- Missing required section files warn and are skipped. The explicitly optional `selected-project.md` is silently omitted when absent.
- Existing single-file Markdown sources and compatibility entry points remain supported.

## Final architecture

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
        selected-project.md   # optional; absent in canonical source
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
  tests/
  tools/                      # legacy compatibility modules
  main.py                     # legacy compatibility entry point
```

## Module responsibilities

- `cli.py`: command-line parsing, path resolution, and orchestration.
- `models.py`: dataclasses for resume metadata and parsed section content.
- `parser.py`: section-content parsing and legacy single-file Markdown parsing.
- `sections.py`: canonical section definitions, file loading, ordering, and missing-file warnings.
- `renderer.py`: DOCX generation.
- `theme.py`: styling and layout constants.

Thin historical entry points and original file-oriented parser and renderer function names remain as compatibility shims. They delegate to the source-oriented package implementation and are intentionally retained to avoid breaking existing callers.

## Canonical source contract

A section-based source contains:

- Required `meta.md` with `name`, `title`, `tagline`, and non-empty `contact_lines` frontmatter.
- Normally, a `sections/` directory.
- Required `summary.md`, `core-skills.md`, `professional-experience.md`, and `education.md` section files. In this contract, required means expected and warning-producing when absent, not fatal.
- Explicitly optional `selected-project.md`.

Every present section file requires a non-empty frontmatter `title`. The title controls only the rendered heading. Canonical section definitions and filenames determine identity, order, and section-specific parsing.

Missing required files produce path-specific warnings and are skipped without an empty heading. If `sections/` itself is absent, each required path produces the same warning. An absent optional file is omitted silently.

## Implementation phases

### Phase 0 — Planning (complete)
- Documented target architecture and implementation state.

### Phase 1 — Package extraction (complete)
- Moved generation logic into the `resume_builder` package.
- Preserved the `build-resume` command and compatibility entry points.

### Phase 2 — Resume source split (complete)
- Migrated the former `docs/resume-source.md` content into metadata and canonical per-section files, now under `source/canon-resume/`.
- Preserved intended resume content.

### Phase 3 — Editable section titles (complete)
- Added section-file frontmatter titles for rendered headings.
- Preserved canonical filename-based identity, ordering, parsing, and legacy single-file behavior.

### Phase 4 — Optional sections (complete)
- Made missing expected section files non-fatal.
- Added warnings for missing required files and silent omission for explicitly optional files.
- Prevented omitted sections from rendering headings or placeholders.

### Phase 5 — Cleanup and documentation (complete)
- Audited code, configuration, tests, examples, and documentation for obsolete monolithic-source and stale layout assumptions.
- Documented the complete source contract, warning behavior, title semantics, CLI path resolution, legacy compatibility, and generated-output handling in the root `README.md`.
- Reviewed compatibility wrappers and retained those needed to preserve package and CLI compatibility.
- Completed the validation recorded in `docs/PROJECT_STATE.md`.
- Completed an adversarial final review for behavior changes, compatibility regressions, inaccurate documentation, stale paths, and unnecessary cleanup churn.
- Removed generated `output/`, `build/`, and `dist/` artifacts.

## Maintenance guidance

- Treat `source/` Markdown as the source of truth and `output/` DOCX files as disposable build artifacts.
- Add or reorder sections by changing the canonical definitions and all affected parsing, rendering, documentation, and tests together; do not use editable frontmatter titles as identifiers.
- Preserve legacy single-file support unless a future version intentionally introduces and documents a breaking change.
- Prefer focused changes over broad parser or renderer refactors now that the planned migration is complete.
