#!/usr/bin/env bash
# Three applications awaiting news. Kranich already interviewed Jane, so its coming rejection
# must keep response_type=interview, or the interview rate silently drops.
set -euo pipefail
bash "$(dirname "${BASH_SOURCE[0]}")/../_shared/copy-profile.sh" 01-pollen-frontend-engineer.txt job-posting.txt

cat > applications.csv <<'EOF'
id,date_applied,company,role,link,location_terms,ats,resume_version,inscribe_title,tailored,status,response_date,response_type,next_step,follow_up_date,autofill_title,autofill_jobs,autofill_phone,autofill_gpa,notes
1,2026-10-20,Pollen Analytics,Frontend Engineer,https://boards.greenhouse.io/pollenanalytics/jobs/4012,Remote (EMEA),greenhouse.io,applications/2026-10-20-pollen-analytics-frontend-engineer,Freelance Frontend Engineer,yes,applied,,,,2026-10-23,,,,,
2,2026-10-10,Kranich Mobility,Senior Frontend Engineer,https://kranich.example/jobs/12,On-site Berlin,,master,Frontend Developer,no,interview,2026-10-15,interview,,2026-10-13,,,,,
3,2026-10-21,Relay,Senior Full-Stack Engineer (Next.js / AI),https://jobs.lever.co/relay/77,Remote (worldwide),lever.co,master,Frontend Developer,no,applied,,,,2026-10-24,,,,,
EOF
