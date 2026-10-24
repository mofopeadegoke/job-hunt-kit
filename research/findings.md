# Hypotheses
- H1: Two-column layouts get read in the wrong order
- H2: Contact details in the page header or footer get lost
- H3: Icons next to email/phone break their extraction
- H4: Unusual section names ("Where I've worked") get misread
- H5: Skills laid out in a table get scrambled
- H6: Without \pdfgentounicode, some letters ("fi", "fl") disappear from words
- H7: Date formats ("Jun 2025 – Present" vs "06/2025") parse differently

#Findings after pdf resumes are turned into raw text format
- A: Strange characters exists but vital information is preserved. Sections appear in the right order as well. 
- B: Strnage characters also exists and order of information is jumbled up. experiences mix with skills. vital information is lost. 
- C: Strange character exist but vital information is preserved. Sections appear in the right order as well. 
- D: Fewer strange characters but vital information is preserved. Sections appear in the right order as well.
- E: Strange characters exists but vital information is preserved. Sections appear in the right order as well.
- F: Strange characters exists but vital information is preserved. Sections appear in the right order as well. Skils are broken down to different lines making it easier to read as opposed to skills being written in one long line
- G: Strange characters exists but vital information is preserved. Sections appear in the right order as well.
- H: Strange characters exists but vital information is preserved. Sections appear in the right order as well.

#Predictions for K,L,M,N resumes
- K: Email and links fixed. Phone still loses “+90”
- L: Jobs split correctly. But Education now starts page 2, so expect Education to break
- N: The fake education entry and the “0.5” CGPA disappear
- M: Close to a perfect score, except location and “+90”

#Findings after testing with Open resume's parser
# ATS parsing research: findings
 
Tested 12 versions of the same resume (same content, one change each) with:
- `pdftotext` (raw text extraction)
- OpenResume's resume parser (rule-based, single-column, English, US-oriented)
Scored against `answer-sheet.md`. Raw scores are in `results.csv`.
 
> Scope: all parser results are from **one** rule-based parser. Rules marked "OpenResume only"
> still need a second parser before they're treated as general.
 
## Headline result
 
The original resume lost its email, phone, links and all job boundaries in the parser,
even though its raw text was perfect. Three small layout fixes (version M) took it from
**1/5 jobs and a broken email** to **5/5 jobs, 5/5 dates, correct email and education**,
without changing a single word of content.
 
| Field | A-baseline | M-fixed-baseline |
| --- | --- | --- |
| Name | ✅ | ✅ |
| Email | ❌ (`0000·name@example.com`) | ✅ |
| Phone | ❌ | ⚠️ missing `+90` (parser limit) |
| Location | ❌ | ❌ (parser limit) |
| Links | 0/3 | 1/3 (parser limit) |
| Jobs | 1/5 | 5/5 |
| Dates | 1/5 | 5/5 |
| Education | 1/1 (with achievements mixed in) | 1/1 |
| Skills | 27/27 | 27/27 |
 
## Hypotheses
 
| # | Hypothesis | Result | Evidence |
| --- | --- | --- | --- |
| H1 | Two-column layouts are read in the wrong order | ✅ Confirmed | B lost education (0/1); raw text interleaves sidebar and job lines |
| H2 | Contact details in the page header get lost | ❓ Untested on a fixed baseline | Raw text keeps header text; baseline contact was already broken |
| H3 | Icons break contact extraction | ⚠️ Mixed | Raw text: icons become junk letters (`m`, `H`, `B`, `Ï`, `Z`). Parser: icons added spacing, which helped |
| H4 | Unusual section names get misread | ✅ Confirmed (largest effect) | E: 0/5 jobs, 0/1 education, 0/27 skills |
| H5 | Skills in a table get scrambled | ⚠️ Partly | F kept 27/27 skills but lost the categories |
| H6 | Without `\pdfgentounicode`, letters go missing | ❌ Rejected (this setup) | G's raw text identical to A |
| H7 | Date formats parse differently | ❓ Untested on a fixed baseline | Experience was already broken in round 1 |
 
## Rules (for `ats-optimize`)
 
### R1: Use standard section headings
- Evidence: E lost every section. The parser identifies a section's type by keywords
  (experience, education, skills, projects).
- Confidence: high
- Skill should: rename creative headings to standard ones.
### R2: Use a single column
- Evidence: B lost education; raw text mixes columns line by line.
- Confidence: high (both tools)
- Skill should: flag multi-column layouts and offer a single-column version.
### R3: Give each contact item clear space (or its own line)
- Evidence: separators closer than one character width are glued with no space,
  producing `0000·name@example.com`. K (wide gaps) fixed the email.
- Confidence: high (OpenResume only)
- Skill should: check spacing around separators in the contact line.
### R4: Leave visible space between jobs and projects
- Evidence: a new entry is detected only when the line gap is > 1.4x the normal gap.
  A (no extra gap) 1/5 jobs; L and M (6pt gap) 5/5 jobs.
- Confidence: high (OpenResume only)
- Skill should: add space between entries.
### R5: Don't start a page with a section heading; prefer one page
- Evidence: the first line of page 2 is glued onto the last line of page 1, so a heading
  there isn't recognized. A: achievements merged into education (GPA "0.5" taken from
  "Top 0.5%"). L: education lost when it moved to the top of page 2. M (one page): fixed.
- Confidence: high (OpenResume only)
- Skill should: keep tailored resumes to one page; if two, keep headings off page tops.
### R6: Don't hyphenate across lines
- Evidence: raw text split "Markdown" into "Mark-" / "down", which can break keyword search.
- Confidence: medium (raw text only)
- Skill should: turn off hyphenation (`\hyphenpenalty=10000`), never split skill names.
### R7: No icons in contact details
- Evidence: icons become junk characters in raw text.
- Confidence: medium
- Skill should: replace icons with plain labels or nothing.

### R8: Include the target job title, honestly. 
- Evidence: in Affinda’s search, “frontend engineer” didn’t find a resume whose titles said “Software Developer.” - Confidence: medium (one test, one tool). 
- Skill should: add a headline and summary opening with the target title, never change official titles.

## Parser limitations (not resume problems; don't "fix" these)
 
- Location must look like `City, ST` (two capital letters): `Famagusta, Cyprus` never matches.
- Phone must look like a US number: `+90` is dropped.
- Only one URL field: at most 1 of 3 links can be extracted.
## Open questions / next tests
 
- [ ] Re-test C (header), D (icons), F (table) and H (dates) on top of M
- [ ] Confirm R3–R5 with a second parser (commercial demo, "Jane Doe" copy only)
- [ ] I-word.pdf and J-plain.pdf: does the authoring tool matter?