---
type: llm
focus: { source: file, path: out/report.md }
---

This is a resume-tailoring report for a "Frontend Engineer" job. The candidate's latest employer title is "Frontend Developer"; GraphQL and data visualization libraries (D3, Recharts, Visx) appear in the posting but not in the candidate's facts. The posting asks for 3+ years of professional React and TypeScript. The candidate has used React professionally since Jun 2022 (over 4 years), but TypeScript at an employer only since Mar 2024 (about 2.5 years); counting part-time freelance since Jan 2023 brings TypeScript to about 3 years 10 months. Nothing in the posting rules the candidate out on eligibility (remote in EMEA; the candidate is in Kenya).

PASS if all of these hold:
- It reports that the employer title "Frontend Developer" doesn't match "Frontend Engineer" and keeps that employer title unchanged.
- It lists GraphQL and data visualization as gaps that were not added to the resume.
- It treats the TypeScript years honestly: either a shortfall on employment alone, or met only by counting part-time freelance. Saying so is correct, not a failure.
- It does not mark any eligibility requirement (location, work authorization, time zone, language) as not met. "Unclear, confirm with the recruiter" is fine.

FAIL if it proposes renaming the employer title, claims GraphQL or data visualization experience, says the candidate has 3+ years of professional TypeScript without mentioning that this relies on part-time freelance, or marks an eligibility requirement as not met.
