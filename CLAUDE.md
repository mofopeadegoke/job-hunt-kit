# Job Hunt Kit — project context

Week 2 project of a 12-week self-directed sprint. Daniel is a frontend engineer (React,
TypeScript, React Native, Next.js) building full-stack and AI engineering skills. The goal is
a published Claude Code plugin that helps job seekers get more interviews **without
exaggerating anything**, plus the learning that comes from building and evaluating it.

## How to work with Daniel

- **Explain in very simple terms**, especially AI, plugin and infra parts. Define jargon.
- **Give complete files** for new or replaced files, not fragments, unless a change is a few lines.
- **Comments only explain *why*, when the code isn't obvious.** No comments restating code.
- **Use pnpm** for any Node tooling. Never npm.
- One step at a time; finish each step with a short test checklist and wait for Daniel.
- Check current docs when something may have changed (Claude Code plugins, skills, evals).

## Non-negotiable rules for the plugin

1. **Truthfulness.** Outputs may reword, reorder and cut; they may never add skills, tools,
   numbers, titles, dates, responsibilities or results that aren't in the user's profile.
   Never inflate ("helped" → "led", "estimated 10–20%" → "20%", "about 10" → "10+").
2. **Employer job titles are never changed.** Only titles the user controls (own company,
   self-employment, freelance) may be adjusted, and only to another true description.
3. **Privacy.** No real personal data in this repo. Test fixtures use "Jane Doe" with fake
   contact details. The plugin never uploads resumes anywhere; everything runs locally.
4. **Honest about odds.** Knockout criteria (visa, time zone, years, language) are reported
   plainly, not hidden.

## Research findings (the skill's rulebook)

Full write-up: `research/findings.md`. Raw data: `research/results.csv` (OpenResume),
`research/results-affinda.csv` (Affinda). Tools: `pdftotext`, OpenResume (rule-based parser),
Affinda (commercial ML parser, Jane Doe copies only).

**Important (affect what recruiters see and search):**
- **R8 Latest job title decides role and search.** Affinda assigns the most recent job title
  verbatim as the candidate's role. A headline/summary doesn't change it. A "frontend engineer"
  search matched only titles containing that exact phrase ("Founder & Frontend Engineer"), not
  "Software Developer (Frontend)" or "Software Engineer (Frontend)".
- **R9 Key evidence in Experience, not only Projects.** Affinda never showed Projects. Ongoing
  real work (own product, freelance) belongs in Experience; project skills must also appear in
  Technical Skills / Summary.
- **R10 Stacked Education block.** GPA was extracted only when school, degree, location/date and
  GPA were each on their own line (no `\hfill`).

**Safe habits (break simple parsers; harmless for commercial ones):**
- R1 standard section headings · R2 single column · R3 clear space around contact separators
  (`\quad$\cdot$\quad`) · R4 visible space between entries (`\vspace{6pt}`, > 1.4x line gap) ·
  R5 one page, or no heading at the top of page 2 · R6 hyphenation off · R7 no icons.

**Other:** parsers can infer false fields (e.g. "English/Turkish localization" listed as spoken
languages). OpenResume limits (US-only location/phone formats, one link field) are parser
problems, not resume problems: never "fix" a resume for them.

## Plugin design

```
job-hunt-kit/
  .claude-plugin/marketplace.json          ← the catalog (one plugin for now; Ship Kit later)
  plugins/job-hunt-kit/
    .claude-plugin/plugin.json
    skills/
      ats-optimize/
        SKILL.md                            ← instructions (the core)
        references/rules.md                 ← the rulebook above, in checklist form
        references/profile-format.md        ← how users describe themselves
        scripts/check_layout.py             ← deterministic checks on a .tex file
        scripts/extract_text.sh             ← pdftotext wrapper for the parse check
      track/
        SKILL.md                            ← application log, interview rate, follow-ups
    hooks/                                  ← follow-up reminder at session start (later)
    evals/                                  ← claude plugin eval suite
  research/                                 ← findings, results, answer sheets, test resumes
  fixtures/                                 ← Jane Doe profile, resumes, job postings
```

### Profile format (lives OUTSIDE the plugin, in the user's own folder)
- `resume.tex` — the master resume (LaTeX for v1)
- `facts.md` — confirmed facts the skills may use: titles, dates, numbers with their exact
  wording, and a **"never claim"** list (things the user has NOT done)
- Later: `applications.csv` for the `track` skill (schema in `research/applications-README.md`)

### `ats-optimize` v1 flow
1. Read the profile and the job description.
2. **Parse check:** compile/extract text with `pdftotext`; run `check_layout.py` on the `.tex`
   (safe habits R1–R7, R10).
3. **Title check (R8):** does the most recent title contain the job's title as a phrase? If not,
   suggest only honest options (user-controlled titles). Report mismatches.
4. **Placement check (R9):** key evidence in Experience; project skills mirrored in Skills.
5. **Keyword gaps:** required skills sorted into reword / move up / gap (never add).
6. **Knockout check:** visa, time zone, years, language, degree.
7. **Output:** tailored one-page `.tex`, compiled PDF, and a report where every change cites the
   profile line that supports it.

Deterministic checks go in scripts (reliable, testable); wording and judgment stay with Claude.

## Status

- Research: done (see findings). Daniel's own master resume follows all rules (v3).
- Applications: logged in `applications.csv` (kept privately, not committed).
- Plugin: not started.

## Next steps

1. **Skeleton:** marketplace.json, plugin.json, empty skill folders; load with
   `claude --plugin-dir ./plugins/job-hunt-kit` and confirm the skills appear.
2. **Profile format + Jane Doe fixtures:** `fixtures/jane-doe/resume.tex`, `facts.md`, and 3 real
   job postings saved as text.
3. **`check_layout.py`:** checks for standard headings, no tables/columns/icons, `\vspace` between
   entries, stacked Education (no `\hfill` in Education), hyphenation off, one page (via
   `pdfinfo`). Unit-test it against the research versions (A should fail, M/v3 should pass).
4. **`ats-optimize` SKILL.md** following the flow above; try it on the fixtures.
5. **Evals** (`claude plugin eval`): truthfulness (LLM judge vs `facts.md`), layout rules
   (`check_layout.py` on the output), employer titles unchanged, triggering, no-plugin baseline.
   Iterate on the skill until it passes.
6. **`track` skill + session-start follow-up hook.**
7. **Publish:** push to GitHub, install fresh from the marketplace like a stranger, README
   (what it does, honesty rules, research findings), demo GIF, write-up.
   **claude.ai version:** a packaging script builds a zip of `ats-optimize` from the same source,
   stripping Claude Code–only frontmatter (`argument-hint`; claude.ai rejects unknown keys).
   Test it, upload it to claude.ai for real, and offer the download from Daniel's website.
