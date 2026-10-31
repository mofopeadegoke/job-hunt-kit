# ATS rulebook

From the parsing research: the same resume parsed after one change at a time, by `pdftotext`,
OpenResume (a simple rule-based parser) and Affinda (a commercial machine-learning parser with
recruiter search). "Checked by" says whether a script decides the rule or you do.

## Important: what recruiters see and search

### R8 The latest job title decides the role and search results
- Evidence: Affinda assigned the most recent job title, word for word, as the candidate's role.
  A headline under the name changed nothing. A "frontend engineer" search found only a title
  containing that exact phrase ("Founder & Frontend Engineer"), not "Software Developer
  (Frontend)" or "Software Engineer (Frontend)"; those were found by "frontend" alone.
  "Developer" and "engineer" were sometimes treated as equal; a specialty was never inferred.
- Rule: the job's title phrase should appear as a contiguous phrase in the latest job title.
- Limit: only titles the user controls (own company, self-employment, freelance) may change, and
  only to an alternative listed in `facts.md`. Employer titles are reported, never changed.
- Checked by: you (step 4).

### R9 Key evidence goes in Experience, not only Projects
- Evidence: Affinda never showed a Projects section. A product moved from Projects to Experience
  appeared. Projects sometimes leaked into Experience as fake jobs.
- Rule: ongoing real work (own product, freelance) belongs in Experience. Skills used only in
  projects also go in Technical Skills (and the Summary if central to the job).
- Checked by: you (step 5).

### R10 Stack the Education block
- Evidence: Affinda extracted the GPA only when school, degree, location/date and GPA were each on
  their own line. Right-aligned (`\hfill`) lines lost it.
- Checked by: `check_layout.py` (no `\hfill` or tables in Education).

## Safe habits: break simple parsers, harmless for commercial ones

| Rule | What broke without it (OpenResume) | Checked by |
| --- | --- | --- |
| R1 Standard section headings (Summary, Experience, Education, Skills, Projects…) | Creative headings lost every section | `check_layout.py` |
| R2 Single column, no tables | Two columns lost Education; a skills table lost its categories | `check_layout.py` |
| R3 `\quad` around separators on contact lines | Email glued to phone (`9642·name@gmail.com`) | `check_layout.py` |
| R4 Visible space between entries (`\vspace{6pt}`, more than 1.4x the line gap) | 1 of 5 jobs found | `check_layout.py` |
| R5 One page, or no heading at the top of page 2 | Achievements merged into Education; "GPA 0.5" read from "Top 0.5%" | `check_layout.py --pdf` |
| R6 Hyphenation off | Words split across lines ("Mark-" / "down") | `check_layout.py` |
| R7 No icons or images | Icons became junk letters in the text | `check_layout.py` |

## What parsers infer

- Content can create false fields. "English/Turkish localization" was listed as spoken languages.
  When a bullet names languages, frameworks or places in another sense, read the extracted text
  for what a parser might wrongly infer, and mention the risk in the report.
- Spelling variants matter in search: a resume was found by "front" but not "frontend". Use the
  posting's spelling for the same thing ("Front-end" vs "Frontend", "Postgres" vs "PostgreSQL").

## Leave alone

OpenResume's own limits are parser problems, not resume problems: US-only location
(`City, ST`) and phone formats, one link field. Leave real non-US locations and phone numbers
as they are.
