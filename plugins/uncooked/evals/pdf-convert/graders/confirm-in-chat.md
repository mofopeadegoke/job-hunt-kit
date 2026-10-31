---
type: llm
weight: 2
---

The user has only a PDF resume and asked for it to be tailored to a job. The skill must first convert the PDF into a LaTeX master resume (resume.tex) with the same words, draft a facts.md, and stop there: the user has to confirm both before any tailoring.

Judge the assistant's final reply to the user.

PASS if all of these hold:
- It names resume.tex as the converted resume and facts.md as a draft to check.
- It asks its questions in the reply itself as a numbered list (for example: things the user has not done that must never be claimed, or details the resume doesn't state). Pointing to questions written only inside facts.md is not enough.
- It asks the user to confirm the converted resume and facts.md (or say what to correct) before tailoring.
- It does not say the resume has already been tailored or present a finished match report.

FAIL if the questions appear only in a file, if it skips the confirmation and says it tailored the resume, or if it claims the candidate has skills the PDF doesn't show.
