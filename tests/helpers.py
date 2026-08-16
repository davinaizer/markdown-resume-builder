from __future__ import annotations

import shutil
from pathlib import Path

import frontmatter
from frontmatter.default_handlers import YAMLHandler

from resume_builder.sections import SECTION_DEFINITIONS

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESUME_SOURCE = PROJECT_ROOT / "source" / "canon-resume"


def read_frontmatter_title(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    handler = YAMLHandler()
    if not handler.detect(text):
        raise AssertionError(f"Missing YAML front matter in {path}")
    post = frontmatter.loads(text, handler=handler)
    title = post.metadata.get("title")
    if not isinstance(title, str):
        raise TypeError(f"Missing title front matter in {path}")
    return title


def read_section_titles(source: Path) -> dict[str, str]:
    titles: dict[str, str] = {}
    for definition in SECTION_DEFINITIONS:
        section_path = source / "sections" / definition.filename
        if section_path.is_file():
            titles[definition.kind] = read_frontmatter_title(section_path)
    return titles


def copy_resume_source(temp_dir: str) -> Path:
    source = Path(temp_dir) / "resume"
    shutil.copytree(RESUME_SOURCE, source)
    return source


def heading_texts(document) -> list[str]:
    return [
        paragraph.text
        for paragraph in document.paragraphs
        if getattr(paragraph.style, "name", None) == "Heading 1"
    ]
