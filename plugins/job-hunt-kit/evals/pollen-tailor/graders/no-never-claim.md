---
type: regex
weight: 2
target: { source: file, path: out/resume.tex }
match: not_contains
flags: i
pattern: 'GraphQL|tRPC|\bAWS\b|Docker|Kubernetes|Python|\bRAG\b|embedding|vector search|\bVue\b|Angular|German|Swift|Kotlin|D3|Recharts|Visx|design system'
---
