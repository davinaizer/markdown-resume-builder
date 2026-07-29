from __future__ import annotations

import argparse
from pathlib import Path

from resume_builder.renderer import build_doc_from_markdown
from resume_builder.theme import DEFAULT_THEME


OUT_PATH = Path("docs/my-resume.docx")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a resume DOCX from Markdown.")
    parser.add_argument("input_md", nargs="?", default=str(Path("docs/my-resume-product.md")))
    parser.add_argument("-o", "--output", default=str(OUT_PATH))
    args = parser.parse_args()

    input_md = Path(args.input_md)
    output_docx = Path(args.output)

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    doc = build_doc_from_markdown(input_md, DEFAULT_THEME)
    output_docx.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_docx))
    print(f"Wrote {output_docx}")


if __name__ == "__main__":
    main()
