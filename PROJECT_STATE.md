# Project State

## Updated
2026-07-29

## Current phase
Phase 3 — Editable section titles complete

## Status summary
- The resume generation logic lives in the `resume_builder` package.
- The resume source is split across `docs/resume/meta.md` and per-section files in `docs/resume/sections/`.
- The CLI defaults to the new `docs/resume` source directory.
- Single-file Markdown sources remain supported for compatibility.
- Each section file's validated `title` frontmatter is passed through `ResumeContent.section_titles` and controls its visible DOCX heading.
- Canonical section definitions and filenames still determine section type, ordering, and parsing behavior; editable titles are presentation-only.
- The current resume has no Selected Project section; it is explicitly optional and is silently omitted when absent.
- Other missing section files remain fatal until Phase 4 adds warning-and-continue behavior.
- Source-oriented APIs accept either the section directory or a legacy single Markdown file; compatibility wrappers preserve the original API names.
- Legacy single-file sources retain canonical section titles and rendering behavior.
- Phase 3 changes were reviewed for bugs and planning drift; no Phase 4 missing-section behavior was introduced.
- Ten parser, source-loading, compatibility, and rendering tests pass, including editable-title, legacy-rendering, and content-model constructor compatibility coverage, and the default DOCX build was validated successfully.

## Active goals
1. Continue decomposing section-specific parsing into smaller modules.
2. Ensure missing expected section files only produce warnings.
3. Complete final cleanup and documentation.

## Expected next implementation step
Start Phase 4 by making missing required section files non-fatal with console warnings while keeping explicitly optional sections silent when absent.
