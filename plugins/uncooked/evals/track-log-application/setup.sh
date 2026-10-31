#!/usr/bin/env bash
# Jane's profile, an existing log with one Relay row, and the application folder ats-optimize
# would have left for Pollen (posting, tailored resume with the "Freelance Frontend Engineer"
# title, report). Logging Pollen should fill columns from that folder and leave the rest blank.
set -euo pipefail
app=applications/2026-10-20-pollen-analytics-frontend-engineer
mkdir -p "$app"
bash "$(dirname "${BASH_SOURCE[0]}")/../_shared/copy-profile.sh" 01-pollen-frontend-engineer.txt "$app/job.txt"

# Move the freelance entry from Projects to the top of Experience, as ats-optimize does (R8/R9).
awk '
  NR == FNR {
    if ($0 ~ /^\\textbf\{Freelance Web Developer\}/) inblock = 1
    if (inblock) block = block $0 "\n"
    if (inblock && $0 ~ /\\end\{itemize\}/) inblock = 0
    next
  }
  $0 ~ /^\\textbf\{Freelance Web Developer\}/ { skip = 1 }
  skip { if ($0 ~ /\\end\{itemize\}/) skip = 0; next }
  { print }
  $0 ~ /^\\section\*\{Experience\}/ { printf "\n%s\n\\vspace{6pt}\n", block }
' resume.tex resume.tex | sed 's/Freelance Web Developer/Freelance Frontend Engineer/' > "$app/resume.tex"
# The first title after the Experience heading must now be the freelance one.
awk '/section\*\{Experience\}/ { on = 1; next } on && /Freelance Frontend Engineer|textit\{Frontend Developer\}/ { print; exit }' \
  "$app/resume.tex" | grep -q 'Freelance Frontend Engineer'
cat > "$app/report.md" <<'EOF'
# Frontend Engineer at Pollen Analytics

## Verdict
Good match. Biggest risk: professional TypeScript is about 2 years 7 months against 3+.

## Title (R8)
- Freelance role retitled "Freelance Frontend Engineer" (an allowed alternative) and listed first.
EOF

cat > applications.csv <<'EOF'
id,date_applied,company,role,link,location_terms,ats,resume_version,inscribe_title,tailored,status,response_date,response_type,next_step,follow_up_date,autofill_title,autofill_jobs,autofill_phone,autofill_gpa,notes
1,2026-10-15,Relay,Senior Full-Stack Engineer (Next.js / AI),https://jobs.lever.co/relay/77,Remote (worldwide),lever.co,master,Frontend Developer,no,applied,,,,2026-10-18,,,,,
EOF
