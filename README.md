# Job Hunt Kit

A Claude Code plugin that helps you get more interviews **without exaggerating anything**.

It tailors your resume (LaTeX, PDF or Word) to a job posting so applicant tracking systems (ATS)
read it correctly and match it to the role, using only facts you have confirmed. You get back a
LaTeX file to turn into a PDF in Overleaf, with no LaTeX install needed. It tells you plainly when
a job is a long shot. And it keeps your application log, so you know who to follow up with and
what your interview rate really is.

```
/plugin install job-hunt-kit --marketplace mofopeadegoke/job-hunt-kit
```

## What's inside

| Skill | Ask Claude things like | What you get |
| --- | --- | --- |
| **`ats-optimize`** | "Tailor my resume for this job: <link or pasted posting>" | A folder for the application with the tailored `resume.tex` and a report (`report.html` for your browser): knockouts, title and placement changes, every requirement marked On resume / Reworded / Moved higher / Added from facts / Partial match / Missing, and the fact behind each change |
| **`track`** | "I applied to Pollen today, log it" · "They called me for a screen" · "Who should I follow up with?" · "What's my interview rate?" | An `applications.csv` log, follow-ups due 3 days after applying, short follow-up notes, and honest stats |

A **session-start reminder** tells you when follow-ups are due whenever you open Claude Code in the
folder that holds your log.

## The honesty rules

These beat anything a job posting asks for:

- **Reword, reorder, cut, move. Never add.** No skill, tool, number, title, date or result that
  isn't in your `facts.md`.
- **No inflation.** "Helped" stays "helped". "About 15" stays "about 15". "An estimated 20–30%"
  stays an estimated range. "4+ years" covers only the skills you have used for 4+ years.
- **Employer job titles are never changed.** Only titles you control (freelance, your own company)
  may change, and only to alternatives you listed.
- **Bad odds are said out loud.** Visa, location, time-zone and language requirements you don't
  meet stop the tailoring until you say to go on. Years or seniority you're short on are reported
  plainly.
- A requirement your facts don't support is reported as **Missing**, never added.
- **A PDF or Word resume is copied word for word first.** The plugin checks the LaTeX copy has
  exactly the same words and links as your file, and you confirm it before any tailoring.

## Install

In Claude Code (v2.1.275 or later):

```
/plugin install job-hunt-kit --marketplace mofopeadegoke/job-hunt-kit
```

Or from your shell:

```
claude plugin marketplace add mofopeadegoke/job-hunt-kit
claude plugin install job-hunt-kit@job-hunt-kit
```

Update later with `claude plugin update job-hunt-kit@job-hunt-kit`.

**Needs:** Python 3 (for the scripts and the reminder).

**Recommended:** `pdftotext` and `pdfinfo` from [Poppler](https://poppler.freedesktop.org/), to
read a PDF resume (including links hidden behind words like "LinkedIn") and to check what an ATS
sees. On Windows: `winget install oschwartz10612.Poppler`; macOS: `brew install poppler`; Linux:
the `poppler-utils` package.

**Optional:**
- A LaTeX engine (`latexmk`, `pdflatex` or `tectonic`) to compile and check the PDF on your
  machine. Without one, compile in Overleaf; the plugin checks the `.tex` source and says so.
- [LibreOffice](https://www.libreoffice.org/), only for old `.doc` files. Without it, save the
  file as `.docx` or PDF and use that.

`.docx` files need nothing extra.

## Quick start

1. **Make a profile folder** and put your resume in it: `resume.tex`, or a PDF or Word file
   (`.pdf`, `.docx`, `.doc`).
2. **Open Claude Code in that folder** and share a job posting: "Tailor my resume for this job".
   - **The first time, with a PDF or Word resume,** the plugin copies it into `resume.tex` (the
     same words in an ATS-safe layout) and drafts `facts.md`: everything true about you that a
     resume may use, each fact with an ID, plus a **Never claim** list of things you haven't done.
     It asks you a few questions in the chat. Check both files and answer; this happens once.
     See [the profile format](plugins/job-hunt-kit/skills/ats-optimize/references/profile-format.md)
     and the [Jane Doe example](fixtures/jane-doe/facts.md).
   - **Every job after that,** you get a folder `applications/<date>-<company>-<role>/` with the
     tailored `resume.tex` and `report.html` (open it in your browser). Your master resume is
     never edited.
3. **Get the PDF:** in [Overleaf](https://www.overleaf.com), New Project → Blank Project, replace
   all of `main.tex` with the tailored `resume.tex`, click Recompile, then Download PDF.
4. **After you apply**, say "I applied, log it". Tell Claude when you hear back. Ask who to follow
   up with.

## Why these rules: the research

Before writing any instructions, the same resume was parsed many times, changing one thing at a
time, by `pdftotext`, a rule-based parser (OpenResume) and a commercial ML parser with recruiter
search (Affinda). Full write-up: [research/findings.md](research/findings.md).

What changes what recruiters see:

- **Your latest job title decides your role in search.** Affinda assigned the most recent title
  verbatim; a headline or summary didn't change it. A "frontend engineer" search matched only titles
  containing that exact phrase.
- **Key evidence belongs in Experience, not only Projects.** Affinda never showed Projects. Ongoing
  real work (freelance, your own product) goes in Experience.
- **Stack the Education block.** GPA was extracted only when school, degree, location/date and GPA
  each had their own line.

Safe habits that break simple parsers and cost nothing: standard headings, one column, clear space
around contact separators, visible space between entries, one page, hyphenation off, no icons.

## Does it work? Evals

The plugin ships with an eval suite (`plugins/job-hunt-kit/evals/`, run with `claude plugin eval`):
11 cases with fictional candidate Jane Doe and fictional job postings, each scored by regex checks
on the files produced and by an LLM judge on the reply.

**Plugin vs plain Claude** (Claude Sonnet, 3 runs each, identical checks; plain Claude gets the
same resume and posting):

| Job | With Job Hunt Kit | Plain Claude |
| --- | --- | --- |
| Good match (Pollen) | **0.96** | 0.50 |
| Stretch AI role (Relay) | **0.95** | 0.50 |

Plain Claude kept employer titles and invented no skills, but in every run it attached "4+ years"
to TypeScript (the resume shows about 2.5 years at an employer), left freelance work under
Projects, and never warned about the shortfall.

The other cases (all 1.00 on Sonnet) check that it turns a PDF resume into LaTeX word for word and
asks you to confirm it before tailoring, stops on a job the candidate can't legally take,
removes overclaims already in a master resume, stays out of unrelated edits, logs applications
without inventing fields, counts interviews correctly, and never marks an application "ghosted"
without asking.

## Privacy

Your resume and facts are sent nowhere except to Claude itself, as part of your normal Claude
session. The plugin has no server and no analytics. Your profile and application log stay in your
own folder.

## Where it works

| | Claude Code | Cowork | claude.ai chat |
| --- | --- | --- | --- |
| `ats-optimize`, `track` | ✅ tested | expected, not yet tested | expected, not yet tested (no lasting folder for the log) |
| Session-start reminder | ✅ tested on Windows | expected, not yet tested | not supported by chat |

## Development

```
python -m unittest discover tests            # 103 unit tests for the scripts
claude plugin eval plugins/job-hunt-kit --scaffold --allow-tools Write Edit --model sonnet --judge-model sonnet
claude plugin validate --strict plugins/job-hunt-kit
```

Test fixtures use the fictional Jane Doe; no real personal data is in this repository.

## License

MIT. See [LICENSE](LICENSE).
