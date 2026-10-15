# Downloads the pinned third-party binaries into lib\ and verifies their SHA-256.
# They aren't committed to the repo; build.ps1 and CI run this first.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$root = Split-Path $PSScriptRoot -Parent
$lib = Join-Path $root 'lib'

$deps = @(
    @{ Name = 'LibreHardwareMonitor 0.9.6'
       Url  = 'https://github.com/LibreHardwareMonitor/LibreHardwareMonitor/releases/download/v0.9.6/LibreHardwareMonitor.zip'
       Sha  = '086D9F1B5A99E643EDC2CFAAAC16051685B551E4C5AC0B32A57C58C0E529C001'
       Dest = 'lhm'; Zip = $true
       # The GUI app's own DLLs (plots, tree view, task scheduler) aren't needed by the library.
       Skip = '^(OxyPlot|Aga\.Controls|Microsoft\.Win32\.TaskScheduler)' },
    @{ Name = 'PawnIO setup 2.2.0 (signed by namazso)'
       Url  = 'https://github.com/namazso/PawnIO.Setup/releases/download/2.2.0/PawnIO_setup.exe'
       Sha  = '1F519A22E47187F70A1379A48CA604981C4FCF694F4E65B734AAA74A9FBA3032'
       Dest = 'pawnio'; Zip = $false }
)

foreach ($d in $deps) {
    $dest = Join-Path $lib $d.Dest
    $stamp = Join-Path $dest '.sha256'
    if ((Test-Path $stamp) -and ((Get-Content $stamp -Raw).Trim() -eq $d.Sha)) { Write-Host "ok      $($d.Name)"; continue }

    Write-Host "fetch   $($d.Name)"
    # Expand-Archive (Windows PowerShell 5.1) only accepts a .zip extension
    $tmp = Join-Path ([IO.Path]::GetTempPath()) ("taskvane-" + [IO.Path]::GetRandomFileName() + ".zip")
    Invoke-WebRequest $d.Url -OutFile $tmp -UseBasicParsing
    $hash = (Get-FileHash $tmp -Algorithm SHA256).Hash
    if ($hash -ne $d.Sha) { Remove-Item $tmp; throw "$($d.Name): SHA-256 mismatch (got $hash)" }

    Remove-Item $dest -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Force $dest | Out-Null
    if ($d.Zip) {
        $x = "$tmp-x"
        Expand-Archive $tmp $x
        Get-ChildItem $x -Filter *.dll | Where-Object Name -notmatch $d.Skip | Copy-Item -Destination $dest
        Copy-Item (Join-Path $x 'LibreHardwareMonitor.exe.config') $dest
        Remove-Item $x -Recurse -Force
    } else {
        Copy-Item $tmp (Join-Path $dest (Split-Path $d.Url -Leaf))
    }
    Remove-Item $tmp
    Get-ChildItem $dest | Unblock-File
    Set-Content $stamp $d.Sha
}
