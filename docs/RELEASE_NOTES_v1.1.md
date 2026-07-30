# Release Notes — v1.1.0

## Summary

This release focuses on internal architecture improvements and developer-facing maintainability work while keeping the CLI behavior and generated resume output stable.

## Highlights

- Added an end-to-end DOCX smoke test that exercises parse → render → save → reload for the canonical resume source.
- Centralized canonical section definitions in a shared registry and switched parser/render dispatch to registry-driven lookup.
- Tightened the resume domain model with frozen/slotted dataclasses, immutable content collections, and a typed `SectionKind` identifier.
- Extracted reusable DOCX styling and XML helpers into `resume_builder/docx_utils.py` so `renderer.py` can focus on document composition.
- Added and updated handoff documentation to reflect the completed refactor phases.

## User impact

- No expected CLI breaking changes.
- Generated DOCX output should remain stable for the canonical source.
- Python consumers importing internal modules may need to adjust for the stricter model types introduced in this release.

## Validation

- `uv run python -m unittest discover -s tests`
- `uv run ruff check .`
- `uv run python -m compileall -q resume_builder tests`
- `git diff --check`

## Notes

This release is primarily a foundation release for future feature work. The new smoke test is intended to guard behavior as the codebase continues to evolve.
