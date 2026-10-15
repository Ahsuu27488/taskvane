# Dev helper: full-page screenshots of the local site with headless Chrome.
#   powershell -File website\scripts\shoot.ps1 -Path / -Width 1440 -Height 3600 -Out home.png
param([string]$Path = '/', [int]$Width = 1440, [int]$Height = 3600, [string]$Out = 'shot.png', [string]$Base = 'http://localhost:4321')
$chrome = @("$env:ProgramFiles\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
            "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe", "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe") |
          Where-Object { Test-Path $_ } | Select-Object -First 1
$outPath = [IO.Path]::GetFullPath($Out)
$profile = Join-Path $env:TEMP 'taskvane-shoot-profile'
& $chrome --headless=new --disable-gpu --hide-scrollbars --no-first-run --user-data-dir="$profile" `
    --virtual-time-budget=4000 --force-prefers-reduced-motion `
    --window-size="$Width,$Height" --screenshot="$outPath" "$Base$Path" 2>$null | Out-Null
Write-Output $outPath
