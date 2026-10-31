---
name: track
description: Keep the user's job application log (applications.csv). Use when the user has applied somewhere and wants it logged, hears back from an employer (screening, interview, rejection, offer), asks who to follow up with, or asks for their interview rate or job-search stats.
---

# Track

Keep `applications.csv` accurate and tell the user, plainly, where their search stands.

`scripts/track.py` owns the log's rules: ids, the 3-day follow-up date, which applications are
due, and the rates. Run it for every read and write, so dates and numbers come from one place.

```
python3 "${CLAUDE_SKILL_DIR}/scripts/track.py" add    <log> --set column=value ...
python3 "${CLAUDE_SKILL_DIR}/scripts/track.py" update <log> <id> --set column=value ... [--followed-up]
python3 "${CLAUDE_SKILL_DIR}/scripts/track.py" due    <log>
python3 "${CLAUDE_SKILL_DIR}/scripts/track.py" stats  <log>
```

Use `python` instead of `python3` on Windows. Exit 2 = bad input; the message says what to fix.
Where no shell tool is available, edit the CSV directly by the same rules (follow-up date =
applied + 3 days, quote any value containing a comma) and tell the user the script wasn't run.

## The log

**Location:** `applications.csv` in the current directory, or in the folder the user names. The
profile (`resume.tex`, `facts.md`) normally sits beside it; check with Glob before saying a file
is missing. The script creates the log on the first `add`. The session-start reminder checks
only the folder a session opens in, so if the log lives elsewhere, say that the reminder won't
see it.

**Columns.** Fill a column only from what the user said, the posting, or the application folder.
Leave the rest blank; a blank is honest, a guess is not.

| Column | Value |
| --- | --- |
| `id`, `follow_up_date` | Set by the script. |
| `date_applied` | `YYYY-MM-DD`; the script defaults to today. |
| `company`, `role` | As written in the posting. |
| `link` | Posting URL. |
| `location_terms` | Remote / hybrid / on-site, region, visa or time-zone terms. |
| `ats` | The applicant tracking system, when the link shows it (greenhouse.io, lever.co, myworkdayjobs.com, ashbyhq.com…). |
| `resume_version` | The tailored resume's path (the application folder), or `master`. |
| `inscribe_title` | The job title of the first entry under Experience on the resume sent (the title ATS parsers take as the current role). |
| `tailored` | `yes` or `no`. |
| `status` | `applied`, `screening`, `interview`, `offer`, `rejected`, `withdrawn` or `ghosted`. |
| `response_date`, `response_type` | When and how the employer replied: `screening`, `interview`, `rejection`, `offer`. |
| `next_step` | What happens next and when, in the user's words. |
| `autofill_title`, `autofill_jobs`, `autofill_phone`, `autofill_gpa` | Optional research: whether the ATS application form filled each field correctly from the resume (`ok`, `wrong`, `missing`). Only when the user reports it. |
| `notes` | Anything else. The script appends "followed up DATE" here. |

## Steps

Pick the branch that matches the request; a message can need more than one.

### Log an application

1. If an application folder exists for it (from `ats-optimize`: `job.txt`, `resume.tex`,
   `report.md`), read it to fill `company`, `role`, `link`, `location_terms`, `resume_version`,
   `inscribe_title` and `tailored`.
2. Ask only for what's missing among `company`, `role` and the date applied, when the user hasn't
   given it. Everything else may stay blank.
3. Run `add`. Tell the user the id and the follow-up date.

Done when the row exists and the user knows when to follow up.

### Record a reply or change

1. Find the row by company and role (`due` or the CSV); ask if more than one matches.
2. Map what happened to `status`: a recruiter call → `screening`; an interview booked →
   `interview`; a rejection → `rejected`; an offer → `offer`; the user pulled out → `withdrawn`.
   Set `response_date` and `response_type` with it. A rejection after an interview keeps
   `response_type=interview`, so it still counts as an interview.
3. When the user says they followed up, run `update <id> --followed-up`: it notes the date and
   sets the next follow-up 3 days out. Add `--today YYYY-MM-DD` when it happened on another day.
4. Run `update`, then confirm the change in one line.

Done when the row matches what the user reported.

### Follow-ups due

1. Run `due`.
2. List each one: company, role, days since applying, follow-ups already sent.
3. For one with 2 or more follow-ups and no reply, suggest marking it `ghosted`, and change it
   only on the user's yes.
4. If the user asks for a follow-up message, keep it short: the role, the date applied, and one
   reason they fit, taken from that application's `report.md` or `facts.md`. Quote each fact in
   its own words: numbers, verbs and terms stay as written ("about 15 reusable React components"
   stays that, never "component libraries"), and years come only from the Skills table.

Done when the user has the list, and every change they asked for is in the log.

### Stats

1. Run `stats`.
2. Report applications, reply rate and interview rate, and the count per status.
3. Under 20 applications, say the rates are rough: one more interview moves them a lot.

Done when the user has the numbers and how much to trust them.
