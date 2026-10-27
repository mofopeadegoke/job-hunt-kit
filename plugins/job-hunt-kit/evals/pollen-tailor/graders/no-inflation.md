---
type: regex
weight: 2
target: { source: file, path: out/resume.tex }
match: not_contains
pattern: '\b(?:Led|Spearheaded|Drove|Headed|Directed)\b|\bled the\b|[Mm]anaged (?:a |the )?team|[Tt]eam [Ll]ead|\bSenior\b|15\+|(?:over|more than) 15\b|1,200\+|(?:over|more than) 1,200|40\+|(?:over|more than) 40\b|[Mm]entored (?:two|2|three|3|several|multiple)|\binterns\b|(?<!20--)\b30\\%|\b(?:20|25)\\%|(?<!estimated )\b20--30'
---
