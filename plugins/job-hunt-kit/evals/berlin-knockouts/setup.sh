#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "${BASH_SOURCE[0]}")/../_shared/copy-profile.sh" 03-kranich-senior-frontend-berlin.txt job-posting.txt
