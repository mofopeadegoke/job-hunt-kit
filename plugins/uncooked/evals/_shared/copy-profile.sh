#!/usr/bin/env bash
# Copies Jane Doe's profile and one job posting into the run's empty workspace.
# The answer key (fixtures/README.md) is deliberately left behind.
# Usage, from a case's setup.sh:
#   bash copy-profile.sh <job file in fixtures/jobs> <name in workspace> [resume-only]
# "resume-only" leaves out facts.md, like a user who has only a resume.
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fixtures="$here/../../../../fixtures"

cp "$fixtures/jane-doe/resume.tex" "$fixtures/jane-doe/resume.pdf" .
if [ "${3:-}" != "resume-only" ]; then
  cp "$fixtures/jane-doe/facts.md" .
fi
cp "$fixtures/jobs/$1" "$2"
