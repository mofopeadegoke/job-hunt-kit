---
description: Realistic baseline. Plain Claude (empty stand-in plugin, no skill) with only a resume and the Pollen job. Compare its score with pollen-tailor's with-plugin score.
tags: [baseline]
plugins: ["no-plugin"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

I'm applying for the job in job-posting.txt. Can you tailor my resume for it? My resume.tex is in this folder. Put everything you produce in a folder called out/.

I won't be around to answer questions, so make the calls you'd recommend and tell me what you chose. If listing my freelance work first helps, that's fine with me.
