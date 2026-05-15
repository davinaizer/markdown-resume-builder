# Markdown Resume Builder

This project builds a polished resume DOCX from a Markdown source file.

The current workflow is:

- edit [docs/my-resume.md](docs/my-resume.md)
- run the generator script with `uv`
- open or upload the resulting [docs/my-resume.docx](docs/my-resume.docx) in Google Docs

The script preserves the resume's current structure and styling, including:

- title block
- summary
- core skills
- professional experience
- selected project
- education

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
