---
createdAt: 2026-08-17
updatedAt: 2026-08-17
---

# Resume Structure Change Report

## 1. Support grouped employment with nested roles

### Before

Each Gamesys/Bally's role was represented as an independent top-level experience:

```text
Frontend Tech Lead | Bally's Interactive | 11/2022 – 11/2023
Senior Frontend Engineer | Gamesys / Bally's Interactive | 10/2020 – 11/2022
Frontend Developer | Gamesys | 03/2019 – 09/2020
```

### After

Represent the continuous employment period as a parent experience containing multiple role entries:

```text
Gamesys → Bally's Interactive | London, UK | 03/2019 – 11/2023

  Frontend Tech Lead | Bally's Interactive | 11/2022 – 11/2023
  Senior Frontend Engineer | Gamesys / Bally's Interactive | 10/2020 – 11/2022
  Frontend Developer | Gamesys | 03/2019 – 09/2020
```

The parent should support:

- organisation/group name;
- overall start/end dates;
- location;
- summary/context;
- ordered nested roles.

Nested roles should support:

- title;
- optional organisation/brand;
- start/end dates;
- summary;
- bullets;
- technologies.

This structure makes internal progression and continuous tenure explicit rather than requiring the reader to infer it.

---

## 2. Location belongs to the employment/project level

Preserve location where it adds useful professional context:

```text
The Signal Group | London, UK
Gamesys → Bally's Interactive | London, UK
UNBOX Learning Experience | Brazil
```

Do not require location for every experience.

In particular:

```text
Planned Career Break | 11/2024 – 11/2025
Independent Product Project | 12/2025 – Present
```

can omit location.

For grouped employment, location belongs primarily to the parent rather than being repeated on every nested role.

Suggested parser model:

```text
location?: string
```

rather than making location mandatory.

---

## 3. Career breaks are first-class timeline entries

The career break remains in Professional Experience but should not be forced into an employer/job schema.

```text
Planned Career Break | 11/2024 – 11/2025
```

It requires:

- type/category;
- title;
- dates;
- optional summary;

but does not inherently require:

- company;
- location;
- bullets;
- technologies.

The previous `Self-Employed | Brazil` representation should be removed because neither accurately describes the entire break.

---

## 4. Alfred is an ongoing side project, not a startup/founder role

Change:

```text
Product Engineer & Co-creator | Independent Product Venture
```

to:

```text
Product Engineer & Co-creator | Independent Product Project
```

The summary should establish that Alfred is an independent side project intended to continue alongside professional employment.

Do not currently represent:

```text
Co-founder
Founder
Chaotic Focus
Startup
```

The project remains a substantial Professional Experience entry with its existing engineering bullets and technology stack.

The distinction is intentional:

- **summary:** establishes side-project status;
- **bullets:** demonstrate substantial current product-engineering work.

---

## 5. Employer transitions/acquisitions can be represented explicitly

The Gamesys/Bally's parent represents organisational continuity across an acquisition:

```text
Gamesys → Bally's Interactive
```

Its summary provides the context:

```text
Joined Gamesys as a Frontend Developer and progressed to Senior Frontend
Engineer and then Frontend Tech Lead, remaining with the business through
its 2021 acquisition by Bally's Corporation.
```

The acquisition became legally effective in October 2021; this is consistent with the existing role dates and internal promotion evidence.

The parser should therefore not assume:

```text
different company name = employment break
```

A grouped experience can represent continuous employment across:

- promotions;
- title changes;
- acquisitions;
- rebrands;
- organisational transitions.

---

## 6. Parent and nested summaries have different purposes

For grouped employment:

**Parent summary**

Explains the overall career trajectory and organisational context.

**Nested role summary**

Explains the scope and focus of that specific role.

Example:

```text
Gamesys → Bally's Interactive
  summary: progression + acquisition + overall evolution

  Frontend Tech Lead
    summary: technical direction, DX, quality, onboarding

  Senior Frontend Engineer
    summary: tooling, automation, frontend platform work

  Frontend Developer
    summary: promotions work expanding into architecture/tooling
```

The renderer should support both without flattening them into a single description.

---

## 7. UNBOX now includes client-scale context

The UNBOX summary changes from generic enterprise-client positioning to:

```text
Fortune 500 and global enterprise clients, including Volvo Brasil,
Grupo Boticário, MetLife and HSBC.
```

This is contextual information rather than a separate achievement bullet.

Preserve the named clients because they provide evidence for the scale claim.

---

## 8. Copy-editing principle

Professional Experience copy should follow:

```text
CognitiveOS voice
+ ATS-safe structure
+ explicit industry/technical terminology
+ concrete evidence
+ moderate compression
```

In practical terms:

- preserve React, TypeScript, CI/CD, REST API, SonarQube, GitHub Actions, etc. explicitly;
- prefer actions and outcomes over claims of expertise;
- preserve useful numbers and measurable outcomes;
- remove generic corporate language;
- avoid excessive résumé verbs and self-promotional language;
- retain enough context to explain the problem and contribution;
- do not shorten copy merely for the sake of compression.

The target is **machine-legible, human-written CV copy**.

---

## Resume/parser implications

The experience model should ideally support:

```text
Experience
├── type
│   ├── employment
│   ├── project
│   └── career_break
├── title?
├── organisation?
├── location?
├── start_date
├── end_date
├── summary?
├── bullets[]
├── technologies[]
└── roles[]?
    ├── title
    ├── organisation?
    ├── start_date
    ├── end_date
    ├── summary?
    ├── bullets[]
    └── technologies[]
```

Key invariant:

> A Professional Experience entry is a timeline item, not necessarily a one-to-one mapping between one employer and one job title.

This allows the resume model to represent continuous employment with promotions, side projects, career breaks and organisational transitions without flattening them into artificial standalone jobs.
