# Project State

## Updated
2026-07-29

## Current phase
Phase 1 — Package extraction complete

## Status summary
- The resume generation logic has been extracted into the `resume_builder` package.
- The existing `build-resume` CLI command now points to the new package entry point.
- Compatibility shims remain in `tools/` so legacy imports continue to work.
- The default CLI source path and README were corrected so `uv run build-resume` works again.
- The build command was validated successfully with and without explicit input paths.

## Active goals
1. Restructure the codebase into smaller modules.
2. Split `docs/resume-source.md` into per-section files.
3. Make section titles editable from frontmatter.
4. Ensure missing section files only produce warnings.

## Expected next implementation step
Start Phase 2 by splitting the resume source into per-section Markdown files with editable frontmatter titles.
