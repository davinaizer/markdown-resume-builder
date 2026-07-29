# Project State

## Updated
2026-07-29

## Current phase
Phase 4 — Optional sections complete

## Status summary
- The project README remains at the repository root; governance, planning, and handoff state live under `docs/`.
- The resume generation logic lives in the `resume_builder` package.
- The canonical resume source is split across `source/canon-resume/meta.md` and per-section files in `source/canon-resume/sections/`.
- The CLI defaults to the named `canon-resume` source under `source/` and writes relative output paths under the ignored `output/` directory.
- Single-file Markdown sources remain supported for compatibility.
- Each section file's validated `title` frontmatter is passed through `ResumeContent.section_titles` and controls its visible DOCX heading.
- Canonical section definitions and filenames still determine section type, ordering, and parsing behavior; editable titles are presentation-only.
- The current resume has no Selected Project section; it is explicitly optional and is silently omitted when absent.
- Missing required section files emit a clear path-specific console warning and are skipped; explicitly optional files remain silent when absent.
- Section presence flows explicitly through the content model so omitted sections render no empty heading or placeholder, while remaining sections retain canonical order and editable titles.
- Source-oriented APIs accept either the section directory or a legacy single Markdown file; compatibility wrappers preserve the original API names.
- Legacy single-file sources retain canonical section titles and rendering behavior.
- Phase 4 changes preserve canonical filename-based identity, ordering, and parsing; editable titles remain presentation-only.
- The finalized repository layout keeps `README.md` at the root, governance handoff files under `docs/`, resume sources under `source/`, and generated documents under ignored `output/`.
- All 15 parser, source-loading, CLI path-resolution, compatibility, omission, and rendering tests pass, covering every required omission and both optional-section states.
- Both `uv run build-resume canon-resume -o resume-test.docx` and the no-argument build succeed with output under `output/`; `uv build` also succeeds with package metadata using the root `README.md`.
- The complete diff was reviewed for bugs and planning drift; no generated resume output artifacts are tracked or included in the diff.

## Active goals
1. Continue decomposing section-specific parsing into smaller modules.
2. Complete final cleanup and documentation.

## Expected next implementation step
Start Phase 5 cleanup: remove obsolete monolithic-source assumptions, finish documentation, and verify the final workflow.
