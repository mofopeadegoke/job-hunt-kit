# Hypotheses
- H1: Two-column layouts get read in the wrong order
- H2: Contact details in the page header or footer get lost
- H3: Icons next to email/phone break their extraction
- H4: Unusual section names ("Where I've worked") get misread
- H5: Skills laid out in a table get scrambled
- H6: Without \pdfgentounicode, some letters ("fi", "fl") disappear from words
- H7: Date formats ("Jun 2025 – Present" vs "06/2025") parse differently

#Findings after pdf resumes are turned into raw text format
- A: Strange characters exists but vital information is preserved. Sections appear in the right order as well. 
- B: Strnage characters also exists and order of information is jumbled up. experiences mix with skills. vital information is lost. 
- C: Strange character exist but vital information is preserved. Sections appear in the right order as well. 
- D: Fewer strange characters but vital information is preserved. Sections appear in the right order as well.
- E: Strange characters exists but vital information is preserved. Sections appear in the right order as well.
- F: Strange characters exists but vital information is preserved. Sections appear in the right order as well. Skils are broken down to different lines making it easier to read as opposed to skills being written in one long line
- G: Strange characters exists but vital information is preserved. Sections appear in the right order as well.
- H: Strange characters exists but vital information is preserved. Sections appear in the right order as well.