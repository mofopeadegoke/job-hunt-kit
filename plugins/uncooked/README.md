# Uncooked

Helps you get more interviews **without exaggerating anything**.

Uncooked finds the true things you've already done and puts them where applicant tracking
systems (ATS) and recruiters will see them. If you don't have something a job asks for, it says so.

It takes a LaTeX, PDF or Word resume and gives you back a tailored LaTeX file to turn into a PDF in
Overleaf, with no LaTeX install needed. It also keeps your application log, so you know who to
follow up with and what your interview rate really is.

## Install

In Claude Code (v2.1.275 or later):

```
/plugin install uncooked --marketplace mofopeadegoke/uncooked
```

## What's inside

| Skill | Ask Claude things like | What you get |
| --- | --- | --- |
| **`ats-optimize`** | "Tailor my resume for this job: <link or pasted posting>" | A folder for the application with the tailored `resume.tex` and `report.html`: knockouts, title and placement changes, every requirement marked On resume / Reworded / Moved higher / Added from facts / Partial match / Missing, and the fact behind each change |
| **`track`** | "I applied to Pollen today, log it" · "They called me for a screen" · "Who should I follow up with?" · "What's my interview rate?" | An `applications.csv` log, follow-ups due 3 days after applying, short follow-up notes, and honest stats |

A **session-start reminder** tells you when follow-ups are due when you open Claude Code in the
folder that holds your log. In any other folder it does nothing.

## How tailoring works

1. **Your profile.** Put your resume in a folder. The first time, a PDF or Word resume is copied
   into `resume.tex` word for word, and the plugin drafts `facts.md`: everything true about you
   that a resume may use, plus a **Never claim** list of things you haven't done. You check both
   once.
2. **Knockouts first.** Visa, location, time-zone and language requirements you don't meet stop
   the work until you say to go on. Years or seniority you're short on are reported plainly.
3. **Title and placement.** Your latest job title is checked against the role, and strong evidence
   sitting in Projects moves into Experience where it's true to do so.
4. **Requirement by requirement.** Each requirement is matched to your facts. What your facts
   don't support is marked **Missing**, never added.
5. **Checks.** The layout is tested by script, and the new resume is audited line by line against
   your facts.

Your master resume is never edited. To get the PDF, paste the tailored `resume.tex` into a blank
[Overleaf](https://www.overleaf.com) project and click Recompile.

## The honesty rules

These beat anything a job posting asks for:

- **Reword, reorder, cut, move. Never add.** No skill, tool, number, title, date or result that
  isn't in your confirmed facts.
- **No inflation.** "Helped" stays "helped". "About 15" stays "about 15". "An estimated 20–30%"
  stays an estimated range. "4+ years" covers only the skills you have used for 4+ years.
- **Employer job titles are never changed.** Only titles you control (freelance, your own company)
  may change, and only to alternatives you listed.
- **Bad odds are said out loud.** Requirements you don't meet are reported, never hidden.

## Why these rules

Before any instructions were written, the same resume was parsed many times, changing one thing at
a time, by `pdftotext`, a rule-based parser and a commercial ML parser with recruiter search. Three
results changed what recruiters could see:

- **Your latest job title decides your role in search.** A headline or summary didn't change it.
- **Key evidence belongs in Experience.** The commercial parser never showed Projects.
- **A stacked Education block.** GPA was extracted only when each detail had its own line.

The full write-up is in the
[research findings](https://github.com/mofopeadegoke/uncooked/blob/main/research/findings.md).

## Does it work?

The plugin is tested with 11 eval cases: fictional candidate, fictional postings, and checks on the
files produced and the reply. Against plain Claude with the same resume and posting (Claude
Sonnet, 3 runs each, identical checks):

| Job | With Uncooked | Plain Claude |
| --- | --- | --- |
| Good match | **0.96** | 0.50 |
| Stretch AI role | **0.95** | 0.50 |

Plain Claude kept employer titles and invented no skills, but in every run it attached "4+ years"
to TypeScript when the resume shows about 2.5 years at an employer, left freelance work under
Projects, and never warned about the shortfall.

## Try it

These examples use the fictional candidate Jane Doe. Her files are in the
[`fixtures` folder](https://github.com/mofopeadegoke/uncooked/tree/main/fixtures) of the
GitHub repository. Put them in an empty folder and open Claude Code there.

**1. Convert a PDF resume.** Copy
[`jane-doe/word/resume.pdf`](https://github.com/mofopeadegoke/uncooked/blob/main/fixtures/jane-doe/word/resume.pdf)
and [`jobs/01-pollen-frontend-engineer.txt`](https://github.com/mofopeadegoke/uncooked/blob/main/fixtures/jobs/01-pollen-frontend-engineer.txt)
(saved as `job-posting.txt`), then say:

> I'm applying for the job in job-posting.txt. Can you tailor my resume for it? All I have is
> resume.pdf in this folder. Put the tailored resume and report in a folder called out/.

Claude writes `resume.tex` with the same words as the PDF, drafts `facts.md`, asks its questions
in the chat and stops before tailoring.

**2. Tailor a resume and see a knockout.** Copy
[`jane-doe/resume.tex`](https://github.com/mofopeadegoke/uncooked/blob/main/fixtures/jane-doe/resume.tex),
[`jane-doe/facts.md`](https://github.com/mofopeadegoke/uncooked/blob/main/fixtures/jane-doe/facts.md)
and [`jobs/03-kranich-senior-frontend-berlin.txt`](https://github.com/mofopeadegoke/uncooked/blob/main/fixtures/jobs/03-kranich-senior-frontend-berlin.txt)
(saved as `job-posting.txt`), then say:

> Tailor my resume for the job in job-posting.txt.

Claude reports the requirements Jane can't meet and asks before tailoring anything. With the
Pollen posting instead, it goes on to write the tailored resume and report.

**3. Track applications.** In the same folder, say:

> Log that I applied to Pollen as a Frontend Engineer 4 days ago.

> Who should I follow up with?

Claude adds the application to `applications.csv` and lists Pollen as due a follow-up. The next
time you open Claude Code in that folder, the reminder appears.

## Needs

- **Python 3,** for the scripts and the reminder.
- **Recommended:** `pdftotext` and `pdfinfo` from [Poppler](https://poppler.freedesktop.org/), to
  read PDF resumes (including links hidden behind words like "LinkedIn") and check what an ATS
  sees. Windows: `winget install oschwartz10612.Poppler`. macOS: `brew install poppler`. Linux: the
  `poppler-utils` package.
- **Optional:** a LaTeX engine (`latexmk`, `pdflatex` or `tectonic`) to compile on your machine.
  [LibreOffice](https://www.libreoffice.org/) is only needed for old `.doc` files.

`.docx` files need nothing extra.

## Where it works

| | Claude Code | Cowork | claude.ai chat |
| --- | --- | --- | --- |
| `ats-optimize`, `track` | ✅ tested | expected, not yet tested | expected, not yet tested (no lasting folder for the log) |
| Session-start reminder | ✅ tested on Windows | expected, not yet tested | not supported by chat |

## What it runs, reads and sends

- **Scripts:** Python scripts in this plugin check layout, extract text, compare a converted
  resume with the original, build the report and manage the log. They run on your computer and
  make no network connections.
- **Other programs:** those scripts call Poppler, a LaTeX engine or LibreOffice if you have them
  installed.
- **Reminder:** when a Claude Code session starts, a hook runs `track.py`, which reads
  `applications.csv` from the folder you opened. If follow-ups are due, it adds them to the
  session, so Claude sees those entries. It changes nothing.
- **Files it writes:** `resume.tex`, `facts.md`, `applications.csv` and application folders,
  all in the folder you work in.
- **Job posting links:** if you share a link, Claude opens that page with its own tools.
- **Sends:** your resume and facts go to Claude as part of your session, and nowhere else. The
  plugin has no server and no analytics.

Overleaf is optional, and you choose whether to paste your resume there. Full details:
[privacy policy](https://github.com/mofopeadegoke/uncooked/blob/main/plugins/uncooked/PRIVACY.md).

## Troubleshooting

- **A PDF resume reads badly or its links are missing:** install Poppler, or share a `.docx`
  version.
- **A `.doc` file won't open:** install LibreOffice, or save it as `.docx` or PDF.
- **No reminder:** it only runs in the folder that holds `applications.csv`, and only when a
  follow-up is due.

## Support

Report problems at [GitHub Issues](https://github.com/mofopeadegoke/uncooked/issues).

## License

MIT.
