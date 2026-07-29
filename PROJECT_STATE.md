# Project State

## Updated
2026-07-29

## Current phase
Phase 2 — Resume source split complete

## Status summary
- The resume generation logic lives in the `resume_builder` package.
- The resume source is split across `docs/resume/meta.md` and per-section files in `docs/resume/sections/`.
- The CLI defaults to the new `docs/resume` source directory.
- Single-file Markdown sources remain supported for compatibility.
- Section files include validated `title` frontmatter, retained by the loader in preparation for editable rendered titles.
- The current resume has no Selected Project section; it is explicitly optional and is silently omitted when absent.
- Other missing section files remain fatal until Phase 4 adds warning-and-continue behavior.
- Source-oriented APIs accept either the section directory or a legacy single Markdown file; compatibility wrappers preserve the original API names.
- Phase 2 changes were reviewed for bugs and planning drift.
- Nine parser, source-loading, compatibility, and rendering tests pass, and the default DOCX build was validated successfully.

## Active goals
1. Continue decomposing section-specific parsing into smaller modules.
2. Make section titles editable from frontmatter.
3. Ensure missing expected section files only produce warnings.
4. Complete final cleanup and documentation.

## Expected next implementation step
Start Phase 3 by reading each section's `title` frontmatter and removing hard-coded section titles from the renderer.
