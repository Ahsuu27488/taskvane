# Package manager manifests

Ready-to-submit manifests for the current release. Update the version, URLs and hashes
(from the release's `SHA256SUMS.txt`) for each new release.

## winget (`winget/1.2.1/`)

Validated with `winget validate --manifest packaging\winget\1.2.1` (schema 1.12).
Submitted 2026-10-16: https://github.com/microsoft/winget-pkgs/pull/453922 (the owner accepts the
Microsoft CLA when the bot asks).

To submit, fork `microsoft/winget-pkgs` and add the three files under
`manifests/a/Ahsuu27488/Taskvane/1.2.1/`, then open a PR. Or let `wingetcreate` do it:

```powershell
winget install wingetcreate
wingetcreate submit --token <GitHub token> packaging\winget\1.2.1
```

Later versions: `wingetcreate update Ahsuu27488.Taskvane --version X.Y.Z --urls <Setup.exe URL> --submit`.

Notes:
- winget installs silently, so the installer's default tasks apply: desktop icon and
  "always start as administrator" are on, start-at-sign-in is off. PawnIO isn't bundled (since 1.2.1).
- New packages from unsigned publishers get extra validation (SmartScreen / Defender scans) in the
  winget-pkgs pipeline; expect a day or two.

## Scoop (`scoop/taskvane.json`)

Uses the portable zip; settings persist across updates in Scoop's `persist\taskvane\data`.
`checkver` + `autoupdate` read new GitHub releases and their `SHA256SUMS.txt`.

Published in our own bucket, https://github.com/Ahsuu27488/scoop-bucket (copy the manifest to
`bucket/taskvane.json` there on each release):

```powershell
scoop bucket add ahsuu27488 https://github.com/Ahsuu27488/scoop-bucket
scoop install ahsuu27488/taskvane
```

Later, once the repo has some traction, PR it to `ScoopInstaller/Extras`. Not yet tested with a real
`scoop install` (schema-validated; hash and zip layout checked against the release).
