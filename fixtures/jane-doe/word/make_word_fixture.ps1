# Builds fixtures/jane-doe/word/resume.{docx,pdf,doc} with Microsoft Word (Windows only).
# Run from the repo root: powershell -ExecutionPolicy Bypass -File fixtures\jane-doe\word\make_word_fixture.ps1
param([string]$OutDir = "$PSScriptRoot")
$ErrorActionPreference = 'Stop'
# Non-ASCII built from code points: PowerShell 5.1 reads BOM-less scripts as ANSI.
$dash = [string][char]0x2013
$dot = "  " + [string][char]0x00B7 + "  "
$m = [Type]::Missing
New-Item -ItemType Directory -Force $OutDir | Out-Null

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Add()
    $doc.PageSetup.PaperSize = 2          # letter
    foreach ($side in 'TopMargin', 'BottomMargin', 'LeftMargin', 'RightMargin') { $doc.PageSetup.$side = 36 }
    $doc.PageSetup.HeaderDistance = 24
    $normal = $doc.Styles.Item(-1)
    $normal.Font.Name = 'Calibri'
    $normal.Font.Size = 10
    $normal.ParagraphFormat.SpaceAfter = 0
    $normal.ParagraphFormat.SpaceBefore = 0
    $normal.ParagraphFormat.LineSpacingRule = 0

    $sel = $word.Selection
    function Start-Line([int]$Align = 0, [switch]$Bullet, [switch]$Tab) {
        $sel.ClearFormatting()
        $sel.ParagraphFormat.Alignment = $Align
        if ($Tab) { $sel.ParagraphFormat.TabStops.Add(540, 2) | Out-Null }
        if ($Bullet) { $sel.Range.ListFormat.ApplyBulletDefault(); $sel.ParagraphFormat.SpaceAfter = 0 }
    }
    function Seg([string]$Text, [switch]$B, [switch]$I, [int]$Size = 0) {
        # Default Paragraph Font: text typed after a link would otherwise stay in the Hyperlink style.
        $sel.Style = $doc.Styles.Item(-66)
        $sel.Font.Reset()
        $sel.Font.Bold = [int][bool]$B
        $sel.Font.Italic = [int][bool]$I
        if ($Size) { $sel.Font.Size = $Size }
        $sel.TypeText($Text)
    }
    function Link([string]$Address, [string]$Shown) {
        $doc.Hyperlinks.Add($sel.Range, $Address, $m, $m, $Shown) | Out-Null
        $sel.EndKey(6) | Out-Null
    }
    function End-Line { $sel.TypeParagraph() }
    function Heading([string]$Text) {
        Start-Line
        $sel.ParagraphFormat.SpaceBefore = 6
        $sel.ParagraphFormat.SpaceAfter = 3
        $sel.ParagraphFormat.Borders.Item(-3).LineStyle = 1
        Seg $Text -B -Size 12
        End-Line
    }
    function Entry([string]$Left, [string]$Right, [switch]$Italic) {
        Start-Line -Tab
        if ($Italic) { Seg $Left -I } else { Seg $Left -B }
        Seg ("`t" + $Right)
        End-Line
    }
    function Bullets([string[]]$Items) {
        foreach ($item in $Items) { Start-Line -Bullet; Seg $item; End-Line }
    }
    function Gap { Start-Line; $sel.ParagraphFormat.SpaceAfter = 0; Seg ''; $sel.Font.Size = 3; End-Line }

    # Contact block in the page header, as many Word templates do (some ATS skip headers).
    $word.ActiveWindow.View.Type = 3
    $word.ActiveWindow.ActivePane.View.SeekView = 9
    Start-Line -Align 1; Seg 'JANE DOE' -B -Size 18; End-Line
    Start-Line -Align 1; Seg ("Nairobi, Kenya" + $dot + "+254 700 000 000" + $dot)
    Link 'mailto:jane.doe@example.com' 'jane.doe@example.com'; End-Line
    Start-Line -Align 1
    Link 'https://github.com/janedoe-dev' 'GitHub'; Seg $dot
    Link 'https://www.linkedin.com/in/jane-doe-example' 'LinkedIn'; End-Line
    Start-Line -Align 1; Seg 'Work Authorization:' -I
    Seg (" Kenyan Citizen" + $dot + "Remote Ready (GMT+3)" + $dot + "Visa Required for Onsite Roles Abroad")
    $word.ActiveWindow.ActivePane.View.SeekView = 0

    Heading 'SUMMARY'
    Start-Line
    Seg 'Frontend developer with 4+ years of professional experience building React web apps and a React Native mobile app for a payments company and a health-tech startup. Builds reusable component libraries, improves page performance, and writes automated tests. Also runs a part-time freelance practice building Next.js websites for small businesses. Fluent in English, native Swahili speaker.'
    End-Line

    Heading 'TECHNICAL SKILLS'
    $skills = @(
        @('Languages', 'TypeScript, JavaScript (ES6+), HTML5, CSS3, SQL'),
        @('Frontend', 'React, Next.js, React Native, Tailwind CSS, Storybook'),
        @('Backend', 'Node.js, Express, REST APIs, PostgreSQL'),
        @('Testing & Tools', 'Jest, React Testing Library, Git, GitHub Actions, Vercel, Figma'),
        @('Spoken Languages', 'English (fluent), Swahili (native), French (basic)')
    )
    # Skills in a borderless two-column table: a common Word template layout.
    $table = $doc.Tables.Add($sel.Range, $skills.Count, 2)
    $table.Borders.Enable = 0
    $table.Columns.Item(1).Width = 110
    $table.Columns.Item(2).Width = 430
    for ($r = 0; $r -lt $skills.Count; $r++) {
        $table.Cell($r + 1, 1).Range.Text = $skills[$r][0]
        $table.Cell($r + 1, 1).Range.Font.Bold = 1
        $table.Cell($r + 1, 2).Range.Text = $skills[$r][1]
    }
    $sel.EndKey(6) | Out-Null

    Heading 'EXPERIENCE'
    Entry 'Brightleaf Labs' 'Nairobi, Kenya (Hybrid)'
    Entry 'Frontend Developer' "Mar 2024 $dash Present" -Italic
    Bullets @(
        'Built and maintained the customer dashboard of a payments web app in React and TypeScript.',
        'Helped migrate the checkout flow from JavaScript to TypeScript, working with two other developers.',
        'Built about 15 reusable React components, documented in Storybook.',
        "Improved dashboard load time by an estimated 20${dash}30% (Lighthouse lab data) through code splitting and image optimization."
    )
    Gap
    Entry 'Kijiji Health' 'Nairobi, Kenya'
    Entry 'Junior Web Developer' "Jun 2022 $dash Feb 2024" -Italic
    Bullets @(
        'Built a React Native appointment booking app with about 1,200 monthly active users (mid-2023).',
        'Built React pages for the clinic admin portal.',
        'Added endpoints to a Node.js/Express REST API backed by PostgreSQL, reviewed by the backend developer.',
        'Wrote unit tests with Jest and React Testing Library.'
    )
    Gap
    Entry 'Tano Systems' 'Nairobi, Kenya'
    Entry 'Software Engineering Intern' "Jun 2021 $dash Sep 2021" -Italic
    Bullets @('Fixed accessibility issues in an internal dashboard toward WCAG 2.1 AA (colour contrast, keyboard navigation, form labels).')

    Heading 'PROJECTS'
    Start-Line -Tab; Seg 'Freelance Web Developer' -B; Seg $dot; Seg 'Self-employed, part-time' -I
    Seg (" (Next.js, Tailwind CSS)`tJan 2023 $dash Present"); End-Line
    Bullets @(
        'Built 6 websites for small businesses with Next.js and Tailwind CSS.',
        'Set up deployments on Vercel and basic analytics with Plausible.'
    )
    Gap
    Start-Line -Tab; Seg 'Shamba Prices' -B; Seg $dot; Seg 'Side Project' -I
    Seg " (Next.js, Claude API, PostgreSQL)`t2025"; End-Line
    Bullets @(
        'Built a chat assistant that answers crop price questions in English and Swahili, using the Claude API and a PostgreSQL database of market prices.',
        'About 40 farmers used it during a 2-week pilot with a local cooperative.'
    )

    Heading 'EDUCATION'
    Start-Line; Seg 'Kilima University' -B; End-Line
    Start-Line; Seg 'B.Sc. Computer Science'; End-Line
    Start-Line; Seg ("Nairobi, Kenya" + $dot + "Graduated Dec 2021"); End-Line
    Start-Line; Seg 'Second Class Honours (Upper Division)'

    # Strip the author / last-saved-by names Word copies from the Office account.
    # Word stamps the Office account's name into the file; the repo is public.
    $props = $doc.BuiltInDocumentProperties
    foreach ($name in 'Author', 'Last Author', 'Company', 'Manager') {
        $prop = [System.__ComObject].InvokeMember('Item', 'GetProperty', $null, $props, @($name))
        $value = if ($name -like '*Author') { 'Jane Doe' } else { '' }
        [System.__ComObject].InvokeMember('Value', 'SetProperty', $null, $prop, @($value))
    }
    $doc.RemovePersonalInformation = $true
    # Plain strings: a Join-Path result reaches Word as a wrapped object and SaveAs2 hangs.
    $doc.SaveAs2("$OutDir\resume.docx", 16)
    $doc.SaveAs2("$OutDir\resume.pdf", 17)
    $doc.SaveAs2("$OutDir\resume.doc", 0)
    "pages: " + $doc.ComputeStatistics(2)
    $doc.Close(0)
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}

