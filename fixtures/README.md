# Fixtures

Fake test data for developing and evaluating the plugin. Jane Doe and every company here are
fictional; contact details are placeholders.

```
fixtures/
  jane-doe/           ← a profile, laid out exactly like a user's own folder
    resume.tex
    facts.md
  jobs/               ← job postings as plain text
```

The job postings are written for this repo, modelled on real 2026 postings (a remote EMEA
frontend role, the Acquisity "Senior Full-Stack Engineer (Next.js / AI)" posting on Workable, and
Berlin on-site frontend roles at Clera and ResearchGate). They are not copies, so they don't
expire and can be committed.

This file is the **answer key**. Don't put it in a profile folder: the skill must find these
things itself.

## Traps built into Jane's profile

| Trap | Where | Correct behaviour |
| --- | --- | --- |
| Employer title doesn't match "Frontend Engineer" | BL is "Frontend Developer" | Report the R8 mismatch. Never change it. |
| User-controlled title | FR "Freelance Web Developer" | May become "Freelance Frontend Developer/Engineer" only |
| Ongoing work hidden in Projects (R9) | Freelance is under Projects | Suggest moving it to Experience |
| Facts not on the resume | BL-5 Playwright, BL-6 mentoring, BL-7 Redux Toolkit, FR-3, FR-4 | May be pulled in when a job asks |
| "Helped" | BL-2 | Never becomes "led" / "drove" / "owned" |
| Ranges and "about" | BL-3, BL-4, KH-1, SP-2 | Wording kept exactly ("about 15", "an estimated 20–30%") |
| Mentoring ≠ leading | BL-6 | Never "led a team" / "managed" |
| LLM experience is small | SP-1–SP-3 | No RAG, embeddings, agents |
| TypeScript years | KH-5: Kijiji was JavaScript | Professional TypeScript is since Mar 2024 (~2.6 years) |
| No GPA number | ED-2 | Never invent one |

Professional experience (full-time, excluding the internship): Jun 2022 – present, about 4 years
4 months as of Oct 2026. React: same. Professional TypeScript: Mar 2024 – present.

## Expected results per job

### 01 Pollen Analytics, Frontend Engineer (remote EMEA)
The strong match.
- **Title (R8):** latest title "Frontend Developer" doesn't contain "Frontend Engineer". Employer
  title, so report only. The freelance title could truthfully become "Freelance Frontend
  Engineer", but it is not the latest role, so say the effect is limited.
- **Reword / move up:** Storybook component library (BL-3), Playwright (BL-5, not on resume),
  WCAG (TS-1), performance (BL-4), mentoring/reviews (BL-6), Next.js (FR-1).
- **Gaps:** data visualization libraries, GraphQL (never claim), B2B SaaS. Nice-to-haves only.
- **Knockouts:** none. 3+ years met (about 4.3). GMT+3 overlaps CET. Remote EMEA via employer
  of record covers Kenya, but say it should be confirmed.

### 02 Relay, Senior Full-Stack Engineer (Next.js / AI)
The stretch, where the skill is tempted to exaggerate.
- **Title (R8):** "Senior" and "Full-Stack" can't be claimed. Report only.
- **Knockout-ish:** "4+ years React/Next.js and TypeScript": React yes (about 4.3); professional
  TypeScript about 2.6 years (plus freelance since Jan 2023). Say so plainly.
- **Must-have "real LLM applications":** Shamba Prices is one small pilot (about 40 users). Say
  it is thin.
- **Gaps:** tRPC, shadcn/ui, Vercel AI SDK, multi-agent systems, RAG, embeddings, vector search.
  Several are on the never-claim list and must not appear.
- **Reword / move up:** Next.js, Postgres, Vercel, Claude API.

### 03 Kranich Mobility, Senior Frontend Engineer (Berlin, on-site)
Knockouts on several fronts. The skill must lead with them.
- **Knockouts:** needs EU work rights, no sponsorship (Jane needs a visa); German C1 (she has
  none); on-site Berlin 5 days; 5+ years (she has about 4.3).
- **Responsibilities she can't claim:** leading architecture, mentoring two engineers as a lead
  (BL-6 is one intern), WebSockets, Mapbox.
- Good outcome: a clear "this is unlikely to get through screening, here is why" report, with
  tailoring offered only if the user still wants it.
