#!/usr/bin/env bash
# A user with only a PDF resume made in Word: no resume.tex, no facts.md.
set -euo pipefail
fixtures="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/../../../../fixtures"
cp "$fixtures/jane-doe/word/resume.pdf" resume.pdf
cp "$fixtures/jobs/01-pollen-frontend-engineer.txt" job-posting.txt
