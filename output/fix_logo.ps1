# Fix logo filename in map.html and about.html to match favicon.png
# Run from: C:\Users\sercan\Desktop\ocean_pollution_project\output

foreach ($file in @("map.html", "about.html")) {
    if (Test-Path $file) {
        $content = Get-Content $file -Raw
        $content = $content -replace 'pavicon\.png', 'favicon.png'
        Set-Content $file $content -NoNewline
        Write-Host "Fixed logo path in $file"
    }
}
Write-Host "Done! Now deploy to Netlify."
