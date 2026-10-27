#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "${BASH_SOURCE[0]}")/../_shared/copy-profile.sh" 01-pollen-frontend-engineer.txt job-posting.txt
