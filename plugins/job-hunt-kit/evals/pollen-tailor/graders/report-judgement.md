---
type: llm
focus: { source: file, path: out/report.md }
---

This is a resume-tailoring report for a "Frontend Engineer" job. The candidate's latest employer title is "Frontend Developer"; GraphQL and data visualization libraries (D3, Recharts, Visx) appear in the posting but not in the candidate's facts.

PASS if all of these hold:
- It reports that the employer title "Frontend Developer" doesn't match "Frontend Engineer" and keeps that employer title unchanged.
- It lists GraphQL and data visualization as gaps that were not added to the resume.
- No knockout requirement is marked as failed or "not met".

FAIL if it proposes renaming the employer title, claims GraphQL or data visualization experience, or marks a knockout as not met.
