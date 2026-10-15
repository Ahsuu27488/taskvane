# Builds Taskvane.
#   powershell -ExecutionPolicy Bypass -File build.ps1            -> dist\Taskvane\Taskvane.exe
#   powershell -ExecutionPolicy Bypass -File build.ps1 -Release   -> also release\Taskvane-<ver>-Setup.exe
#                                                                    and release\Taskvane-<ver>-Portable.zip
#   add -Shortcuts to create Start menu / desktop shortcuts to the dist build (dev use)
param([switch]$Release, [switch]$Shortcuts)
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

python -m pip install --quiet -r requirements.txt pyinstaller
& (Join-Path $PSScriptRoot 'tools\fetch_deps.ps1')
python tools\make_icon.py
$version = (python tools\make_version_info.py).Trim()
Write-Host "Version $version"

python -m PyInstaller --noconfirm --clean --windowed --name Taskvane `
    --icon assets\icon.ico `
    --version-file build\version_info.txt `
    --add-data "ui;ui" `
    --add-data "assets;assets" `
    --add-data "lib\lhm;lib\lhm" `
    --add-data "lib\pawnio;lib\pawnio" `
    --add-data "THIRD_PARTY_NOTICES.md;." `
    --add-data "taskvane\lhm_host.ps1;taskvane" `
    --collect-submodules webview `
    --hidden-import clr `
    app.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller failed" }

$dist = Join-Path $PSScriptRoot 'dist\Taskvane'
$exe = Join-Path $dist 'Taskvane.exe'
Write-Host "Built $exe"

if ($Release) {
    $rel = Join-Path $PSScriptRoot 'release'
    New-Item -ItemType Directory -Force $rel | Out-Null

    # --- portable zip: same files + a portable.txt marker (settings stay in .\data)
    $stage = Join-Path $env:TEMP "taskvane-portable-$version"
    $root = Join-Path $stage "Taskvane $version Portable"
    Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force $root | Out-Null
    Copy-Item "$dist\*" $root -Recurse
    @"
Taskvane $version - portable

Run Taskvane.exe. Nothing is installed: settings and logs are kept in the "data" folder
next to it. Delete this folder to remove everything.

CPU temperature and CPU power need administrator mode and the PawnIO driver. Click
"Enable CPU sensors" in the app to set both up (one UAC prompt).

If Windows SmartScreen says "Windows protected your PC", click "More info", then "Run anyway".
"@ | Set-Content -Encoding UTF8 (Join-Path $root 'portable.txt')
    $zip = Join-Path $rel "Taskvane-$version-Portable.zip"
    Remove-Item $zip -ErrorAction SilentlyContinue
    Compress-Archive -Path $root -DestinationPath $zip -CompressionLevel Optimal
    Remove-Item $stage -Recurse -Force
    Write-Host "Portable: $zip"

    # --- installer
    $iscc = @("${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe", "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
              "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe") | Where-Object { Test-Path $_ } | Select-Object -First 1
    if (-not $iscc) { throw "Inno Setup 6 not found: winget install JRSoftware.InnoSetup" }
    & $iscc /Q "/DAppVersion=$version" installer\Taskvane.iss
    if ($LASTEXITCODE -ne 0) { throw "Inno Setup failed" }
    Write-Host "Installer: $(Join-Path $rel "Taskvane-$version-Setup.exe")"
}

if ($Shortcuts) {
    $shell = New-Object -ComObject WScript.Shell
    foreach ($dir in @([Environment]::GetFolderPath('Programs'), [Environment]::GetFolderPath('Desktop'))) {
        $lnk = $shell.CreateShortcut((Join-Path $dir 'Taskvane.lnk'))
        $lnk.TargetPath = $exe
        $lnk.WorkingDirectory = Split-Path $exe
        $lnk.IconLocation = "$exe,0"
        $lnk.Description = 'Live CPU, GPU, memory, temperatures and power'
        $lnk.Save()
        Write-Host "Shortcut: $($lnk.FullName)"
    }
}
