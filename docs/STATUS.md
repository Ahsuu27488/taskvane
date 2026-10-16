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

1. **Google Search Console**: verified 2026-10-16 (URL-prefix property `https://taskvane.ahsandev.site/`, owner's Google account) via `website/public/google07f290b9883c4ddb.html` (keep that file forever). `sitemap-index.xml` submitted. Indexing requested for `/` and `/download/`. **Bing Webmaster Tools**: imported from GSC 2026-10-16, sitemap status Success. Check GSC → Pages in about a week. Possible later improvement: IndexNow ping from `website.yml` on each deploy.
2. **winget**: PR opened 2026-10-16, https://github.com/microsoft/winget-pkgs/pull/453922. CLA accepted by the owner 2026-10-16; validation checks 01–07 passed; waiting for installation validation and a moderator. Once merged, add `winget install Ahsuu27488.Taskvane` to the download page and README.
   **Scoop**: live in https://github.com/Ahsuu27488/scoop-bucket (`scoop bucket add ahsuu27488 …; scoop install ahsuu27488/taskvane`). Test a real install before advertising it on the site. Each release: update `bucket/taskvane.json` there (or rely on `autoupdate` via Scoop's Excavator if it moves to Extras).
   **AlternativeTo** listing text in `docs/launch.md` (owner submits).
3. Launch posts: drafts for Show HN, r/Windows11, r/pcmasterrace, Product Hunt and awesome lists are in `docs/launch.md` (local only, gitignored, on the owner's PC); the owner posts them.
4. **Code signing**: apply to SignPath Foundation (free for OSS) to remove the SmartScreen warning.
5. **PawnIO redistribution**: get written OK from namazso (admin@namazso.eu) before wider distribution.
6. GitHub profile README (repo `Ahsuu27488/Ahsuu27488`) and the site's About page now lead with AI work: Chronos (OpenAI Agents SDK multi-agent, 7 self-written MCP tools, Whisper voice, Qdrant semantic search, SSE/push/email notifications, K8s/Dapr/Kafka) and the Physical AI textbook (RAG over Qdrant, LLM Urdu translation). Claims checked against those repos' code; chronos.ahsandev.site is down, so links use the Vercel URL.
7. Owner to-dos: set GitHub bio (`gh auth refresh -h github.com -s user`, or paste in Settings), pin repos on profile, review About page wording (`website/src/pages/about.astro`).

## Repo hygiene (2026-10-16)

- `.github/` (CI workflows, issue/PR templates) stays public. `.claude/` (settings.json + the two doc hooks) is local only now: untracked and ignored by `/.claude/` (owner's call, 2026-10-16). The files still live on the owner's PC, so the hooks keep working there.
- Personal working notes moved from CLAUDE.md to `CLAUDE.local.md`, and launch drafts to a local-only `docs/launch.md` (both gitignored).
- History rewritten with git-filter-repo (owner approved) to remove the private repo names, the personal notes and `docs/launch.md` from old commits; `main` force-pushed. `v1.2.0` and earlier commits were untouched. A backup bundle of the old history is in `%USERPROFILE%	askvane-pre-rewrite.bundle`.

## Known limitations

- Whole-system power is only available on battery (Windows limitation); on AC only CPU/GPU package power.
- CPU sensors need admin + PawnIO.
- Not code-signed yet → SmartScreen warning on first run.
