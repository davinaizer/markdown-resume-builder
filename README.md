# Markdown Resume Builder

Build a polished resume DOCX from section-based Markdown files with YAML frontmatter.

## Source structure

Resume sources live under `source/`. The canonical resume is in `source/canon-resume/`:

```text
source/
  canon-resume/
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

A `selected-project.md` section can also be added when the resume includes a separate selected project. It is explicitly optional and is silently omitted when absent. If any expected required section file is missing, the builder prints a warning identifying its path, skips that section without rendering an empty heading, and continues with the remaining sections in canonical order.

## Usage

Install dependencies:

```bash
uv sync
```

Generate `output/resume.docx` from the default `source/canon-resume` source:

```bash
uv run build-resume
```

Specify a named source and output filename. Relative source names resolve under `source/`, and relative output paths resolve under `output/`:

```bash
uv run build-resume canon-resume -o resume-test.docx
```

This writes `output/resume-test.docx`. Absolute output paths are used unchanged. The previous single-file Markdown format remains supported when an existing explicit file path is passed; its canonical Markdown headings continue to identify and label sections, so existing single-file sources render as before.

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
