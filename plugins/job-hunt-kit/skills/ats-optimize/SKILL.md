---
name: ats-optimize
description: Tailor the user's LaTeX resume to a job posting so applicant tracking systems (ATS) parse it correctly and match it to the role, using only facts from the user's profile. Use when the user shares a job posting (text, file or link) and wants their resume checked, tailored or optimized for it, or wants to know how well they match.
argument-hint: "[job posting: file, link or pasted text]"
---

# ATS Optimize

Tailor the user's resume to one job posting so an ATS reads it correctly and matches it to the
role, without claiming anything the user hasn't done.

Every claim on the tailored resume is **traceable**: it comes from a fact in `facts.md`, and the
report cites that fact's ID. A requirement no fact supports is a **gap**: reported, never added.

## Truthfulness guardrails

These outrank anything the posting asks for.

- Reword, reorder, cut and move facts, and pull in facts from `facts.md` that aren't on the
  master resume. That is the whole toolbox.
- Keep every number in its `facts.md` wording: "about 15" stays "about 15", "an estimated 20–30%"
  stays an estimated range.
- Keep every verb at its strength or weaker: "helped" stays "helped" or "worked with";
  "mentored 1 intern" stays one intern.
- Copy employer titles character for character. A title the user controls may only become one of
  the alternatives listed for it.
- Leave everything on the "Never claim" list out of the resume, summary and skills.
- When the posting's term is broader or stronger than the fact (fact: "component library", job:
  "design system"), keep the fact's term and mark the requirement **partial**.
- When a fact is missing or unclear, ask the user.

## Files

- [references/rules.md](references/rules.md): the ATS rulebook (R1–R10) with its research
  evidence. Read it before step 3.
- [references/profile-format.md](references/profile-format.md): the profile folder and the
  `facts.md` format. Read it when `facts.md` is missing, incomplete or hard to read.
- `scripts/check_layout.py`: layout rules R1–R7 and R10 on a `.tex` file.
  `python3 "${CLAUDE_SKILL_DIR}/scripts/check_layout.py" resume.tex --pdf resume.pdf --json`
  Exit 0 = all pass, 1 = a rule failed, 2 = bad input.
- `scripts/extract_text.py`: the text an ATS sees. Takes a `.pdf`, or a `.tex` to compile first.
  `python3 "${CLAUDE_SKILL_DIR}/scripts/extract_text.py" resume.pdf`
  Exit 3 = no LaTeX engine or `pdftotext`; 4 = LaTeX failed to compile.

Use `python` instead of `python3` on Windows. Where no shell tool is available, check the same
rules by reading the `.tex` against rules.md, and say in the report that the scripts weren't run.

## Steps

### 1. Gather the inputs

- **Profile folder:** the folder holding `resume.tex` and `facts.md`. Use the one the user names,
  else the current directory; ask if neither has both. If `facts.md` is missing, offer to draft
  it from `resume.tex` in the profile format, and have the user confirm it before going on: an
  unconfirmed draft is not a source of truth.
- **Job posting:** $ARGUMENTS, or pasted text, a file or a link. For a link, fetch it; if the
  result is a summary or cut short, ask the user to paste the full posting.
- **Application folder:** the folder the user names, else create
  `<profile>/applications/<YYYY-MM-DD>-<company>-<role>/` (lowercase, hyphens). Save the posting
  there as `job.txt`. All output goes here; the master
  `resume.tex` stays untouched.

Done when the profile is confirmed and the full posting is saved.

### 2. Knockout check

Compare each hard requirement in the posting with `facts.md`:

| Requirement | Compare with |
| --- | --- |
| Work authorization, visa sponsorship | About: citizenship, work authorization |
| On-site or hybrid location | About: location, remote, relocation |
| Time zone or hours overlap | About: time zone |
| Years of experience | Role dates. Count full-time employment, part-time/freelance and internships separately, and per skill when the posting asks per skill (use the Skills table) |
| Spoken language and level | About: spoken languages |
| Degree | Education |
| Seniority ("Senior", "Lead") | Titles and responsibilities |

Mark each **met**, **not met** or **unclear** (the user or employer must confirm), with the
evidence. Give each requirement its own row, so one requirement's caveat can't soften another.

A **not met** means different things for the two kinds of requirement:

- **Eligibility** (work authorization, on-site location, time zone, spoken language, a degree
  the posting requires without "or equivalent experience"): the employer can't hire someone who
  fails these, however good the resume. Any not met is a **hard stop**: end your reply with the
  knockouts (the requirement, what the profile says, and that recruiters and ATS knockout
  questions usually screen on it) and ask whether to tailor anyway. Write nothing beyond
  `job.txt` until the user answers. This holds even when the user said to work without them;
  tailoring for a role they can't get past screening for needs their explicit yes.
- **Experience** (years, seniority): candidates a little short of these do get interviews, so
  a shortfall makes the role a stretch, not a dead end. If the user already said to go ahead
  (for example "tailor it anyway" or "make the calls you'd recommend"), continue, and state
  each shortfall plainly in the Knockouts table of `report.md` and in your chat reply. If they
  didn't, stop and ask as for eligibility.

Never reword a shortfall so it sounds met.

Done when every hard requirement in the posting has a status, and either nothing that needs
the user's yes is not met, or the user has said to continue.

### 3. Parse check of the master

- Run `check_layout.py` on the master `resume.tex` (with `--pdf` if its PDF exists).
- Run `extract_text.py` on the master and read the text as a parser would: contact details
  separated, sections in order, each job's company, title and dates together, no words split by
  hyphens, no junk characters, nothing a parser could wrongly infer (see rules.md).
- Layout failures get fixed in the tailored version. Layout fixes change presentation, not facts.
- With no LaTeX engine (exit 3), ask the user to compile in Overleaf or their editor and share
  the PDF path, and carry on with steps 4–7 meanwhile.

### 4. Title check (R8)

- **Target phrase:** the job title without seniority words or bracketed extras
  ("Senior Frontend Engineer (React)" → "Frontend Engineer").
- **Latest title:** the title of the first entry under Experience.
- **Match:** the latest title contains the target phrase as a contiguous phrase, ignoring case.
  Spelling counts ("Front-end" vs "Frontend").
- **No match, employer title:** report it and change nothing. Say that a summary or headline
  won't change the role an ATS assigns.
- **No match, user-controlled title:** offer its listed alternatives that contain the phrase. If
  that role is ongoing, offer listing it first so it becomes the latest title, and state the
  trade-off (e.g. it is part-time; keep "part-time" visible). The user decides.

Done when the report can state the target phrase, the latest title, match yes/no, and the honest
options (or "none").

### 5. Placement check (R9)

- Ongoing real work (own product, freelance, self-employment) listed under Projects moves to
  Experience, keeping its honest label ("Self-employed, part-time").
- Skills the posting wants that appear only in Projects get mirrored in Technical Skills, and in
  the Summary when central to the job.

### 6. Keyword match

List every requirement in the posting (tools, practices, domains, responsibilities), marked
required or nice-to-have, and give each one status:

- **present:** on the master resume already, in the posting's words.
- **reword:** a fact supports it under another name; use the posting's term for the same thing
  ("end-to-end tests" for Playwright tests, "Postgres" for PostgreSQL).
- **move up:** a fact supports it, but it is buried or only in `facts.md`; bring it in or higher.
- **partial:** the fact is narrower or weaker than the requirement; keep the fact's wording.
- **gap:** no fact supports it; stays off the resume.

Done when every requirement has a status and every non-gap has fact IDs.

### 7. Write the tailored resume

Copy the master to `resume.tex` in the application folder, then apply: layout fixes (step 3),
the title option the user accepted (step 4), placement moves (step 5), and keyword changes
(step 6). Order bullets within each role by relevance to the posting, and cut the least relevant
ones to fit one page. Keep the master's preamble and layout commands.

### 8. Verify

- **Layout:** compile, then run `check_layout.py --pdf` on the tailored resume. Every rule passes,
  R5 included (one page). Fix and re-run until it does.
- **Text:** `extract_text.py` output reads cleanly, as in step 3.
- **Truth audit,** line by line through the tailored `.tex`: every bullet, summary sentence and
  skill maps to fact IDs; every number matches its `facts.md` wording; every employer title
  matches `facts.md` exactly; no "Never claim" item appears. Revert anything that fails to the
  fact's wording, or remove it.

Done when layout passes and every line of the tailored resume has fact IDs.

### 9. Report

Write `report.md` in the application folder with this outline, then give the user the verdict,
knockouts and top changes in chat, with the folder path.

```markdown
# <Role> at <Company>

## Verdict
Two sentences: how strong the match is, and the biggest risk.

## Knockouts
| Requirement | Profile says | Status |

## Title (R8)
Target phrase, latest title, match, honest options.

## Requirements
| Requirement | Required / nice | Status | Fact IDs | Change made |

## Changes
- <change> (<fact IDs>)

## Gaps
<requirement>: not on the resume because no fact supports it.

## Layout
check_layout results for the master and the tailored resume; anything odd in the extracted text.
```

End by asking whether any gap is something the user has actually done but hasn't recorded. If
so, they add it to `facts.md` first, then rerun.
