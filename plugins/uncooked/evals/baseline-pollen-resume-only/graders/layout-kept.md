---
type: regex
target: { source: file, path: out/resume.tex }
pattern: '^(?=[\s\S]*\\usepackage\[none\]\{hyphenat\})(?=[\s\S]*\\quad\$\\cdot\$\\quad \+254)(?=[\s\S]*\\vspace\{6pt\})(?![\s\S]*\\section\*\{Education\}[\s\S]*\\hfill)(?![\s\S]*\\begin\{(?:tabular|multicols|minipage))'
---
