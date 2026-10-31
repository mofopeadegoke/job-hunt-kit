---
type: regex
weight: 2
target: { source: file, path: resume.tex }
match: not_contains
flags: i
pattern: 'GraphQL|\bD3\b|Recharts|Visx|design system|Core Web Vitals|Playwright|code review|pairing|\bled\b|15\+|1,200\+|40\+|your-name|\{\{|github\.com/(?!janedoe-dev\b)|linkedin\.com/in/(?!jane-doe-example\b)'
---
