from __future__ import annotations

import argparse
from pathlib import Path

from resume_builder.renderer import build_doc_from_source
from resume_builder.theme import DEFAULT_THEME

SOURCE_ROOT = Path("source")
DEFAULT_SOURCE = Path("canon-resume")
OUTPUT_ROOT = Path("output")
DEFAULT_OUTPUT = Path("resume.docx")


def resolve_source_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute() or path.exists():
        return path
    return SOURCE_ROOT / path


def resolve_output_path(value: str | Path) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return OUTPUT_ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a resume DOCX from Markdown.")
    parser.add_argument("input_path", nargs="?", default=str(DEFAULT_SOURCE))
    parser.add_argument("-o", "--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    input_path = resolve_source_path(args.input_path)
    output_docx = resolve_output_path(args.output)

    doc = build_doc_from_source(input_path, DEFAULT_THEME)
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_docx))
    print(f"Wrote {output_docx}")


if __name__ == "__main__":
    main()
