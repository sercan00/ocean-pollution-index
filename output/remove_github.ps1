# Removes all GitHub links/references from index.html and about.html
# Run from: C:\Users\sercan\Desktop\ocean_pollution_project\output

# ===== INDEX.HTML =====
if (Test-Path "index.html") {
    $i = Get-Content "index.html" -Raw
    # Remove the footer "Open source" link
    $i = $i -replace '<p>© 2026 Sercan Emiroglu · <a href="https://github\.com/sercan00/ocean-pollution-index"[^>]*>Open source</a></p>', '<p>© 2026 Sercan Emiroglu</p>'
    # Remove GitHub from footer links list
    $i = $i -replace '<a href="https://github\.com/sercan00/ocean-pollution-index" target="_blank">GitHub</a>', ''
    Set-Content "index.html" $i -NoNewline
    Write-Host "Removed GitHub links from index.html"
}

# ===== ABOUT.HTML =====
if (Test-Path "about.html") {
    $a = Get-Content "about.html" -Raw
    # Remove "Source Code" bio link
    $a = $a -replace '<a href="https://github\.com/sercan00/ocean-pollution-index"[^>]*>Source Code</a>', ''
    # Remove GitHub bio link
    $a = $a -replace '<a href="https://github\.com/sercan00"[^>]*>GitHub</a>', ''
    # Remove footer "Open source on GitHub" link
    $a = $a -replace '· <a href="https://github\.com/sercan00/ocean-pollution-index"[^>]*>Open source on GitHub</a>', ''
    Set-Content "about.html" $a -NoNewline
    Write-Host "Removed GitHub links from about.html"
}

Write-Host ""
Write-Host "Done. LinkedIn link kept. Deploy to Netlify next."
