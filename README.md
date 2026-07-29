# Markdown Resume Builder

Build a polished resume DOCX from section-based Markdown files with YAML frontmatter.

## Source structure

The resume source lives in `docs/resume/`:

```text
docs/resume/
  meta.md
  sections/
    summary.md
    core-skills.md
    professional-experience.md
    education.md
```

`meta.md` contains the shared resume metadata:

- `name`
- `title`
- `tagline`
- `contact_lines`

Each section file contains its section content and a required, non-empty `title` frontmatter field. That value controls the visible heading in the generated DOCX. For example, changing `title: Summary` to `title: Professional Profile` changes only the displayed heading; filenames and canonical section definitions still determine section type, ordering, and parsing behavior.

A `selected-project.md` section can also be added when the resume includes a separate selected project. It is explicitly optional and is silently omitted when absent; other missing section files currently fail the build until optional-section handling is completed.

## Usage

Install dependencies:

```bash
uv sync
```

Generate the DOCX using the default source and output paths:

```bash
uv run build-resume
```

Specify a source directory and output path explicitly:

```bash
uv run build-resume docs/resume -o docs/my-resume.docx
```

The previous single-file Markdown format remains supported when an explicit file path is passed. Its canonical Markdown headings continue to identify and label sections, so existing single-file sources render as before.

## Package structure

- `resume_builder/cli.py`: command-line entry point
- `resume_builder/models.py`: resume data models
- `resume_builder/parser.py`: Markdown content parsing
- `resume_builder/sections.py`: section discovery and loading
- `resume_builder/renderer.py`: DOCX generation
- `resume_builder/theme.py`: document styling and layout

## Tests

Run the parser tests with:

```bash
uv run python -m unittest discover -s tests
```
