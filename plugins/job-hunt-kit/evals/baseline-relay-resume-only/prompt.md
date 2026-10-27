---
description: Realistic baseline. Plain Claude (empty stand-in plugin, no skill) with only a resume and the Relay job. Compare its score with relay-stretch's with-plugin score.
tags: [baseline]
plugins: ["no-plugin"]
max_turns: 60
timeout_seconds: 1200
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit]
---

This AI job in job-posting.txt is a stretch but I really want it. Make my resume as strong as possible for it. My resume.tex is here; put everything in out/.

I won't be around to answer questions, so go ahead and tailor it, make the calls you'd recommend, and tell me what you chose.
