# Status

_Last updated: 2026-10-20 (update notifications on main; PawnIO unbundled in 1.2.1)_

## Live

- **App:** v1.2.1, released 2026-10-20 at https://github.com/Ahsuu27488/taskvane/releases/tag/v1.2.1 (installer, portable zip, SHA256SUMS; no PawnIO inside, checked). v1.2.0's installer/zip/SHA256SUMS were removed from its release (they bundled PawnIO; backup in `%USERPROFILE%\taskvane-v1.2.0-assets-backup`); its notes point to 1.2.1 and the demo reels stay attached there.
- **Website:** https://taskvane.ahsandev.site (GitHub Pages, HTTPS enforced, cert valid to 2027-01-13). Cloudflare DNS: `CNAME taskvane → ahsuu27488.github.io`, **DNS only** (grey cloud).
- **CI:** `build.yml` passes on windows-latest (build + smoke test). `website.yml` deploys on changes to `website/**`, `CHANGELOG.md`, `app.py`, and on new releases.
- **GitHub profile:** README rewritten in repo `Ahsuu27488/Ahsuu27488` (renamed from `aboutMe`).

## Verified

- 1.2.1 CPU sensors flow (2026-10-20): with PawnIO reported missing, **Enable CPU sensors** opens https://pawnio.eu/ and shows the explanation toast; once PawnIO appears in the Uninstall registry the banner switches to **Restart as administrator** within ~3 s (watcher thread); that button hands off to the elevated task → 108 sensors incl. CPU temps and package power. (The missing-PawnIO part was tested from source with `pawnio_status` patched, since PawnIO is installed on this PC.)
- "Always start as administrator" (elevated scheduled tasks), sign-in task, and turning both off cleanly.
- Installer lifecycle with the 1.2.1 Setup.exe (2026-10-20): upgrade over 1.2.0 removes the old `_internal\lib\pawnio` → run via task → uninstall while running leaves nothing behind; settings kept on silent uninstall; PawnIO untouched. 1.2.1 Setup/zip contain no PawnIO files (Setup ~3 MB smaller).
- Portable zip keeps all data in `.\data`.
- App cost ≈0.4% CPU total (app + WebView2 + sensor helper).

## Website mobile pass (2026-10-16)

- Phone menu: hamburger button with a drop-down list (was a clipped, sideways-scrolling row).
- Temperature scale: moment labels in two staggered rows on phones (no more "Gaming…"/"Throttling" overlap), compact state badge, wider slider thumb, 2×2 legend.
- Comparison tables (home, /compare/*, docs command table) become one card per row on phones, so the Taskvane column is always visible.
- Download page: buttons say "Download installer" / "Download portable zip"; filename + size shown below.
- Home: new "Also in Taskvane" grid (alerts, mini widget, startup apps, history, portable, privacy); phone-only "Send link to my PC" note (Web Share / copy); app screenshots run off the right edge on phones so they're readable.
- Verified with Playwright captures at 375 px and 1440 px (scripts in the session scratchpad; `website/scripts/shoot.ps1` still covers ≥500 px).

## Update notifications (2026-10-20, on `main`, not released)

- New: daily update check (`App._update_loop` in `app.py`) → `get_stats()["update"]` → Overview banner with What's new / Download / Skip this version / × (hide until restart), and one tray notification per new version. Settings > About > **Check for updates** (default ON). Off = no request.
- Verified from source: a real check stored `latest 1.2.0` and later `1.2.1` (no banner, since we run 1.2.1); faked `latest 9.9.9` → banner rendered; **Skip this version** hid it and saved `skipped`; with the toggle off there was no request in 45 s; turning it on ran the check. App cost 0.32% CPU (30 s, 9 processes).
- Privacy wording updated (README, SECURITY.md, website FAQ, docs, home, code-signing policy, llms.txt).
- **Owner decision:** default ON vs OFF. Note the SignPath privacy template sentence ("will not transfer any information … unless specifically requested by the user"): an on-by-default check may need to become an opt-in prompt (ask once on first run) before applying. Flipping the default is one line (`DEFAULTS["check_updates"]` in `app.py`).
- **Follow-up (after code signing):** optional download-and-install of the update. Not built on purpose (see DECISIONS.md).

## Website guides (2026-10-20, scheduled)

- `/guides/` section: Astro content collection `website/src/content/guides/*.md` (schema in `content.config.ts`), template `pages/guides/[slug].astro` (Article + FAQPage + BreadcrumbList JSON-LD, FAQ, download box, related guides, compare link), index page, `llms.txt` section, `/sitemap.xml` → sitemap index.
- **Scheduled publishing:** a guide is built only once its `published` date has come (`src/lib/guides.ts`); links to not-yet-live guides are unwrapped to plain text after the build (`astro.config.mjs`); the Guides menu link and `llms.txt` section appear once at least one guide is live. `website.yml` rebuilds daily at 05:00 UTC (10:00 PKT) and pings IndexNow (Bing/Yandex) with pages that are new compared with the live sitemap. Test any day with `GUIDES_NOW=2026-10-24 npx astro build` (`C:\dev\taskvane-guides\test_dates.py` checks 4 dates for dead links).
- Schedule: 21 Oct CPU temperature + normal CPU temperature; 24 Oct GPU temperature + battery health; 27 Oct laptop power draw + overheating.
- Written by Gemini 3.8 Flash (High) workers via Foreman from fact sheets taken from the app's code; every claim reviewed and fixed by Claude (each draft had ~1 invented detail). Briefs + scripts: `C:\dev\taskvane-guides` (local).
- Next: guides 7–10 from the owner's SEO brief (alternatives roundup, startup apps, CPU temp while gaming, logging over time); request indexing in Search Console after each batch goes live (optional, Google also reads the sitemap).

## Next steps

1. **Google Search Console**: verified 2026-10-16 (URL-prefix property `https://taskvane.ahsandev.site/`, owner's Google account) via `website/public/google07f290b9883c4ddb.html` (keep that file forever). `sitemap-index.xml` submitted. Indexing requested for `/` and `/download/`. **Bing Webmaster Tools**: imported from GSC 2026-10-16, sitemap status Success. Check GSC → Pages in about a week. Possible later improvement: IndexNow ping from `website.yml` on each deploy. **Check 2026-10-20:** Google read the sitemap (12 pages discovered) but has indexed only `/` (5 impressions, 0 clicks; Page indexing report still processing). Bing read the sitemap; 0 pages indexed, 0 impressions. Re-check ~2026-10-27.
2. **winget**: PR opened 2026-10-16, https://github.com/microsoft/winget-pkgs/pull/453922. CLA accepted by the owner 2026-10-16; validation checks 01–07 passed; waiting for installation validation and a moderator. Once merged, add `winget install Ahsuu27488.Taskvane` to the download page and README.
   **Scoop**: live in https://github.com/Ahsuu27488/scoop-bucket (`scoop bucket add ahsuu27488 …; scoop install ahsuu27488/taskvane`). Test a real install before advertising it on the site. Each release: update `bucket/taskvane.json` there (or rely on `autoupdate` via Scoop's Excavator if it moves to Extras).
   **AlternativeTo** listing text in `docs/launch.md` (owner submits).
3. **Ad reel**: 9:16 Remotion reel in English (Liam voice, 46 s) and Hinglish (Bunty voice, 50 s), with an original ElevenLabs synthwave track. Source is a separate local project `C:\dev\taskvane-reel` (not in this repo; its README covers re-rendering). The MP4s are attached to the v1.2.0 release as `Taskvane-demo-reel-*.mp4` and, compressed (~9 MB), served from the website at `/video/taskvane-demo-{en,hinglish}.mp4` (`website/public/video/`). The README "Demo video" section links to the website copies, because release assets always download instead of playing (posters in `docs/screenshots/reel-*.jpg`). For a future release, re-upload them or update the README links. Posting on Instagram is in the owner's Reminders. The music take wasn't checked for vocals: ElevenLabs credits ran out.
4. Launch posts: drafts for Show HN, r/Windows11, r/pcmasterrace, Product Hunt and awesome lists are in `docs/launch.md` (local only, gitignored, on the owner's PC); the owner posts them.
5. **Code signing (SignPath Foundation)**: requirements met on our side as of 2026-10-17: code signing policy + privacy at `/code-signing/`, linked from the footer (every page), download page and README. Form answers are in local `docs/launch.md`. The owner submits (it creates a SignPath account; CAPTCHA). **Re-checked 2026-10-20 against signpath.org/terms:** no proprietary components now that PawnIO isn't bundled (bundling it would have broken their "No proprietary code" rule too); GitHub 2FA on; release notes now link the code signing policy; stale "sends nothing over the network" lines fixed. Open: the update check is on by default, while their template privacy sentence says nothing is sent unless requested, and data-sending features must be shown at install with an option to turn them off (installer checkbox or opt-in prompt). Weak spot: their "Reputation" field (0 stars, a handful of downloads), so submitting after the launch posts / winget merge is wiser. Needs GitHub 2FA. After approval: change "We're applying" wording to the final credit line and add the SignPath step to `build.yml`.
6. **PawnIO redistribution: resolved (2026-10-20).** namazso said bundling PawnIO in a GPL-3.0 app breaks GPL-3's Installation Information clause; 1.2.1 doesn't bundle it and links to pawnio.eu (DECISIONS.md). Reply sent to namazso 2026-10-20 (same Gmail thread). winget PR #453922 updated to 1.2.1 (manifest validated locally; title/body updated); Scoop bucket updated to 1.2.1; `packaging/` manifests here too. The website needed a manual redeploy after the release (CLAUDE.md trap; `build.yml` now triggers it) and links to v1.2.1.
7. GitHub profile README (repo `Ahsuu27488/Ahsuu27488`) and the site's About page now lead with AI work: Chronos (OpenAI Agents SDK multi-agent, 7 self-written MCP tools, Whisper voice, Qdrant semantic search, SSE/push/email notifications, K8s/Dapr/Kafka) and the Physical AI textbook (RAG over Qdrant, LLM Urdu translation). Claims checked against those repos' code; chronos.ahsandev.site is down, so links use the Vercel URL.
8. Owner to-dos: set GitHub bio (`gh auth refresh -h github.com -s user`, or paste in Settings), pin repos on profile, review About page wording (`website/src/pages/about.astro`).

## Repo hygiene (2026-10-16)

- `.github/` (CI workflows, issue/PR templates) stays public. `.claude/` (settings.json + the two doc hooks) is local only now: untracked and ignored by `/.claude/` (owner's call, 2026-10-16). The files still live on the owner's PC, so the hooks keep working there.
- Personal working notes moved from CLAUDE.md to `CLAUDE.local.md`, and launch drafts to a local-only `docs/launch.md` (both gitignored).
- History rewritten with git-filter-repo (owner approved) to remove the private repo names, the personal notes and `docs/launch.md` from old commits; `main` force-pushed. `v1.2.0` and earlier commits were untouched. A backup bundle of the old history is in `%USERPROFILE%	askvane-pre-rewrite.bundle`.

## Known limitations

- Whole-system power is only available on battery (Windows limitation); on AC only CPU/GPU package power.
- CPU sensors need admin + PawnIO, which users install themselves from pawnio.eu.
- Not code-signed yet → SmartScreen warning on first run.
