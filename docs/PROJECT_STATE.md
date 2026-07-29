# Project State

## Updated

2026-07-29

## Current phase

Phase 5 — Cleanup and documentation complete

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
- Legacy single-file Markdown sources remain supported through canonical level-one headings. Original file-oriented parser and renderer names and thin historical entry points remain compatibility shims.
- References to the obsolete `docs/resume-source.md` path are migration history only, not current source or usage guidance.
- Phase 5 removed four unreachable heading-prefix branches from `resume_builder/parser.py`; `clean_md_text()` had already removed those prefixes, so behavior is unchanged.
- No resume source content was changed.
- A final adversarial review found no CLI, parsing, rendering, ordering, omission, title-handling, or legacy-compatibility regressions. It corrected documentation around non-fatal required files, an absent `sections/` directory, retained compatibility paths, and obsolete-path wording.

## Phase 5 validation

Completed successfully:

- `uv run python -m unittest discover -s tests` — 15 tests passed.
- `uv run build-resume` — wrote `output/resume.docx`.
- `uv run build-resume canon-resume -o resume-test.docx` — wrote `output/resume-test.docx`.
- `uv build` — built the source distribution and wheel successfully using root `README.md` package metadata.
- `uv run python -m compileall -q resume_builder tools main.py tests` — passed.
- Project diagnostics — no errors; parser and active package cleanup are clean.
- `git diff --check` — passed.
- Final stale-reference and documentation-consistency scans — passed.

Generated `output/`, `build/`, and `dist/` artifacts were removed after validation.

## Known issues and tooling limitations

- Ruff is not declared or installed in the project environment, so `uv run ruff check .` and `uv run ruff format --check .` could not run (`Failed to spawn: ruff`). No formatting dependency was added solely for Phase 5.
- Editor diagnostics report import-format warnings in the thin historical entry points `main.py` and `tools/build_resume_docx.py`; both compile and remain unchanged for compatibility.

## Recommended next step

Use the completed section-based workflow for resume maintenance. If further engineering work is planned, first decide whether the legacy `tools/`, `main.py`, and file-oriented API shims will remain part of the supported public surface; only then consider a separately versioned compatibility-removal or parser-decomposition change.