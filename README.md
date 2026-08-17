# Markdown Resume Builder

Build a polished resume DOCX or a single combined Markdown file from section-based Markdown files with YAML frontmatter.

## Repository layout

```text
README.md                    # project documentation
docs/                        # planning and handoff documents
source/                      # resume sources
  canon-resume/              # canonical section-based source
    meta.md
    sections/
      summary.md
      core-skills.md
      professional-experience.md
      selected-project.md    # optional; absent in the canonical source
      education.md
output/                      # generated DOCX/Markdown files; ignored by Git
resume_builder/              # Python package
tests/                       # test suite
```

Generated documents are build artifacts, not source files. Keep resume content under `source/`; the CLI creates `output/` when needed, and Git ignores it.

## Section-based sources

A section-based source is a directory containing `meta.md` and normally a `sections/` directory. `meta.md` provides the required shared frontmatter fields:

- `name`
- `title`
- `tagline`
- `contact_lines` (a non-empty list)

The canonical section definitions establish section identity, parsing rules, and order. Here, **required** means expected and warning-producing when absent, not fatal:

| Order | File                         | Requirement | Canonical identity      |
| ----- | ---------------------------- | ----------- | ----------------------- |
| 1     | `summary.md`                 | Required    | Summary                 |
| 2     | `core-skills.md`             | Required    | Core Skills             |
| 3     | `professional-experience.md` | Required    | Professional Experience |
| 4     | `selected-project.md`        | Optional    | Selected Project        |
| 5     | `education.md`               | Required    | Education               |

Each present section file must begin with YAML frontmatter containing a non-empty `title`. This title is presentation-only: it controls the visible heading in the generated DOCX/Markdown output but does not change section identity or parsing.

The `meta.md` frontmatter may also contain a `sections` list that controls the canonical order. For example:

```yaml
sections:
  - summary
  - core_skills
  - professional_experience
  - education
```

You can reorder sections by editing this list. If the list is omitted, the builder falls back to the built-in canonical order. Files outside the canonical list are not resume sections.

If a required section file is missing, the builder writes a path-specific warning to standard error, skips that section, and continues. It does not render an empty heading or placeholder. If the entire `sections/` directory is absent, the same rule applies to each required file. If the explicitly optional `selected-project.md` is absent, the section is omitted silently.

## Professional Experience source format

`sections/professional-experience.md` is an interim Markdown adapter for a typed timeline model. Every `##` entry heading must be followed by exactly one type marker (blank lines allowed before it):

```md
<!-- experience: employment -->
<!-- experience: project -->
<!-- experience: career_break -->
```

The final `|`-separated heading segment is always the display date range. `employment` and `project` entries use `title | organisation [| location] | dates`; a `career_break` uses `title | dates`. Grouped employment uses `organisation [| location] | dates` followed by one or more `###` role headings in the form `title [| organisation] | dates`.

Entries and roles may contain any number of summary paragraphs, bullets, and an optional `**Tech:**` display string. The parent context ends at the first nested role and each role owns its own summary, bullets, and technologies. A career break may have summaries only; it cannot contain roles, bullets, or technologies.

This contract preserves readable Markdown while the type comments remove ambiguity. It is temporary: a future PKM-generated professional-profile projection will import into the same typed experience model.

## Usage

Install dependencies:

```bash
uv sync
```

The primary explicit command is:

```bash
uv run build-resume canon-resume -o resume-test.docx
```

It reads `source/canon-resume/` and writes `output/resume-test.docx`.

To export the full resume as one Markdown file, give the output a `.md` or `.markdown` suffix:

```bash
uv run build-resume canon-resume -o resume.md
```

The no-argument form uses the same canonical source and writes `output/resume.docx`:

```bash
uv run build-resume
```

CLI path resolution follows these rules:

- A relative source name that does not already exist resolves under `source/`. For example, `canon-resume` becomes `source/canon-resume`.
- An existing relative source directory is used as provided.
- An absolute source directory is used as provided.
- Source files are not supported; the input must be a section-based source directory.
- A relative output path always resolves under `output/`.
- An absolute output path is used as provided.

## Package structure

- `resume_builder/cli.py`: command-line parsing, path resolution, and orchestration
- `resume_builder/models.py`: parsed resume data models
- `resume_builder/parser.py`: section-content parsing
- `resume_builder/sections.py`: canonical section definitions, discovery, loading, ordering, and missing-file warnings
- `resume_builder/renderer.py`: DOCX generation
- `resume_builder/theme.py`: document styling and layout

## Tests and packaging

Run the full test suite:

```bash
uv run python -m unittest discover -s tests
```

Run lint and formatting checks:

```bash
uv run ruff check .
uv run ruff format --check .
```

Apply Ruff formatting with `uv run ruff format .`.

Build the distributable package:

```bash
uv build
```
