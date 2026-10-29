# Profile format

A profile is a folder the user keeps outside the plugin, e.g. `~/job-hunt/`. It holds two files:

| File | What it is | Who writes it |
| --- | --- | --- |
| `resume.tex` | The master resume in LaTeX. The starting point for every tailored version. | The user, or the skill converting their PDF or Word resume once ([convert.md](convert.md)), which the user confirms |
| `facts.md` | Every confirmed fact the skill may use, plus a "Never claim" list. The source of truth. | The user (the skill may help draft it, the user confirms it) |

`resume.tex` is how the facts are presented. `facts.md` is what is true. When they disagree,
`facts.md` wins and the mismatch goes in the report.

`facts.md` may hold more than the resume does (extra bullets, extra skills). Those are true and
can be pulled into a tailored version when a job asks for them.

## `facts.md` sections

### About
One line each: location, citizenship, work authorization (where the user can work without a
visa), time zone, remote/relocation, spoken languages with levels. These drive the knockout check.

### Experience
One block per role, newest first:

```markdown
### [BL] Brightleaf Labs: Frontend Developer
- **Title set by:** employer (never change)
- **Dates:** Mar 2024 – Present
- **Location:** Nairobi, Kenya (hybrid)
- **Facts:**
  - BL-1: Built and maintained the customer dashboard of a payments web app in React and TypeScript.
```

- **`[BL]`** is a short code for the role. Each fact gets an ID (`BL-1`, `BL-2`…). The report
  cites these IDs for every change, so each claim on the resume can be traced to its fact.
- **Title set by** is `employer` or `user`.
  - `employer`: the title is copied exactly. Never reworded, never "improved".
  - `user` (own company, self-employment, freelance): list the allowed alternatives, and
    optionally the ones that are not allowed. Only allowed alternatives may be used.
- **Facts** are written the way the user is comfortable seeing them. Numbers keep their exact
  wording: "about 15", "an estimated 20–30%", "about 1,200". A tailored resume may not round,
  narrow or strengthen them.
- Facts that limit a claim belong here too (e.g. "The codebase was JavaScript"). They stop the
  skill from over-reaching.

### Projects
Same as Experience without "Title set by". Use the same ID style (`SP-1`).

### Education
One fact per line: school, degree, dates, location, honours or GPA exactly as awarded.

### Skills
A table of skill, how it was used, and the fact IDs that prove it:

```markdown
| Skill | How it was used | Evidence |
| --- | --- | --- |
| TypeScript | Professional since Mar 2024; freelance since Jan 2023 | BL-1, FR-4 |
```

"How it was used" separates professional use from side projects and coursework, so years of
experience aren't overstated. A skill with no evidence ID is allowed (e.g. Git) but should be
treated as a supporting skill, not a headline claim.

### Never claim
Things the user has **not** done or does not want claimed, one per line. Include near-misses a
job posting might tempt the skill into: tools the user hasn't used, a stronger verb ("led" when
they "helped"), a seniority level, a language level, a rounded number. This list beats anything
the job description asks for.

## How the skill uses the profile

- **May:** reword a fact, reorder facts, cut facts, move a fact to another section, pull in a
  fact that isn't on the master resume, use an allowed alternative for a `user` title.
- **May not:** add a skill, tool, number, title, date, responsibility or result that isn't in
  `facts.md`; strengthen a verb or a number; change an `employer` title; use anything on the
  "Never claim" list.
- If a job requires something the profile doesn't support, it is reported as a **gap**, never
  added.
- If `facts.md` is missing or doesn't cover something on the resume, ask the user. Don't guess.
