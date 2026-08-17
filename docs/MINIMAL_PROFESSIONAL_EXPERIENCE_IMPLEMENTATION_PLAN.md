---
createdAt: 2026-08-17
updatedAt: 2026-08-17
status: complete
---

# Minimal Professional Experience Implementation Plan

## Implementation status

Completed 2026-08-17. The Markdown adapter, typed experience model, nested DOCX rendering, canonical type markers, documentation, and regression tests are implemented. The PKM professional-profile projection remains the future input-adapter migration.

## Purpose

Implement the Professional Experience structure described in [`reports/resume-structure-change-report.md`](reports/resume-structure-change-report.md) with the smallest focused change to the current Markdown Resume Builder.

This plan supports grouped employment, nested roles, optional locations, projects, and career breaks while preserving the existing single-file Markdown source and avoiding a premature migration to the planned PKM-backed professional-profile projection.

## Scope

### In scope

- Explicit Professional Experience entry types: `employment`, `project`, and `career_break`.
- Grouped employment entries with ordered `###` nested roles.
- Separate parent and nested-role summaries, bullets, and technology stacks.
- Optional location at employment/project level.
- Proper DOCX rendering of grouped employment, projects, and career breaks.
- Parser, renderer, documentation, and regression-test updates.

### Out of scope

- Splitting Professional Experience into one source file per entry.
- Replacing canonical Markdown source with PKM-generated JSON.
- Shared schema/type generation with the Professional Site.
- Date normalisation from display strings to machine-readable date values.
- PKM identifiers, evidence references, output profile variants, or privacy classification.
- Refactoring unrelated sections such as Selected Project.

## Source contract

Retain `source/canon-resume/sections/professional-experience.md` as the canonical source file.

Every top-level Professional Experience entry uses a visible `##` heading followed by exactly one required hidden type marker. Blank lines between the heading and marker are allowed:

```md
## **Product Engineer & Co-creator | Independent Product Project | 12/2025 – Present**
<!-- experience: project -->
```

```md
## **Planned Career Break | 11/2024 – 11/2025**
<!-- experience: career_break -->
```

```md
## **Senior Frontend Software Engineer | The Signal Group | London, UK | 12/2023 – 10/2024**
<!-- experience: employment -->
```

```md
## **Gamesys → Bally's Interactive | London, UK | 03/2019 – 11/2023**
<!-- experience: employment -->

Parent summary.

### **Frontend Tech Lead | Bally's Interactive | 11/2022 – 11/2023**

Role summary.

- Role contribution.

**Tech:** React • TypeScript
```

HTML comments retain readable visible Markdown and do not appear in normal Markdown rendering. They also prevent the parser from inferring timeline semantics from missing fields or display wording.

### Heading grammar

The final `|`-separated heading segment is always the display date range.

| Entry shape | Segments before the date range |
| --- | --- |
| `career_break` | `title` |
| Flat `employment` | `title \| organisation [\| location]` |
| `project` | `title \| organisation [\| location]` |
| Grouped `employment` parent | `organisation [\| location]` |
| Nested role (`###`) | `title [\| organisation]` |

The presence of one or more `###` headings identifies a grouped employment parent. Nested roles are valid only under an `employment` parent.

### Body grammar

For both parent entries and nested roles:

- zero or more normal paragraphs are summaries;
- lines beginning `- ` are bullets;
- an optional `**Tech:**` line contains the technology display string;
- summaries may contain any number of paragraphs;
- parent context ends when the first `###` nested role begins;
- a role ends at the next `###`, the next top-level `##`, or end of file.

A `career_break` may contain summaries only. It must not contain roles, bullets, or a technology line.

## Model changes

Retain `EntryBlock` for the unrelated Selected Project section. Add dedicated Professional Experience models in `resume_builder/models.py`:

```python
class ExperienceType(StrEnum):
    EMPLOYMENT = "employment"
    PROJECT = "project"
    CAREER_BREAK = "career_break"


@dataclass(frozen=True, slots=True)
class ExperienceRole:
    title: str
    organisation: str | None
    date_right: str
    descriptions: tuple[str, ...]
    bullets: tuple[str, ...]
    tech: str


@dataclass(frozen=True, slots=True)
class ExperienceEntry:
    type: ExperienceType
    title: str | None
    organisation: str | None
    location: str | None
    date_right: str
    descriptions: tuple[str, ...]
    bullets: tuple[str, ...]
    tech: str
    roles: tuple[ExperienceRole, ...]
```

Change `ResumeContent.experience` and `ParsedSections.experience` from `tuple[EntryBlock, ...]` to `tuple[ExperienceEntry, ...]`.

Dates and technologies deliberately remain display strings in this temporary implementation. The later PKM professional-profile projection will supply structured dates and technology arrays.

## Parser implementation

### 1. Recognise headings and type markers

In `resume_builder/parser.py`:

- add `is_h3()` for `### ` headings;
- add a type-marker parser for `<!-- experience: TYPE -->`;
- require exactly one valid type marker immediately after each top-level `##` heading, ignoring blank lines;
- accept only `employment`, `project`, and `career_break` values.

A missing or invalid marker raises a clear `ValueError` naming the affected entry.

### 2. Parse top-level entry boundaries

Replace the current flat `parse_experience_lines()` loop with logic that:

1. identifies a `##` entry heading;
2. consumes its type marker;
3. parses through to the next `##` heading or end of input;
4. detects and separately parses any `###` child role blocks;
5. returns a typed `ExperienceEntry`.

The parser must not let a `###` role heading become part of its parent summary. This fixes the current issue in which the first nested Gamesys/Bally's role is folded into the parent and later roles are skipped.

### 3. Parse content blocks once

Extract/reuse a content-block parser that reads paragraphs, bullets, and the optional `**Tech:**` line until a supplied boundary predicate.

Use it for:

- flat top-level entries;
- grouped parent context;
- nested role content.

This keeps paragraph preservation consistent with the existing behaviour.

### 4. Parse and validate heading fields

After parsing child roles, determine whether an employment entry is grouped.

- A grouped employment heading supplies `organisation` and optional `location`; `title` is `None`.
- A flat employment/project heading supplies `title`, `organisation`, and optional `location`.
- A career-break heading supplies only `title`.
- A role heading supplies `title` and optional `organisation`.

Validate:

- child roles only occur under `employment`;
- `career_break` has no organisation, location, roles, bullets, or technology line;
- grouped employment has at least one role;
- headings have the allowed field counts for their type/shape;
- role headings include title and date range.

Keep the existing non-fatal warning for a missing introductory paragraph because summaries are optional. A career break without a summary remains valid.

## DOCX rendering

### Rendering dispatch

Update `render_professional_experience_section()` in `resume_builder/renderer.py` to dispatch by entry type and grouped status:

| Entry type | Rendering |
| --- | --- |
| Flat `employment` | Current heading/summary/bullet/tech layout |
| `project` | Current heading/summary/bullet/tech layout |
| `career_break` | Heading plus optional summaries only |
| Grouped `employment` | Parent heading/context followed by each nested role |

### Grouped employment layout

Render the parent organisation/location and overall date range first, then parent summaries. Render every role independently with its role-specific heading, dates, summaries, bullets, and technologies.

The renderer must preserve the distinction between:

- parent context: progression, acquisition, and overall employment narrative;
- role context: scope and contributions specific to that position.

### DOCX utility changes

Add a dedicated `add_nested_role_entry()` helper in `resume_builder/docx_utils.py`.

It may reuse internal role-entry logic, but should provide a clear visual hierarchy:

- nested role heading is subordinate to the parent employment heading;
- nested heading/content receives modest left indentation;
- role summaries, bullets, and technology lines remain visually associated with their role;
- parent location is shown once and is not repeated for every role.

Do not overload Core Skills styles for role hierarchy. Use focused helper parameters and theme values only where required.

## Canonical source update

Update only `source/canon-resume/sections/professional-experience.md` by adding the required type comments:

| Entry | Type |
| --- | --- |
| Product Engineer & Co-creator / Independent Product Project | `project` |
| Planned Career Break | `career_break` |
| Senior Frontend Software Engineer / The Signal Group | `employment` |
| Gamesys → Bally's Interactive | `employment` |
| Co-founder & Technical Lead / UNBOX Learning Experience | `employment` |

Do not rewrite the current experience copy as part of the structural implementation. The report's intended Alfred, career-break, Gamesys/Bally's, and UNBOX copy changes are already present in canonical source.

## Tests

### Parser coverage

Add or update tests in `tests/test_parser.py` for:

1. a project entry without location;
2. flat employment with location;
3. career break with title, dates, and summary;
4. grouped employment with parent summary and three ordered roles;
5. independent parent and role summaries, bullets, and technology values;
6. optional role organisation;
7. preservation of multiple summary paragraphs;
8. missing type marker;
9. unknown type marker;
10. malformed heading field count;
11. a nested role under a project or career break;
12. bullets or technology line under a career break.

### DOCX utility coverage

Update `tests/test_docx_utils.py` to verify:

- nested role heading/content render separately from parent content;
- all introductory paragraphs still render;
- role text appears in the expected document order.

### Renderer coverage

Update `tests/test_renderer.py` to verify that canonical DOCX output contains:

1. Gamesys → Bally's Interactive parent heading and dates;
2. parent acquisition/progression summary;
3. all three nested role headings in source order;
4. role-specific summaries and technologies;
5. the career break heading and summary without empty technology/bullet output;
6. no regression in section heading/order behaviour.

Correct the existing stale editable-title test: it currently replaces the literal `title: About`, while canonical `summary.md` now uses `title: Summary`. Read and replace the current title dynamically, as other tests already do.

## Documentation updates

Update:

- `README.md` with the temporary Professional Experience Markdown grammar;
- `docs/PLAN.md` with the revised Professional Experience contract;
- this plan's status as implementation progresses.

Document that this is an interim Markdown adapter. The target integration described in `PROFESSIONAL_PROFILE_IMPLEMENTATION_PLAN.md` remains a PKM-generated, versioned professional-profile projection.

## Implementation sequence

1. Add parser tests describing the new source contract.
2. Add models and revise parser until parser tests pass.
3. Add nested DOCX helper and renderer dispatch.
4. Add/update renderer and DOCX tests.
5. Add type markers to canonical Professional Experience source.
6. Update README, `docs/PLAN.md`, and the stale title test.
7. Generate a DOCX manually for visual hierarchy review.
8. Run the required validation suite.

## Validation

Before completing implementation, run:

```bash
uv run python -m unittest discover -s tests
uv run ruff check .
uv run ruff format --check .
uv run python -m compileall -q resume_builder tests
git diff --check
```

Additionally generate the canonical resume and inspect the Gamesys/Bally's section visually:

```bash
uv run build-resume canon-resume -o resume-structure-review.docx
```

The generated file remains a disposable `output/` artifact and must not become canonical source.

## Migration boundary

This plan deliberately creates a stable internal typed experience model:

```text
current Professional Experience Markdown
  → temporary Markdown adapter
  → typed experience model
  → DOCX / Markdown renderers
```

When PKM exports `professional-profile.v1.json`, replace only the input adapter:

```text
PKM professional-profile.v1.json
  → projection importer
  → same typed experience model
  → same DOCX / Markdown renderers
```

The renderer must not remain coupled to Markdown heading levels, pipe-delimited fields, or type comments after the future migration.
