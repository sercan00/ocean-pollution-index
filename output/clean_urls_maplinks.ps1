# Updates internal links in map.html to use clean URLs
# Run from: C:\Users\sercan\Desktop\ocean_pollution_project\output

if (Test-Path "map.html") {
    $c = Get-Content "map.html" -Raw
    $c = $c -replace 'href="about\.html"', 'href="about"'
    $c = $c -replace 'href="map\.html"', 'href="map"'
    $c = $c -replace 'href="index\.html"', 'href="/"'
    Set-Content "map.html" $c -NoNewline
    Write-Host "map.html links updated to clean URLs"
} else {
    Write-Host "map.html not found in this folder"
}
