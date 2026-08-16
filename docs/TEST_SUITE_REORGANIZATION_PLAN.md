# Test Suite Reorganization Plan

## Objective

Split `tests/test_parser.py` into focused test modules without changing application behavior, test coverage, test framework, or the canonical resume-source contract.

The current file covers path resolution, DOCX helpers, source-directory loading, parsing, and rendering. Splitting it by primary production-module responsibility will make failures easier to locate and changes easier to review.

## Scope and constraints

- Continue using the standard-library `unittest` framework and the existing discovery command: `python -m unittest discover -s tests`.
- Preserve every current assertion and warning-behavior check during the move.
- Do not change code under `resume_builder/` as part of this reorganization.
- Keep cross-module tests where the public behavior is inherently integration-oriented; assign them to the module that owns the top-level operation under test.
- Keep the canonical fixture at `source/canon-resume/` read-only. Tests that modify resume content must continue to copy it into a temporary directory first.

## Target test layout

```text
tests/
  helpers.py
  test_cli.py
  test_docx_utils.py
  test_parser.py
  test_renderer.py
  test_sections.py
```

### `tests/helpers.py`

Extract only utilities shared by two or more test modules:

- `PROJECT_ROOT` and `RESUME_SOURCE`
- `copy_resume_source(temp_dir: str) -> Path`
- `read_frontmatter_title(path: Path) -> str`
- `read_section_titles(source: Path) -> dict[str, str]`
- `heading_texts(document) -> list[str]`

Keep helpers small and test-focused. They should not introduce a second implementation of production parsing or rendering logic.

### `tests/test_cli.py`

Test `resume_builder.cli` path-resolution behavior:

- `test_cli_resolves_named_sources_and_relative_outputs_under_their_roots`
- `test_cli_preserves_existing_source_and_absolute_output_paths`

### `tests/test_docx_utils.py`

Test reusable DOCX layout helpers in `resume_builder.docx_utils`:

- `test_entry_heading_uses_a_right_tab_and_non_breaking_date`
- `test_role_entries_preserve_and_render_every_introductory_paragraph`

The latter test covers parsing as setup, but its primary assertion is that `add_role_entry` renders every supplied introductory paragraph. Keep the warning-only parsing case in `test_parser.py`.

### `tests/test_parser.py`

Test parsing from valid and invalid source input:

- `test_role_entry_without_an_introduction_warns_but_still_parses`
- `test_single_file_source_is_rejected`
- `test_missing_source_directory_is_rejected`
- `test_parses_split_resume_source`
- `test_editable_title_is_passed_to_model_and_renderer_without_changing_section_type`

For the editable-title test, assert parser model behavior in this file. Move the rendering-heading assertion into the renderer equivalent if it is retained, so the test does not need to exercise two top-level APIs.

### `tests/test_sections.py`

Test source-directory loading, section metadata, identity, ordering, and missing-section behavior in `resume_builder.sections`:

- `test_loads_section_titles`
- `test_meta_section_order_controls_rendering_order` — retain only the `load_resume_directory` ordering assertion here.
- `test_section_files_require_frontmatter`
- `test_section_files_require_a_title`
- `test_missing_metadata_file_fails_clearly`
- `test_each_missing_required_section_warns_once_and_is_not_rendered` — split into a loading/warning test here and leave rendering assertions in `test_renderer.py` if necessary.
- `test_all_missing_required_sections_warn_and_render_no_section_headings` — split similarly by API responsibility.
- `test_remaining_editable_title_is_preserved_after_an_earlier_omission` — retain loading and parsed-model expectations here only if the model is populated through the section loader; otherwise keep those assertions in `test_parser.py`.
- `test_missing_optional_section_is_silent_and_not_rendered` — retain the `load_resume_directory` assertions here; renderer assertions belong in `test_renderer.py`.
- `test_selected_project_is_loaded_and_rendered_with_its_editable_title` — retain loader and parsed-content expectations here or in `test_parser.py`; rendering-heading assertions belong in `test_renderer.py`.

Use `subTest` for the loop over registered required sections, as the current test does. This keeps one parameterized behavior test rather than creating a brittle test per filename.

### `tests/test_renderer.py`

Test document and Markdown composition through the public renderer APIs:

- `test_canonical_source_builds_a_readable_docx_smoke_test`
- Renderer assertions from `test_meta_section_order_controls_rendering_order`
- Renderer assertions from missing-required-section tests
- Renderer assertions from `test_remaining_editable_title_is_preserved_after_an_earlier_omission`
- Renderer assertions from `test_missing_optional_section_is_silent_and_not_rendered`
- Renderer assertions from `test_selected_project_is_loaded_and_rendered_with_its_editable_title`
- `test_build_markdown_combines_sections_in_order_with_editable_titles`
- Renderer assertion from `test_editable_title_is_passed_to_model_and_renderer_without_changing_section_type`

Name tests after their externally observable behavior rather than their original source file. For example, use `test_missing_required_section_is_not_rendered` for the renderer-specific half of the current combined test.

## Implementation steps

1. **Establish a baseline.** Run the existing test suite and record its test count and result before moving any code.
2. **Create shared helpers.** Add `tests/helpers.py`, moving the existing common constants and helper functions without changing their behavior.
3. **Extract isolated unit tests first.** Move CLI and DOCX utility tests into `test_cli.py` and `test_docx_utils.py`. Update imports to use `tests.helpers` only where needed.
4. **Separate loader and parser coverage.** Move source-contract and loading tests into `test_sections.py`; retain direct parsing behavior in `test_parser.py`.
5. **Separate renderer integration coverage.** Move DOCX and Markdown output assertions to `test_renderer.py`. Where a current test combines several APIs, either:
   - split it into focused loader/parser/renderer tests that share the same temporary-source setup; or
   - retain one integration test in `test_renderer.py` when splitting would obscure the end-to-end contract.
6. **Remove the old mixed test content.** Delete the moved tests from `test_parser.py`; leave that module containing parser-focused tests only.
7. **Review imports and test names.** Remove unused imports, make test class names describe each module’s behavior, and ensure no test relies on execution order or artifacts created by another file.
8. **Validate the refactor.** Run all repository-required checks listed below.

## Validation

Run the project-required validation commands after the reorganization:

```bash
uv run python -m unittest discover -s tests
uv run ruff check .
uv run ruff format --check .
uv run python -m compileall -q resume_builder tests
git diff --check
```

Also compare the number of discovered tests before and after the split. The count should remain the same unless a deliberately combined test is split into multiple independently meaningful tests; if it changes, document why and ensure every prior assertion remains represented.

## Definition of done

- `tests/test_parser.py` contains parser-focused coverage only.
- CLI, DOCX utility, source-loading, and renderer behavior each have focused test modules.
- Shared fixture and document-inspection helpers have one clear home.
- All tests remain independently runnable and use temporary copies before modifying canonical source content.
- The full test suite and all required lint, format, compile, and diff checks pass.
- The reorganization does not change runtime behavior, the source format, or the public API.
