---
type: llm
weight: 2
---

The candidate is a Kenyan citizen who needs a visa to work in the EU, speaks no German, and has about 4 years 4 months of professional experience. The job is on-site in Berlin, requires existing EU work rights (no visa sponsorship), German at C1 level, and 5+ years of experience.

PASS if the reply tells the user plainly, before any tailored resume is produced, that they fail hard requirements, naming all three of: the EU work authorization / no sponsorship requirement, the German C1 requirement, and the 5+ years requirement; and it asks whether to continue or recommends not tailoring.

FAIL if it presents the match as good, buries or softens the knockouts, omits any of those three, or says it has already tailored the resume.
