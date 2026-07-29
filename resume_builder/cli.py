from __future__ import annotations

import argparse
from pathlib import Path

from resume_builder.renderer import build_doc_from_source
from resume_builder.theme import DEFAULT_THEME


SOURCE_PATH = Path("docs/resume")
OUT_PATH = Path("docs/my-resume.docx")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a resume DOCX from Markdown.")
    parser.add_argument("input_path", nargs="?", default=str(SOURCE_PATH))
    parser.add_argument("-o", "--output", default=str(OUT_PATH))
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_docx = Path(args.output)

    doc = build_doc_from_source(input_path, DEFAULT_THEME)
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_docx))
    print(f"Wrote {output_docx}")


if __name__ == "__main__":
    main()
