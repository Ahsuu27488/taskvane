# Status

_Last updated: 2026-10-16_

## Live

- **App:** v1.2.0, released at https://github.com/Ahsuu27488/taskvane/releases/tag/v1.2.0 (installer, portable zip, SHA256SUMS). The tag points at the source the binaries were built from.
- **Website:** https://taskvane.ahsandev.site (GitHub Pages, HTTPS enforced, cert valid to 2027-01-13). Cloudflare DNS: `CNAME taskvane → ahsuu27488.github.io`, **DNS only** (grey cloud).
- **CI:** `build.yml` passes on windows-latest (build + smoke test). `website.yml` deploys on changes to `website/**`, `CHANGELOG.md`, `app.py`, and on new releases.
- **GitHub profile:** README rewritten in repo `Ahsuu27488/Ahsuu27488` (renamed from `aboutMe`).

## Verified

- Admin flow end to end: Enable CPU sensors → UAC → elevated relaunch → silent PawnIO install → 108 sensors incl. CPU temps and package power; UI connects in admin mode.
- "Always start as administrator" (elevated scheduled tasks), sign-in task, and turning both off cleanly.
- Installer lifecycle with the released Setup.exe: install → run via task → uninstall while running leaves nothing behind; settings kept on silent uninstall; PawnIO kept.
- Portable zip keeps all data in `.\data`.
- App cost ≈0.4% CPU total (app + WebView2 + sensor helper).

## Next steps

1. Register the site in **Google Search Console** and **Bing Webmaster Tools** (owner must sign in; verify via DNS TXT in Cloudflare or an HTML file in `website/public/`), then submit `https://taskvane.ahsandev.site/sitemap-index.xml`.
2. Submit Taskvane to **winget** (PR to microsoft/winget-pkgs; `wingetcreate` can generate the manifest from the release URL), **AlternativeTo** (as alternative to Task Manager / HWiNFO), Scoop.
3. Launch posts: Reddit (r/Windows11, r/pcmasterrace), Show HN, Product Hunt; PRs to awesome-windows lists.
4. **Code signing**: apply to SignPath Foundation (free for OSS) to remove the SmartScreen warning.
5. **PawnIO redistribution**: get written OK from namazso (admin@namazso.eu) before wider distribution.
6. Owner to-dos: set GitHub bio (`gh auth refresh -h github.com -s user`, or paste in Settings), pin repos on profile, review About page wording (`website/src/pages/about.astro`).

## Known limitations

- Whole-system power is only available on battery (Windows limitation); on AC only CPU/GPU package power.
- CPU sensors need admin + PawnIO.
- Not code-signed yet → SmartScreen warning on first run.
