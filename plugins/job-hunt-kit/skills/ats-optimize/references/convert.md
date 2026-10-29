# Converting a PDF or Word resume to the master `resume.tex`

The goal is a **faithful copy**: the same words and links as the user's file, in the layout of
[resume-template.tex](resume-template.tex). Nothing is tailored, reworded or tidied here.
Tailoring starts only after the user confirms this copy, so that every later change has a
checked starting point.

The user's original file stays untouched. Convert once; later jobs reuse the confirmed
`resume.tex`.

## 1. Read the original

`python3 "${CLAUDE_SKILL_DIR}/scripts/extract_text.py" <original> --json` gives its text and its
link addresses (including links shown only as a word, like "LinkedIn").

- **Exit 3 on a `.doc`:** LibreOffice isn't installed. Pass on the script's message (Save As
  `.docx` or PDF in Word or Google Docs) and wait for the new file.
- **Little or no text from a PDF:** it is a scanned image. Ask for the Word file or a PDF exported
  from a text editor. Retyping from an image invites mistakes nobody can check.
- **Columns:** text from a two-column PDF can come out interleaved. Rebuild each entry by
  meaning; the word check in step 3 doesn't depend on order, and the user reviews order in step 5.
- **No shell tool:** read a PDF with your file-reading tool. A `.docx` needs the script, so ask
  for a PDF instead. Say in step 5 that the scripts weren't run.

Note what an ATS would have trouble with in the original (contact details in a page header or
footer, tables, columns, icons, text in images): it goes in the report.

## 2. Fill the template

Copy `resume-template.tex` to `<profile>/resume.tex` (never overwrite an existing one) and follow
the instructions at the top of the template. In short: the person's exact words, their section
order and headings, one block per job, project or degree, special characters escaped, every
`{{placeholder}}` and example address replaced or the line deleted.

When the original is ambiguous (which dates belong to which role, whether a line is a title or a
bullet), ask the user rather than guess.

## 3. Check the copy

- `python3 "${CLAUDE_SKILL_DIR}/scripts/compare_text.py" <original> resume.tex --json`
  Exit 0 means the same words and links. Fix every `missing`, `added`, `links_missing` and
  `links_added` item in `resume.tex` and re-run until it exits 0. The only differences that may
  stay are page numbers and page headers or footers repeated on every page; list them for the
  user.
- `python3 "${CLAUDE_SKILL_DIR}/scripts/check_layout.py" resume.tex` passes every rule (R5 needs
  a compiled PDF; skip it without a LaTeX engine).

Done when compare_text exits 0 (or only lists the allowed leftovers) and check_layout passes.

## 4. Draft `facts.md`

If the profile has no `facts.md`, draft one from the converted `resume.tex` in the
[profile format](profile-format.md). Copy facts from the resume only. About fields the resume
doesn't state (citizenship, work authorization, time zone) and the "Never claim" list come from
the user: mark them `(to confirm)` in the draft and ask for them in step 5.

## 5. Confirm with the user

This is the one stop before tailoring. In one message, give:

- the path of the new `resume.tex`, and that it is their resume in a new, ATS-safe layout with
  the same words (the compare_text result in one line, plus any allowed leftovers);
- the layout changes they will notice (for example: contact details moved out of the page
  header, the skills table turned into lines);
- how to see it: paste it into a blank Overleaf project and click Recompile;
- the path of the `facts.md` draft;
- your questions, numbered, in the reply itself: every `(to confirm)` item and anything unclear.
  The user answers here in the chat; you write the answers into `facts.md`.

Ask them to answer the questions and confirm both files or say what to correct. Write nothing
else until they answer.
After a correction, re-run compare_text: the only differences left must be the ones the user
asked for.

Done when the user has confirmed `resume.tex` and `facts.md`. Carry on with step 2 of SKILL.md.
