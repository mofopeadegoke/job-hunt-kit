# Job Hunt Kit privacy policy

Last updated: 31 October 2026

Job Hunt Kit is an open-source plugin for Claude. It helps you tailor a resume to a job posting and
keep a log of your applications. This policy explains what data it uses and where that data goes.

## The short version

The plugin's author receives none of your data. The plugin has no server, no account and no
analytics. Your resume and job search details go to Claude as part of your normal Claude session,
and your files stay in the folder you work in.

## What the plugin uses

- **Your resume and confirmed facts:** `resume.tex` or a PDF or Word resume, and `facts.md`. These
  can include your name, contact details, work history and education.
- **Job postings:** text, files or links you share.
- **Your application log:** `applications.csv`, with details such as company, role, dates, status
  and notes.

## Where your data goes

- **To Claude:** what you share, and what Claude reads from your files during a session, is
  processed by Claude under your agreement with Anthropic. Anthropic's terms and privacy policy
  apply to that data, not this policy.
- **Session-start reminder:** in Claude Code, when you open a folder containing `applications.csv`,
  the plugin checks that file. If follow-ups are due, those entries are added to your Claude
  session.
- **Job posting links:** if you share a link, Claude opens that page with its own tools.

The plugin's scripts run on your computer and make no network connections. They may call programs
you have installed: Poppler, a LaTeX engine or LibreOffice.

Overleaf is an optional step you carry out yourself. If you paste your resume there, Overleaf's own
terms apply.

## Storage and retention

The plugin writes files only where you are working, such as `resume.tex`, `facts.md`,
`applications.csv` and application folders. It keeps them until you delete them. Uninstalling the
plugin does not delete these files.

Your Claude conversations are kept according to your Claude account's settings.

## Your choices

You can read, edit or delete any of these files at any time. To stop the reminder, disable or
uninstall the plugin, or remove `applications.csv` from the folder.

## Children

Job Hunt Kit is intended for adults looking for work, and is not intended for people under 18.

## Changes

Changes to this policy are recorded in the
[project's GitHub history](https://github.com/mofopeadegoke/job-hunt-kit/commits/main/plugins/job-hunt-kit/PRIVACY.md).

## Contact

Ask questions or report problems at
[GitHub Issues](https://github.com/mofopeadegoke/job-hunt-kit/issues).
