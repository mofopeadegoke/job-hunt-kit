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
3. **Privacy.** No real personal data in this repo (the repo is public). Test fixtures use the
   fictional "Jane Doe". The plugin sends the resume nowhere except to Claude itself; describe
   it that way, not as "everything runs locally". Daniel's real research resumes live outside
   the repo (private folder) and were purged from git history.
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
        scripts/extract_text.py             ← compile (if LaTeX exists) + pdftotext; .py so it runs on Windows
      track/
        SKILL.md                            ← application log, interview rate, follow-ups
    hooks/hooks.json                        ← session-start follow-up reminder (runs track.py hook)
    evals/                                  ← claude plugin eval suite
  research/                                 ← findings and result CSVs (raw resumes are private)
  fixtures/                                 ← Jane Doe profile, fictional job postings, answer key
  tests/                                    ← unittest for the scripts: python -m unittest discover tests
```

### Profile format (lives OUTSIDE the plugin, in the user's own folder)
- `resume.tex` — the master resume (LaTeX for v1)
- `facts.md` — confirmed facts the skills may use: titles, dates, numbers with their exact
  wording, and a **"never claim"** list (things the user has NOT done)
- Later: `applications.csv` for the `track` skill (schema in `research/applications-README.md`)

### `ats-optimize` v1 flow
The source of truth is `SKILL.md` (9 steps). In short: gather inputs → **knockout check first**
(a failed eligibility knockout, like visa, location, time zone or language, is a hard stop:
report and ask before tailoring; a years/seniority shortfall is reported plainly, and tailoring
continues if the user already said to go ahead) → parse check → title (R8)
→ placement (R9) → keyword match (present / reword / move up / partial / gap) → write → verify
(layout + line-by-line truth audit) → `report.md` citing fact IDs.

Deterministic checks go in scripts (reliable, testable); wording and judgment stay with Claude.

### `track` and the hook
`track.py` owns the log (ids, follow-up = applied + 3 days, due list, rates); SKILL.md always
calls it. The SessionStart hook is ONE shell-form command with `"shell": "powershell"`:
`Set-Alias python3 python; python3 ".../track.py" hook`. On Windows (PowerShell) the alias
beats the Microsoft Store `python3` stub; on macOS/Linux (bash, assumed: the docs only describe
the setting on Windows; check in step 7) `Set-Alias` is an unknown command and `python3` runs.
Hooks can't be marked "allowed to fail": every failing hook shows a "SessionStart hook error",
so two hooks (python3 + python) showed one error on every machine. Claude Code here can't find
Git Bash (under `AppData\Local\Programs\Git`), so bash-only hooks fail. Test with
`claude -p ... --plugin-dir plugins/job-hunt-kit --debug --debug-file <log>`.

### Evals (`plugins/job-hunt-kit/evals/`)
- Run: `claude plugin eval plugins/job-hunt-kit --scaffold --allow-tools Write Edit --no-publish`
  (add `--model haiku` for cheap iteration, `--judge-model sonnet` because a Haiku judge misgrades).
- No Bash in cases: native Windows has no sandbox, so granting Bash refuses every run. The skill
  falls back to checking rules by reading the `.tex`.
- No custom-code graders exist, so layout and truth rules are regexes over `out/resume.tex`.
  Check new regexes for free with Node against a known-good resume and broken copies first.
- `baseline-*` cases load an empty stand-in plugin (a `no-plugin/` folder inside each case; the
  tool rejects one outside the case folder) and give plain
  Claude only `resume.tex`: the realistic "no plugin" comparison. The normal without-arm still
  gets `facts.md`, which already does much of the honesty work.

## Status

- Research: done (see findings). Daniel's own master resume follows all rules (v3).
- Applications: logged in `applications.csv` (kept privately, not committed).
- Plugin: steps 1–4 done (skeleton, Jane Doe fixtures with fictional postings, `check_layout.py`
  and `extract_text.py` with 31 unit tests, `ats-optimize` skill tried by hand on Pollen and
  Berlin). Step 5 evals: 7 cases; all plugin cases pass on Haiku after two fixes (knockout hard
  stop, one row per requirement). On Sonnet (3 runs each, Sonnet judge): berlin, master,
  relay, typo 1.00; pollen 0.97 (every regex passes; the `report-judgement` LLM grader is
  noisy). Sonnet exposed two eval/skill bugs: the knockout hard stop blocked a stretch role
  the user had said to tailor anyway (now split into eligibility vs experience knockouts), and
  pollen's grader wrongly required "no knockout not met" when Jane's TypeScript years are
  borderline. Plugin vs plain Claude (Sonnet, 3 runs each, identical graders on the resume and
  chat reply): Pollen 0.96 vs 0.50, Relay 0.95 vs 0.50. Plain Claude kept employer titles and
  added no never-claim skills, but every run attached "4+ years" to TypeScript/Next.js, left
  freelance in Projects (R9), skipped the R8 title, and didn't warn about the TypeScript years.
  The plugin's own summaries did the same "4+ years … in TypeScript" until SKILL.md got a rule
  that a years figure covers only what it was counted for. LLM judges stay noisy (one 3-vote
  FAIL per case in some runs); the regexes are stable.

## Next steps

1. ~~Skeleton~~ · 2. ~~Profile format + fixtures~~ · 3. ~~`check_layout.py`~~ · 4. ~~SKILL.md~~
5. ~~Evals~~
6. ~~`track` skill + session-start follow-up hook~~ (`track.py` + 24 unit tests; 3 eval cases:
   log, replies, ghosted-needs-yes. Sonnet 1.00 on all three; Haiku 1.00 / 0.93 / 1.00, its one
   slip being a rejection after an interview losing `response_type=interview` in 1 of 3 runs.
   LLM graders for notes list every relevant fact and allow paraphrase: a partial fact list
   made the judge fail honest notes.)
7. **Publish:** push to GitHub, install fresh from the marketplace like a stranger, README
   (what it does, honesty rules, research findings), demo GIF, write-up.
   **claude.ai version:** a packaging script builds a zip of `ats-optimize` from the same source,
   stripping Claude Code–only frontmatter (`argument-hint`; claude.ai rejects unknown keys).
   Test it, upload it to claude.ai for real, and offer the download from Daniel's website.
