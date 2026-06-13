# Markdown Resume Builder

This project builds a polished resume DOCX from a Markdown source file with YAML front matter.

The current workflow is:

- edit [docs/my-resume.md](docs/my-resume.md)
- run the generator script with `uv`
- open or upload the resulting [docs/my-resume.docx](docs/my-resume.docx) in Google Docs

The source file uses:

- YAML front matter for metadata and contact lines
- Markdown body content for the resume sections

The script preserves the resume's current structure and styling, including:

- title block
- summary
- core skills
- professional experience
- selected project
- education

Styling is centralized in [tools/resume_theme.py](tools/resume_theme.py). Update that file to adjust the font family, colors, font sizes, spacing, and page layout values used by the generator.

The front matter currently expects:

- `name`
- `title`
- `tagline`
- `contact_lines`

## Usage

Install dependencies through `uv` if needed:

```bash
uv sync
```

Generate the DOCX from the Markdown source:

```bash
uv run build-resume docs/my-resume.md -o docs/my-resume.docx
```

You can also output to a different file:

```bash
uv run build-resume docs/my-resume.md -o /path/to/resume.docx
```

## Files

- [docs/my-resume.md](docs/my-resume.md): source resume content
- [docs/my-resume.docx](docs/my-resume.docx): generated Word document
- [tools/build_resume_docx.py](tools/build_resume_docx.py): Markdown-to-DOCX generator
- [tools/resume_theme.py](tools/resume_theme.py): default styling/theme values
