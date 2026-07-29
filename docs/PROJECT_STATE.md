# Project State

## Updated

2026-07-29

## Current phase

Phase 6 — API simplification and development tooling complete

## Status summary

- All planned phases are complete.
- `README.md` remains at the repository root; governance, planning, and handoff documents live under `docs/`.
- Resume sources live under `source/`, with the canonical source split across `source/canon-resume/meta.md` and `source/canon-resume/sections/`.
- Generated DOCX files resolve under ignored `output/` and are treated as disposable build artifacts.
- The CLI defaults to `source/canon-resume/`; `uv run build-resume canon-resume -o resume-test.docx` is the primary explicit example and writes `output/resume-test.docx`.
- Relative source names resolve under `source/` unless the supplied path already exists. Relative output paths resolve under `output/`. Absolute source and output paths are preserved.
- Required section files are `summary.md`, `core-skills.md`, `professional-experience.md`, and `education.md`. Here, required means expected and warning-producing when absent, not fatal; missing files are skipped without headings or placeholders.
- `selected-project.md` is explicitly optional and is silently omitted when absent.
- Every present section file requires a non-empty frontmatter `title`; that value controls only the rendered heading.
- Canonical section definitions and filenames determine section identity, ordering, and parsing behavior. Editable titles do not override them.
- Resume inputs must be section-based source directories; file inputs raise `NotADirectoryError`.
- Ruff is installed as a development dependency for linting and formatting.
- Phase 5 removed four unreachable heading-prefix branches from `resume_builder/parser.py`; `clean_md_text()` had already removed those prefixes, so behavior is unchanged.
- No resume source content was changed.
- Unsupported source paths, APIs, entry points, model defaults, tests, packaging references, and documentation have been removed.

## Final validation

Completed successfully:

- `uv run python -m unittest discover -s tests` — 15 tests passed.
- `uv run build-resume` — wrote `output/resume.docx`.
- `uv run build-resume canon-resume -o resume-test.docx` — wrote `output/resume-test.docx`.
- `uv build` — built the source distribution and wheel successfully using root `README.md` package metadata.
- `uv run ruff check .` — passed.
- `uv run ruff format --check .` — 16 files already formatted.
- `uv run python -m compileall -q resume_builder tests` — passed.
- Project diagnostics — no errors or warnings.
- `git diff --check` — passed.
- Final stale-reference and documentation-consistency scans — passed.

Generated `output/`, `build/`, and `dist/` artifacts were removed after validation.

## Known issues

- None currently known.

## Recommended next step

Use the section-based workflow for resume maintenance and run the documented tests and Ruff checks for future changes.