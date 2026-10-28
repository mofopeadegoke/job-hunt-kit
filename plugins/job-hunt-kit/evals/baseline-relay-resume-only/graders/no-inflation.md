---
type: regex
weight: 2
target: { source: file, path: out/resume.tex }
match: not_contains
pattern: '\b(?:Led|Spearheaded|Drove|Headed|Directed)\b|\bled the\b|[Mm]anaged (?:a |the )?team|[Tt]eam [Ll]ead|15\+|(?:over|more than) 15\b|1,200\+|(?:over|more than) 1,200|40\+|(?:over|more than) 40\b|[Mm]entored (?:two|2|three|3|several|multiple)|\binterns\b|(?<!20--)\b30\\%|\b(?:20|25)\\%|(?<!estimated )\b20--30|(?<![\d.])[3-9]\+? years (?:of )?(?:(?:professional|production|React(?:/Next\.js)?|Next\.js|and),? )*TypeScript|(?<![\d.])[3-9]\+? years\b[^.;]{0,90}?\b(?:in|with|and)\s+(?:(?:React|Next\.js|React/Next\.js),?\s+(?:and\s+)?)*TypeScript\b'
---
