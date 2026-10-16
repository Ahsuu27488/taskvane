# Package manager manifests

Ready-to-submit manifests for the current release. Update the version, URLs and hashes
(from the release's `SHA256SUMS.txt`) for each new release.

## winget (`winget/1.2.0/`)

Validated with `winget validate --manifest packaging\winget\1.2.0`.

To submit, fork `microsoft/winget-pkgs` and add the three files under
`manifests/a/Ahsuu27488/Taskvane/1.2.0/`, then open a PR. Or let `wingetcreate` do it:

```powershell
winget install wingetcreate
wingetcreate submit --token <GitHub token> packaging\winget\1.2.0
```

Later versions: `wingetcreate update Ahsuu27488.Taskvane --version X.Y.Z --urls <Setup.exe URL> --submit`.

Notes:
- winget installs silently, so the installer's default tasks apply: desktop icon, PawnIO driver and
  "always start as administrator" are on, start-at-sign-in is off.
- New packages from unsigned publishers get extra validation (SmartScreen / Defender scans) in the
  winget-pkgs pipeline; expect a day or two.

## Scoop (`scoop/taskvane.json`)

Uses the portable zip; settings persist across updates in Scoop's `persist\taskvane\data`.
`checkver` + `autoupdate` read new GitHub releases and their `SHA256SUMS.txt`.

Main/extras buckets require a notable project (stars, age). Until then, either:
- PR it to the `ScoopInstaller/Extras` bucket once the repo has some traction, or
- host it in a bucket repo of our own (`Ahsuu27488/scoop-bucket`):
  `scoop bucket add taskvane https://github.com/Ahsuu27488/scoop-bucket && scoop install taskvane`.
