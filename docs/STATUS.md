# Status

_Last updated: 2026-10-16 (website mobile pass, packaging drafts)_

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

## Website mobile pass (2026-10-16)

- Phone menu: hamburger button with a drop-down list (was a clipped, sideways-scrolling row).
- Temperature scale: moment labels in two staggered rows on phones (no more "Gaming…"/"Throttling" overlap), compact state badge, wider slider thumb, 2×2 legend.
- Comparison tables (home, /compare/*, docs command table) become one card per row on phones, so the Taskvane column is always visible.
- Download page: buttons say "Download installer" / "Download portable zip"; filename + size shown below.
- Home: new "Also in Taskvane" grid (alerts, mini widget, startup apps, history, portable, privacy); phone-only "Send link to my PC" note (Web Share / copy); app screenshots run off the right edge on phones so they're readable.
- Verified with Playwright captures at 375 px and 1440 px (scripts in the session scratchpad; `website/scripts/shoot.ps1` still covers ≥500 px).

## Next steps

1. Register the site in **Google Search Console** and **Bing Webmaster Tools** (owner must sign in; verify via DNS TXT in Cloudflare or an HTML file in `website/public/`), then submit `https://taskvane.ahsandev.site/sitemap-index.xml`.
2. Submit to **winget**: manifests are ready and validated in `packaging/winget/1.2.0/` (steps in `packaging/README.md`); needs the owner's OK to open the PR on microsoft/winget-pkgs. **Scoop** manifest in `packaging/scoop/taskvane.json` (own bucket or Extras later). **AlternativeTo** listing text in `docs/launch.md`.
3. Launch posts: drafts for Show HN, r/Windows11, r/pcmasterrace, Product Hunt and awesome lists are in `docs/launch.md`; the owner posts them.
4. **Code signing**: apply to SignPath Foundation (free for OSS) to remove the SmartScreen warning.
5. **PawnIO redistribution**: get written OK from namazso (admin@namazso.eu) before wider distribution.
6. Owner to-dos: set GitHub bio (`gh auth refresh -h github.com -s user`, or paste in Settings), pin repos on profile, review About page wording (`website/src/pages/about.astro`).

## Known limitations

- Whole-system power is only available on battery (Windows limitation); on AC only CPU/GPU package power.
- CPU sensors need admin + PawnIO.
- Not code-signed yet → SmartScreen warning on first run.
