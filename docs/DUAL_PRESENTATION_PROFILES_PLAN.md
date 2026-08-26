---
createdAt: 2026-08-26
updatedAt: 2026-08-26
status: complete
---

# Dual Presentation Profiles Plan

## Purpose

Keep grouped employment as the canonical professional-history representation while producing an ATS-safe résumé presentation for job applications.

The current grouped Gamesys/Bally's representation is valuable for showing continuous employment, promotion, and acquisition context. However, many ATS and application systems reconstruct career history by looking for repeated, conventional records containing a job title, organisation, location, and dates at the same structural level. The grouped DOCX and Markdown output does not reliably satisfy that assumption.

This plan separates **career-history structure** from **output presentation** rather than reverting the typed experience model.

## Decision

Maintain one canonical typed experience model and support two output profiles:

| Profile | Primary use | Experience presentation |
| --- | --- | --- |
| `ats` | Job applications and automated parsing | Every role is a standalone, conventional employment record |
| `grouped` | Human review, portfolio, and site-oriented output | Continuous employment is shown as a parent entry with nested roles |

The default profile for the command-line builder is `ats`, because the most consequential output is the document uploaded to an application system. The grouped presentation remains available explicitly.

Example commands:

```bash
uv run build-resume canon-resume -o resume-ats.docx
uv run build-resume canon-resume -o resume-grouped.docx --profile grouped
uv run build-resume canon-resume -o resume-ats.md --profile ats
```

The source of truth remains under `source/`. No résumé facts should be duplicated into separate ATS-only source Markdown.

## Implementation status

Implemented on 2026-08-26. The builder now exposes `OutputProfile.ATS` and `OutputProfile.GROUPED`, defaults both direct builders and the CLI to `ats`, flattens grouped roles through a derived profile adapter, and renders profile-specific DOCX and Markdown output. The grouped profile remains available for the existing human-oriented layout.

## Goals

- Preserve grouped employment, promotions, acquisitions, and continuous-tenure context in the canonical model.
- Produce an ATS output in which every employment role has an explicit title, organisation, location, and date range.
- Avoid relying on heading depth, indentation, tabs, visual grouping, or decorative symbols for machine-readable relationships.
- Preserve role-specific summaries, bullets, and technologies.
- Preserve the Gamesys/Bally's acquisition and progression context without creating an incomplete parent job record in ATS output.
- Keep grouped and ATS outputs derived from the same parsed content.
- Keep flat employment, projects, and career breaks working as they do today.
- Make the selected output profile explicit and testable.

## Non-goals

- Reverting the typed `ExperienceEntry` and `ExperienceRole` models.
- Maintaining two independently edited versions of the résumé.
- Guaranteeing compatibility with every proprietary ATS parser.
- Changing résumé wording except where needed to make an output profile machine-legible.
- Introducing the future PKM export or professional-profile JSON schema as part of this change.
- Normalising display date strings into structured dates; that remains part of the future professional-profile projection.
- Redesigning unrelated sections or the overall DOCX theme.

## Current problem and constraints

The current canonical entry is structurally correct for a grouped timeline:

```text
Gamesys → Bally's Interactive | London, UK | 03/2019 – 11/2023

Frontend Tech Lead | Bally's Interactive | 11/2022 – 11/2023
Senior Frontend Engineer | Gamesys / Bally's Interactive | 10/2020 – 11/2022
Frontend Developer | Gamesys | 03/2019 – 09/2020
```

The current DOCX renderer makes the parent and roles visually distinguishable, but the distinction is primarily visual:

- the parent and nested roles use the same Word `Heading 2` style;
- nested roles are identified by left indentation;
- the parent contains no job title in the model;
- the role headings do not repeat the parent location;
- the parent heading uses an arrow-based organisation label;
- the date is positioned with a tab for visual alignment.

These are reasonable human-layout choices but weak assumptions for an extractor that expects independent job records.

The current Markdown exporter also concatenates source sections. Consequently, its grouped output retains `###` role headings and type comments rather than being a profile-specific serialization of the typed model.

## Target architecture

```text
Canonical section Markdown
  → parser
    → typed ResumeContent with grouped ExperienceEntry / ExperienceRole values
      ├─ grouped presentation adapter
      │    → grouped DOCX or Markdown
      └─ ATS presentation adapter
           → flattened experience values
             → ATS DOCX or Markdown
```

The parser and domain model must not know whether the final document is intended for an ATS. Profile-specific behavior belongs between the parsed model and the format renderers.

## Output-profile API

Introduce an explicit profile value, preferably a small `StrEnum` such as:

```python
class OutputProfile(StrEnum):
    ATS = "ats"
    GROUPED = "grouped"
```

The final module location should follow the existing package boundaries. A small profile module is preferable if adding the enum to `models.py` would mix domain data with presentation configuration.

Extend the public builder functions without breaking existing positional theme calls:

```python
def build_doc_from_source(
    source_path: Path,
    theme: ResumeTheme = DEFAULT_THEME,
    *,
    profile: OutputProfile = OutputProfile.ATS,
) -> DocumentType: ...


def build_markdown_from_source(
    source_path: Path,
    *,
    profile: OutputProfile = OutputProfile.ATS,
) -> str: ...
```

The exact type and parameter names may be adjusted to match project style, but profile selection must be explicit, validated, and shared by DOCX and Markdown paths.

The CLI should add:

```text
--profile {ats,grouped}
```

An invalid profile should produce argparse's normal clear command-line error. The default should be `ats`.

## ATS flattening rules

Add a focused adapter or transformation function. Do not make the DOCX renderer inspect `roles` differently in several places.

### Flat entries

- Flat `employment` entries remain one ATS record.
- `project` entries remain one project record with their existing title, organisation, optional location, dates, summaries, bullets, and technologies.
- `career_break` entries remain a distinct timeline item with title, dates, and summaries only.

### Grouped employment

A grouped employment parent must not be emitted as an additional ATS job record because it has no job title. Instead, emit one standalone ATS record for each nested role.

For every nested role:

```text
title | organisation | location | role dates
```

Use the following values:

- `title`: the nested role title;
- `organisation`: the nested role organisation when present; otherwise the parent organisation;
- `location`: the parent location when present;
- `date_right`: the nested role date range;
- `descriptions`, `bullets`, and `tech`: the nested role's own content.

The current Gamesys/Bally's output should therefore contain records equivalent to:

```text
Frontend Tech Lead | Bally's Interactive | London, UK | 11/2022 – 11/2023
Senior Frontend Engineer | Gamesys / Bally's Interactive | London, UK | 10/2020 – 11/2022
Frontend Developer | Gamesys | London, UK | 03/2019 – 09/2020
```

No role should depend on the parent heading or indentation to establish its employer or location.

### Parent context preservation

Parent summaries explain progression and the acquisition. They must not disappear when the parent heading is removed from ATS output.

For the initial implementation:

- prepend the parent summaries to the first emitted role's summaries;
- preserve parent bullets, if any, before the first role's bullets;
- preserve parent technology text, if any, with the first role's technology content without silently dropping it;
- do not repeat the parent context for every role.

The first Gamesys/Bally's ATS role will therefore retain context equivalent to:

```text
Joined Gamesys as a Frontend Developer and progressed to Senior Frontend Engineer and then Frontend Tech Lead, remaining with the business through its 2021 acquisition by Bally's Corporation.
```

The adapter should preserve paragraph boundaries and ordering. It should not try to infer or rewrite organisation aliases from display strings such as `Gamesys → Bally's Interactive`. If a role has no organisation, the parent organisation is the explicit fallback. More structured organisation aliases should be handled by the future professional-profile projection rather than by parsing display punctuation here.

## ATS DOCX presentation

The ATS DOCX renderer should use a conventional, flat employment layout:

- all experience records render at the same structural level;
- grouped roles render with zero left indentation;
- each heading contains title, organisation, location where available, and dates;
- role content follows immediately after its heading;
- no parent-only Gamesys/Bally's heading is emitted;
- no decorative arrow is required to understand the employer relationship;
- dates must remain close to the heading and should not be the only visible content on a separate extracted line.

The existing human layout uses a tab stop to right-align dates. For ATS mode, add a focused heading option/helper that emits one contiguous heading string, for example:

```text
Frontend Tech Lead | Bally's Interactive | London, UK | 11/2022 – 11/2023
```

The grouped profile may retain the current tab-aligned visual heading. Do not change the existing grouped visual hierarchy unless a test demonstrates that the change is necessary.

Use ordinary Word heading styles and native list paragraphs. Avoid introducing tables, text boxes, headers, footers, columns, or positioned elements for ATS content.

## ATS Markdown presentation

The ATS Markdown serializer should be generated from the typed output model rather than returning the raw grouped source section.

For ATS output:

- emit every experience record as a top-level `##` entry;
- use explicit visible heading fields in the order `title | organisation | location | dates` where applicable;
- do not emit nested `###` role headings;
- do not emit the internal `<!-- experience: ... -->` markers unless they are required for another downstream consumer;
- preserve paragraphs, bullets, and `**Tech:**` lines;
- retain normal section ordering and metadata.

The grouped Markdown profile preserves the readable grouped form, including nested role headings, but is serialized from the parsed typed model so it shares validation and content semantics with the DOCX renderer.

## Renderer design

Keep profile handling at the composition boundary:

1. `parse_resume_source()` continues to return grouped typed experience data.
2. A profile adapter prepares the experience entries for the selected profile.
3. DOCX and Markdown renderers consume the prepared entries using shared content helpers.
4. The renderer does not mutate canonical models or source files.

Prefer a small prepared/render model over passing a boolean such as `flatten_grouped_roles` through multiple helper layers. This keeps the grouped domain model intact and makes future profiles easier to add without weakening the model.

Potential internal shape:

```text
Parsed ResumeContent
  → Profile-specific experience view
     → render DOCX
     → render Markdown
```

The adapter may use existing `ExperienceEntry`/`ExperienceRole` values or a small render-only record. It must not duplicate factual content in a second source file.

## CLI and compatibility

Update `resume_builder/cli.py` to:

- accept `--profile`;
- pass the selected profile to either DOCX or Markdown generation;
- default to `ats`;
- retain existing source and output path resolution;
- preserve the current output suffix behavior.

Existing callers that invoke the builder functions directly should continue to work, with the documented default profile applied. Tests that intentionally check grouped behavior should pass `profile=OutputProfile.GROUPED` explicitly after the default changes.

The output filename is not the profile selector. `resume-ats.docx` and `resume-grouped.docx` are recommended names, but the CLI must use the option rather than guessing from a filename.

## Documentation updates

Update the following together with implementation:

### `README.md`

Document:

- the two output profiles;
- the default `ats` profile;
- example commands for both profiles;
- the difference between canonical grouped source and ATS output;
- why ATS output repeats organisation and location per role;
- that the profile affects presentation, not the canonical experience facts.

### `docs/PLAN.md`

Add the dual-profile behavior to the architecture and output contract. Clarify that the typed professional-experience model is presentation-neutral and that output profiles are consumers of that model.

### This plan

When implementation is complete, update the status and implementation notes with the final API and any decisions that differ from this proposal.

Do not modify the future PKM plan's source-of-truth direction. The profile adapter should remain compatible with a future structured professional-profile importer.

## Testing plan

### Profile transformation tests

Add focused tests for the adapter:

1. flat employment remains one record;
2. project remains one record;
3. career break remains one record without bullets or technology output;
4. grouped employment produces one record per nested role;
5. grouped parent title is not emitted as an ATS job;
6. nested role organisation is used when present;
7. parent organisation is the fallback when a role organisation is absent;
8. parent location is copied to each flattened role;
9. role dates remain role-specific;
10. parent summaries, bullets, and technology values are preserved according to the first-role context rule;
11. role order is unchanged;
12. the input `ResumeContent` is not mutated.

### DOCX renderer tests

Keep the existing grouped tests and add explicit profile tests:

- grouped output contains the parent and nested visual hierarchy;
- ATS output contains the three Gamesys/Bally's role headings as standalone records;
- ATS output does not contain the parent-only `Gamesys → Bally's Interactive` heading;
- every flattened role heading contains title, organisation, location, and dates;
- ATS role headings have zero left indentation;
- ATS headings are extracted as one contiguous paragraph where practical;
- role descriptions, bullets, technologies, and acquisition context remain in the expected order;
- flat employment, project, career-break, and unrelated sections do not regress.

Tests should inspect both paragraph text and relevant paragraph formatting. Do not rely only on visual snapshots.

### Markdown renderer tests

Verify that:

- ATS output has top-level headings for all three Gamesys/Bally's roles;
- ATS output contains no nested `###` role headings in Professional Experience;
- ATS output contains no parent-only grouped employment heading;
- ATS output preserves the parent acquisition context;
- grouped output retains nested roles and current readable ordering;
- the two profiles are generated from the same source and include the same role facts.

### CLI tests

Add coverage for:

- defaulting to `ats`;
- selecting `--profile grouped`;
- selecting `--profile ats` explicitly;
- rejecting an unknown profile;
- passing the selected profile for both `.docx` and `.md` outputs.

## Implementation sequence

### Phase 1 — Establish profile abstraction

- Add the output-profile enum/value and defaults.
- Add CLI parsing and pass-through plumbing.
- Add profile-selection tests before changing rendering behavior.

### Phase 2 — Implement ATS experience transformation

- Add the focused grouped-to-flat adapter.
- Preserve parent context using the first-role rule.
- Add transformation tests for all experience types and edge cases.

### Phase 3 — Implement profile-aware DOCX rendering

- Keep the current grouped renderer behavior under `grouped`.
- Add flat ATS rendering with explicit headings, repeated location, and no indentation.
- Add an ATS-safe contiguous heading helper or option.
- Add DOCX extraction and formatting tests.

### Phase 4 — Implement profile-aware Markdown rendering

- Keep grouped output readable and nested.
- Serialize ATS Professional Experience from the flattened model with top-level headings.
- Remove internal type comments from ATS output unless a documented consumer requires them.
- Add Markdown profile tests.

### Phase 5 — Make ATS the documented default

- Update README, `docs/PLAN.md`, and CLI help.
- Update existing tests that relied on implicit grouped output to select `grouped` explicitly.
- Add examples to the documentation.

### Phase 6 — Validate and manually inspect

Run the repository-mandated validation:

```bash
uv run python -m unittest discover -s tests
uv run ruff check .
uv run ruff format --check .
uv run python -m compileall -q resume_builder tests
git diff --check
```

Additionally:

```bash
uv run build-resume canon-resume -o /tmp/resume-ats.docx --profile ats
uv run build-resume canon-resume -o /tmp/resume-grouped.docx --profile grouped
uv run build-resume canon-resume -o /tmp/resume-ats.md --profile ats
uv run build-resume canon-resume -o /tmp/resume-grouped.md --profile grouped
```

Inspect extracted DOCX paragraph text and headings for both profiles. Confirm that the ATS document presents three independent Gamesys/Bally's records and that the grouped document retains the current human-readable hierarchy.

## Acceptance criteria

The implementation is complete when:

- canonical source remains grouped and is not duplicated into ATS-specific source files;
- `parse_resume_source()` still returns the grouped typed model;
- the default builder output is ATS-safe and profile selection is explicit;
- ATS DOCX output contains standalone records for `Frontend Tech Lead`, `Senior Frontend Engineer`, and `Frontend Developer`;
- each ATS role record includes its title, organisation, location, and own dates;
- acquisition/progression context is preserved without an incomplete parent job record;
- ATS output does not rely on `###` headings or indentation;
- grouped output remains available and preserves the current parent/role presentation;
- flat entries, projects, career breaks, section ordering, and editable section titles still work;
- DOCX and Markdown outputs use the same profile semantics;
- tests cover transformation, rendering, serialization, and CLI selection;
- the complete repository validation passes.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| ATS output loses useful parent context | Attach parent context to the first flattened role and test for it explicitly |
| Different format renderers diverge | Use one profile-specific experience view before DOCX/Markdown rendering |
| A future role lacks an organisation | Use explicit parent organisation fallback and add structured aliases in the future professional-profile schema |
| Default-profile change surprises existing callers | Preserve direct-call compatibility and document the new default; use explicit `grouped` in grouped tests and workflows |
| ATS parser still mishandles dates or punctuation | Keep headings contiguous and conventional; manually inspect extracted DOCX text; avoid claiming universal ATS compatibility |
| Canonical content becomes duplicated | Keep flattening as a derived transformation only; never add a second editable résumé source |
| Current uncommitted résumé edits are overwritten | Limit implementation changes to profile code, tests, and documentation; do not reset or rewrite unrelated source changes |

## Future compatibility

The future PKM professional-profile projection should supply structured employment entries, organisation aliases, dates, and role relationships. This dual-profile implementation should consume those typed facts through the same rendering boundary:

```text
professional-profile JSON
  → validated typed model
    → ATS or grouped presentation
```

The ATS flattening rules should therefore remain an output concern. They must not be copied into the PKM data model or used as justification for weakening grouped employment relationships in the canonical professional profile.
