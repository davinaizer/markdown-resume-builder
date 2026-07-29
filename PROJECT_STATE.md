# Project State

## Updated
2026-07-29

## Current phase
Phase 0 — Planning

## Status summary
- The refactor has been specified but not implemented yet.
- No source files have been changed for the architecture split.
- The plan has been documented in `PLAN.md`.

## Active goals
1. Restructure the codebase into smaller modules.
2. Split `docs/resume-source.md` into per-section files.
3. Make section titles editable from frontmatter.
4. Ensure missing section files only produce warnings.

## Expected next implementation step
Start Phase 1 by extracting the current resume generation logic into a dedicated package structure while preserving the existing CLI behavior.
