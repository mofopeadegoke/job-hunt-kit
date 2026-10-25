# Hypotheses for openResume's parser
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

Same resume content, one change per version, scored against an answer sheet.

| Tool | Type | Versions tested |
| --- | --- | --- |
| `pdftotext` | Raw text extraction | All |
| OpenResume | Rule-based parser (single-column, English, US-oriented) | A–H, K–N |
| Affinda | Commercial, machine-learning parser with candidate search | A, M, Z, P, Q, T0–T5, G1–G3, B, D, E, F, E1 (Jane Doe copies) |

Raw results: `results.csv` (OpenResume), `results-affinda.csv` (Affinda).

## Headline results

1. **A simple parser breaks on layout.** In OpenResume, the original resume lost its email,
   phone, links and 4 of 5 jobs, even though its raw text was perfect. Three spacing fixes
   (version M) recovered them without changing a word.
2. **A commercial parser handles layout, but labels you by your latest job title.** Affinda
   read every layout correctly (two columns, icons, tables, creative headings), but the role
   it assigns is the most recent job title, word for word, and recruiter search depends on it.
3. **Projects may be invisible.** Affinda never showed a Projects section in any version.
   Moving Inscribe from Projects to Experience made it appear.

## Rules for `ats-optimize`

### Important (affects what recruiters see and search)

**R8: The latest job title decides your role and search results**
- Evidence (Affinda): role = most recent title, verbatim (T0–T5). A headline under the name
  changed nothing (T3). A "frontend engineer" search found only "Founder & Frontend Engineer"
  (T1); not "Software Developer (Frontend)" (T4) or "Software Engineer (Frontend)" (T5), which
  were found by "frontend" alone. "Developer" and "engineer" were sometimes treated as
  equivalent (E, F found by "software engineer"), but a specialty is never inferred.
- Rule: the target title must appear **as a contiguous phrase** in the most recent job title.
- Honesty: only on titles the user controls (self-employment, own company, freelance).
  Never change a title an employer gave. Use one title consistently (resume and LinkedIn).
- Confidence: high (Affinda); not yet tested elsewhere.

**R9: Put key evidence in Experience, not only Projects**
- Evidence (Affinda): Projects never shown (all versions). Inscribe appeared once moved to
  Experience (P). Projects sometimes leak into Experience (F counted Omniplexus as a job).
- Rule: real ongoing work (own product, freelance) goes in Experience; project skills must
  also appear in Technical Skills / Summary.
- Confidence: high (Affinda).

**R10: Stack the Education block line by line**
- Evidence (Affinda): GPA extracted only when school, degree, location/date and GPA were each
  on their own line (B, E1). Not extracted with right-aligned (\hfill) lines, a "GPA:" label,
  or a spelled-out degree (A, Q, G1–G3).
- Confidence: medium-high (two versions, one tool).

### Safe habits (required by simple parsers; harmless elsewhere)

| Rule | OpenResume | Affinda |
| --- | --- | --- |
| R1: Standard section headings | Creative names lost every section (E) | No effect |
| R2: Single column | Lost education (B) | No effect |
| R3: Clear space around contact items | Email glued to phone: `0000·name@example.com` (A); fixed by wide gaps (K) | No effect |
| R4: Visible space between entries (> 1.4x line gap) | 1/5 jobs (A) vs 5/5 (L, M) | No effect |
| R5: One page, or no heading at the top of page 2 | Achievements merged into education; "GPA 0.5" from "Top 0.5%" (A); education lost (L) | No effect |
| R6: No hyphenation | Raw text split "Mark-" / "down" | Possibly more skills found (Z: 85 vs 75) |
| R7: No icons in contact details | Icons become junk letters (`m`, `H`, `B`) in raw text | No effect |

### Other observations

- Content can create false fields: "English/Turkish localization" was listed by Affinda as
  spoken languages (E1). Review what a parser infers, not just what it extracts.
- Spelling variants may matter in search: D was found by "front" but not "frontend".
- OpenResume limits (not resume problems): location must look like `City, ST`; phone must
  be US-format (`+90` dropped); only one link field.

## Hypotheses

| # | Hypothesis | OpenResume | Affinda |
| --- | --- | --- | --- |
| H1 | Two columns are read in the wrong order | ✅ Confirmed | ❌ No effect |
| H2 | Contact details in the page header get lost | ❓ | Not tested |
| H3 | Icons break contact extraction | ⚠️ Mixed | ❌ No effect |
| H4 | Unusual section names get misread | ✅ Confirmed (largest effect) | ❌ No effect |
| H5 | Skills in a table get scrambled | ⚠️ Lost categories | ❌ No effect |
| H6 | Without `\pdfgentounicode`, letters go missing | ❌ Rejected (this setup) | Not tested |
| H7 | Date formats parse differently | ❓ | Not tested |

## Open questions

- [ ] Does a "software engineer" search find "Founder & Frontend Engineer" (T1)?
- [ ] Real ATS autofill (Workday, Greenhouse, Lever…) during real applications: log what each extracts
- [ ] I-word.pdf / J-plain.pdf: does the authoring tool matter?



#Predictions
- T0: Assigns Founder & Solo developer as Inscribe experience indicates
- T1: Becomes Founder & Frontend Engineer
- T2: Becomes Founder & Frontend Engineer
- T3: Title remains the title of of the most recent job
- T4: Project does not affect title
- G1: No GPA
- G2: No GPA
- G3: No GPA
- B: Education and jobs not found properly
- E: It loses sections like OpenResume did
- D: Email, phone and links not correct
- F: Skills not found well Differences found