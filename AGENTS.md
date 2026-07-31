# Repository Instructions

## Authority

- `docs/PLAN.md` is the source of truth for architecture, source format, and maintenance.
- This file only adds operational and résumé-writing guidance.
- If this file conflicts with the plan, follow the plan.

## Repository Contract

- Edit canonical résumé content only under `source/`; treat `output/` as disposable.
- Support section-based source directories only.
- Preserve canonical section identity by filename and registry definition.
- Treat section frontmatter titles as presentation text, never as identifiers.
- Use `meta.md` to add or reorder registered sections.
- Update parsing, rendering, documentation, and tests together when changing the section contract.
- Keep changes focused; preserve existing package boundaries unless a change clearly reduces risk or complexity.
- Use Conventional Commits v1.0.0 for every commit, with a lowercase imperative subject.

## Validation

Before completing code changes, run:

```bash
uv run python -m unittest discover -s tests
uv run ruff check .
uv run ruff format --check .
uv run python -m compileall -q resume_builder tests
git diff --check
```

## Résumé Writing

- Write in the candidate's natural voice: thoughtful, matter-of-fact, collaborative, technically confident, and understated.
- Keep every claim evidence-based and defensible. Qualify or remove uncertain claims; never invent impact or inflate metrics.
- Explain why work mattered before implementation detail.
- Use role introductions for context and bullets for concise evidence. Preserve any number of introductory paragraphs.
- Emphasise recurring problems solved, ways of working, and growth. Technology supports that narrative; it is not the narrative.
- Include only technologies that materially supported the work.
- Prefer plain verbs such as `built`, `improved`, `simplified`, `supported`, and `collaborated`.
- Use ownership language such as `led`, `drove`, `architected`, or `owned` only when directly supported.
- Avoid hype, keyword stuffing, buzzwords, generic marketing language, and unnecessary adjectives.
- Remove content that does not help the reader understand what kind of engineer the candidate is.
