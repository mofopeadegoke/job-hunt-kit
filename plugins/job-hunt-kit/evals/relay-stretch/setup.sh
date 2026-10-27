#!/usr/bin/env bash
set -euo pipefail
bash "$(dirname "${BASH_SOURCE[0]}")/../_shared/copy-profile.sh" 02-relay-senior-fullstack-ai.txt job-posting.txt
