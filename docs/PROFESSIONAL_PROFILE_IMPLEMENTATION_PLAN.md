---
createdAt: 2026-08-17
updatedAt: 2026-08-17
status: proposed
---

# Professional Profile Implementation Plan

## Purpose

Define a cross-project plan for representing professional history consistently across:

- Personal Knowledge Model (PKM);
- Markdown Resume Builder;
- Professional Site.

This plan responds to requirements that do not fit a flat employer/job model, including grouped employment, promotions, acquisitions, projects, career breaks, optional locations, and role-specific achievements and technologies.

## Architectural decision

PKM is the long-term source of truth for professional facts, relationships, and evidence. The resume builder and Professional Site are presentation consumers; they must not independently own duplicated career-history facts.

The integration boundary is a versioned, public **professional profile projection**.

```text
PKM canonical entities and evidence
  → professional-profile projection
    → Resume Builder
      → DOCX and Markdown CV outputs
    → Professional Site
      → public website output
```

The projection is deliberately separate from PKM's internal entity representation. PKM may contain private information, evidence, uncertainty, source links, and Obsidian relationships that should not automatically enter public outputs.

## Ownership boundaries

| Area | PKM | Professional profile projection | Resume Builder | Professional Site |
| --- | --- | --- | --- | --- |
| Professional facts and evidence | Owns | Selects public facts | Consumes | Consumes |
| Organisations, roles, transitions | Owns | Resolves for public timeline | Consumes | Consumes |
| Public entry order and inclusion | Governs | Owns | May apply resume-specific selection rules | May apply site-specific selection rules |
| Reusable public summaries and contributions | Supports/evidences | Exports defaults | May compress for CV | May adapt for web presentation |
| DOCX layout and ATS formatting | No | No | Owns | No |
| Web routes, components, interactions, SEO | No | No | No | Owns |
| Private notes and evidence metadata | Owns | Excludes by default | Does not receive | Does not receive |

Outputs may adapt presentation and compress copy, but must not invent or silently diverge from evidence-backed professional facts.

## Target profile contract

The professional profile must represent timeline entries through a discriminated type rather than making a conventional `company` and `role` mandatory.

```text
ProfessionalProfile
├── version
├── identity
├── summary
├── skills / focus areas
├── experience[]
│   ├── employment
│   │   ├── organisation
│   │   ├── location?
│   │   ├── dates
│   │   ├── summaries[]
│   │   └── roles[]
│   ├── project
│   │   ├── title
│   │   ├── organisation?
│   │   ├── location?
│   │   ├── dates
│   │   ├── summaries[]
│   │   ├── contributions[]
│   │   └── technologies[]
│   └── career_break
│       ├── title
│       ├── dates
│       └── summaries[]
├── contact links
└── resume metadata
```

### Type rules

- `employment` supports an organisation, optional location, optional parent summary, and zero or more roles.
- A grouped employment item represents continuous tenure, including promotions, rebrands, or acquisitions.
- Nested `roles` contain their own title, optional organisation/brand, dates, summaries, contributions, and technologies.
- `project` represents substantial professional work that is not an employer/job relationship.
- `career_break` is a first-class timeline item with title, dates, and optional summary; it does not require an organisation, location, contributions, technologies, or roles.
- Locations are optional and should appear at the timeline-item level unless a child role genuinely needs a distinct location.

### Date rules

Store dates in machine-stable form:

```text
YYYY-MM
```

Use `null` for an ongoing end date. Renderers own presentation:

```text
2025-12 + null      → 12/2025 – Present
2019-03 + 2023-11   → 03/2019 – 11/2023
```

### Example

```json
{
  "type": "employment",
  "id": "gamesys-ballys",
  "organisation": "Gamesys → Bally's Interactive",
  "location": "London, UK",
  "startDate": "2019-03",
  "endDate": "2023-11",
  "summaries": [
    "Joined Gamesys as a Frontend Developer and progressed to Senior Frontend Engineer and then Frontend Tech Lead, remaining with the business through its acquisition by Bally's Corporation."
  ],
  "roles": [
    {
      "id": "gamesys-ballys-tech-lead",
      "title": "Frontend Tech Lead",
      "organisation": "Bally's Interactive",
      "startDate": "2022-11",
      "endDate": "2023-11",
      "summaries": ["Provided technical direction across frontend initiatives."],
      "contributions": ["Defined a frontend code-quality standardisation programme."],
      "technologies": ["React", "TypeScript", "SonarQube"]
    }
  ]
}
```

## Contract format and location

Define `professional-profile` v1 as JSON Schema. It is portable across Python and TypeScript, supports validation, and avoids coupling consumers to PKM's Markdown/YAML and Obsidian-link internals.

Initial PKM layout:

```text
exports/
  professional-profile/
    v1/
      professional-profile.schema.json
      professional-profile.example.json
      README.md
```

The generated interchange artifact should be JSON. YAML may be used for human-authored fixtures where appropriate.

The schema is the contract source. Consumer repositories should generate or validate language-specific types from it where practical rather than manually maintaining duplicate shapes.

## Implementation phases

### Phase 0 — Confirm PKM vocabulary and boundaries

**Owner:** PKM governance and cross-project review.

Review the PKM documents designated as authoritative for entity vocabulary, modelling, entity-file representation, source conversion, and resume generation. In particular, use PKM's entity specification rather than inventing competing entity types in consumer repositories.

Answer:

1. Which PKM entities represent organisations, work periods, roles, projects, technologies, claims, and evidence?
2. How do the existing PKM rules represent acquisitions, rebrands, and organisational continuity?
3. How are public-safe facts separated from internal notes and supporting evidence?
4. Whether PKM already provides an export/projection mechanism.
5. Which output-specific editorial copy may live outside canonical evidence-backed knowledge.

**Deliverable:** a PKM architecture decision record establishing PKM → public projection → consumer ownership.

**Decision gate:** do not redesign the resume parser until the shared target model maps cleanly to PKM's approved entity vocabulary.

### Phase 1 — Define professional-profile v1

**Owner:** PKM, reviewed by the Resume Builder and Professional Site.

Create:

1. `professional-profile.schema.json`;
2. a complete example fixture;
3. a concise contract README describing field meanings, required/optional values, date rules, public-data rules, and versioning.

The example fixture must include:

- Alfred as a `project`;
- Planned Career Break as a `career_break`;
- The Signal Group as flat `employment`;
- Gamesys → Bally's Interactive as grouped `employment` with three roles;
- UNBOX as `employment`.

Keep v1 limited to demonstrated requirements. Do not expose internal evidence, confidence, notes, interview prompts, or private PKM relationships without a specific public consumer need.

**Acceptance criterion:** both consumer projects can load the fixture and render all five timeline entries without special-case Markdown parsing.

### Phase 2 — Validate the contract against both outputs

**Owners:** Resume Builder and Professional Site.

Use the v1 fixture before implementing the PKM exporter.

#### Resume Builder validation

Validate that the fixture supports:

- parent organisation heading and overall tenure;
- parent employment context;
- nested roles, role dates, summaries, contributions, and technologies;
- location displayed once at parent level;
- project and career-break timeline entries;
- preservation of multiple summary paragraphs;
- ATS-readable DOCX ordering and hierarchy.

#### Professional Site validation

Validate that the fixture supports:

- a grouped employment timeline;
- a suitable display of nested roles;
- a distinct career-break presentation;
- project work without implying a startup/founder relationship;
- existing site pages and components without assuming every item has both company and role.

The site must replace its flat conventional-job type with a discriminated union. It must not weaken the current model into a broadly optional object such as `company?: string; role?: string`.

**Deliverable:** a short review listing only genuinely cross-consumer fields missing from v1. Revise the contract once after this review rather than iterating schema changes for local implementation details.

### Phase 3 — Implement the PKM projection exporter

**Owner:** PKM.

Implement a deterministic export pipeline:

```text
PKM entities and evidence
  → public selection and presentation policy
    → validated professional-profile v1 JSON
```

The exporter must:

1. resolve PKM relationships into the public profile representation;
2. validate generated output against the v1 schema;
3. fail on missing required public fields rather than emitting ambiguous records;
4. confirm exported claims meet PKM evidence rules;
5. exclude private/internal content by default;
6. use explicit profile ordering rather than filesystem order;
7. include the schema version in each artifact.

Maintain public inclusion, display grouping, and ordering as an explicit PKM profile configuration. This is a selection/presentation policy over canonical knowledge, not duplicate factual ownership.

**Deliverable:** a reproducible command generating a validated `professional-profile.v1.json` artifact according to PKM's established output conventions.

### Phase 4 — Refactor Markdown Resume Builder

**Owner:** Markdown Resume Builder.

#### 4.1 Add a typed projection importer

Load `professional-profile.v1.json` into validated Python models. DOCX rendering must not consume raw dictionaries or parse heading formatting.

```text
profile JSON
  → validated profile model
    → resume render model
    → DOCX / Markdown outputs
```

#### 4.2 Replace flat experience assumptions

Replace the current flat Professional Experience `EntryBlock` assumption with typed timeline models supporting employment, projects, career breaks, optional locations, grouped employment, nested roles, and structured technologies.

Keep unrelated section models, such as `selected_project`, unchanged unless they are intentionally added to the shared contract.

#### 4.3 Add a transition adapter

During PKM exporter development, retain a temporary adapter from the current local source:

```text
legacy section Markdown → ProfessionalProfile model
PKM projection JSON     → ProfessionalProfile model
```

Both paths must produce the same typed internal model. This permits incremental work without coupling renderers to the temporary source format.

#### 4.4 Add grouped rendering

Render parent employment context and every nested role separately. Preserve the distinction between parent and role summaries. Render location only when present. Provide dedicated styling/layout helpers for nested roles rather than repurposing unrelated heading styles.

#### 4.5 Update tests and documentation

Add coverage for each entry type, grouped-role ordering, multiple summaries, optional location, invalid type/field combinations, and DOCX output hierarchy. Update `README.md`, `docs/PLAN.md`, and the source-contract documentation. Correct the existing editable-title test that assumes a stale literal `title: About` value.

### Phase 5 — Refactor Professional Site

**Owner:** Professional Site.

1. Consume the generated v1 JSON artifact.
2. Generate or validate TypeScript types from the schema.
3. Replace the flat `ExperienceEntry` contract with a discriminated timeline-entry union.
4. Render nested roles only for employment entries.
5. Add fixtures/tests for each entry type.
6. Keep site-only concerns—routes, UI labels, presentation, interactions, SEO, and visual options—outside the shared professional-profile contract.

### Phase 6 — Cut over and remove duplication

After PKM exports a validated profile and both consumers successfully use it:

1. designate PKM as the authoritative location for professional facts;
2. mark local resume experience Markdown as transitional or remove it;
3. remove duplicated professional history from the Professional Site;
4. ensure career fact changes begin in PKM;
5. retain only truly output-specific configuration in consumer repositories;
6. add CI checks that validate the projection, build the resume, and type-check/build the Professional Site against a fixture or generated artifact.

## Immediate next action

Begin with a focused PKM contract-discovery pass:

1. Read PKM's entity specification and resume-generation rules.
2. Map the five existing timeline entries to the approved PKM entity vocabulary and relationships.
3. Draft the complete `professional-profile` v1 fixture.
4. Review the fixture against current resume layout requirements and Professional Site usage.
5. Record the architecture decision defining PKM → projection → consumer ownership.

Do not begin a permanent resume source-format migration until this fixture and its schema are agreed. The current Markdown parser can be retained temporarily behind an adapter while the shared projection is implemented.
