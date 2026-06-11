# Patch script — adds PNG logo to all pages and fixes forecast numbers
# Run from: C:\Users\sercan\Desktop\ocean_pollution_project\output

# 1. Add favicon link to all three HTML files (right after <title>)
$faviconLine = '<link rel="icon" type="image/png" href="pavicon.png">'

foreach ($file in @("index.html", "map.html", "about.html")) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        # Remove any old favicon line first
        $content = $content -replace '<link rel="icon"[^>]*>', ''
        # Add the new one after </title>
        $content = $content -replace '(</title>)', "`$1`n$faviconLine"
        Set-Content $file $content -NoNewline
        Write-Host "Added logo to $file"
    } else {
        Write-Host "WARNING: $file not found"
    }
}

# 2. Fix forecast numbers on the landing page (index.html)
if (Test-Path "index.html") {
    $idx = Get-Content "index.html" -Raw

    # Indian Ocean forecast card (2026, 2030, 2050, 2100)
    $idx = $idx -replace '>37\.9<', '>48.4<'
    $idx = $idx -replace '>42\.6<', '>49.8<'
    $idx = $idx -replace '>77\.1<', '>95.9<'
    $idx = $idx -replace '>338<', '>398<'

    # Findings card scores
    $idx = $idx -replace 'Score: 40\.7', 'Score: 43.2'
    $idx = $idx -replace 'Score: 37\.9', 'Score: 48.4'
    $idx = $idx -replace 'Score: 39\.3', 'Score: 41.6'
    $idx = $idx -replace 'Score: 4\.8', 'Score: 6.4'

    Set-Content "index.html" $idx -NoNewline
    Write-Host "Fixed forecast numbers on index.html"
}

Write-Host ""
Write-Host "DONE! Now drag the output folder to Netlify to deploy."
