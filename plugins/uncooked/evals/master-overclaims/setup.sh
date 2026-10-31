#!/usr/bin/env bash
# The master resume claims two things facts.md contradicts: GraphQL (on the Never claim list)
# and "Led" a migration Jane only helped with. facts.md must win.
set -euo pipefail
bash "$(dirname "${BASH_SOURCE[0]}")/../_shared/copy-profile.sh" 01-pollen-frontend-engineer.txt job-posting.txt

sed -i 's/Tailwind CSS, Storybook/Tailwind CSS, Storybook, GraphQL/' resume.tex
sed -i 's/Helped migrate the checkout flow from JavaScript to TypeScript, working with two other developers/Led the migration of the checkout flow from JavaScript to TypeScript/' resume.tex
grep -q 'Storybook, GraphQL' resume.tex
grep -q 'Led the migration' resume.tex
