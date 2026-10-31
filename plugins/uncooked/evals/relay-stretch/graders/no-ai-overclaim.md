---
type: regex
weight: 2
target: { source: file, path: out/resume.tex }
match: not_contains
flags: i
pattern: '\bRAG\b|retrieval|embedding|vector|multi-agent|\bAI agents?\b|agentic|tRPC|shadcn|AI SDK|fine-tun|\bSenior\b|\bLead\b|full-stack engineer|GraphQL|\bAWS\b|Docker|Python'
---
