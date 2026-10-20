# Status

_Last updated: 2026-10-20 (PawnIO no longer bundled; 1.2.1 ready, not tagged)_

## Live

- **App:** `main` is **1.2.1** (PawnIO unbundled), **not tagged/released yet**; waiting for the owner's OK. Latest release is still v1.2.0 at https://github.com/Ahsuu27488/taskvane/releases/tag/v1.2.0 (installer, portable zip, SHA256SUMS). The tag points at the source the binaries were built from.
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

## Next steps

1. **Google Search Console**: verified 2026-10-16 (URL-prefix property `https://taskvane.ahsandev.site/`, owner's Google account) via `website/public/google07f290b9883c4ddb.html` (keep that file forever). `sitemap-index.xml` submitted. Indexing requested for `/` and `/download/`. **Bing Webmaster Tools**: imported from GSC 2026-10-16, sitemap status Success. Check GSC → Pages in about a week. Possible later improvement: IndexNow ping from `website.yml` on each deploy.
2. **winget**: PR opened 2026-10-16, https://github.com/microsoft/winget-pkgs/pull/453922. CLA accepted by the owner 2026-10-16; validation checks 01–07 passed; waiting for installation validation and a moderator. Once merged, add `winget install Ahsuu27488.Taskvane` to the download page and README.
   **Scoop**: live in https://github.com/Ahsuu27488/scoop-bucket (`scoop bucket add ahsuu27488 …; scoop install ahsuu27488/taskvane`). Test a real install before advertising it on the site. Each release: update `bucket/taskvane.json` there (or rely on `autoupdate` via Scoop's Excavator if it moves to Extras).
   **AlternativeTo** listing text in `docs/launch.md` (owner submits).
3. **Ad reel**: 9:16 Remotion reel in English (Liam voice, 46 s) and Hinglish (Bunty voice, 50 s), with an original ElevenLabs synthwave track. Source is a separate local project `C:\dev\taskvane-reel` (not in this repo; its README covers re-rendering). The MP4s are attached to the v1.2.0 release as `Taskvane-demo-reel-*.mp4` and, compressed (~9 MB), served from the website at `/video/taskvane-demo-{en,hinglish}.mp4` (`website/public/video/`). The README "Demo video" section links to the website copies, because release assets always download instead of playing (posters in `docs/screenshots/reel-*.jpg`). For a future release, re-upload them or update the README links. Posting on Instagram is in the owner's Reminders. The music take wasn't checked for vocals: ElevenLabs credits ran out.
4. Launch posts: drafts for Show HN, r/Windows11, r/pcmasterrace, Product Hunt and awesome lists are in `docs/launch.md` (local only, gitignored, on the owner's PC); the owner posts them.
5. **Code signing (SignPath Foundation)**: requirements met on our side as of 2026-10-17: code signing policy + privacy at `/code-signing/`, linked from the footer (every page), download page and README. Form answers are in local `docs/launch.md`. The owner submits (it creates a SignPath account; CAPTCHA). Weak spot: their "Reputation" field (0 stars, a handful of downloads), so submitting after the launch posts / winget merge is wiser. Needs GitHub 2FA. After approval: change "We're applying" wording to the final credit line and add the SignPath step to `build.yml`.
6. **PawnIO redistribution: resolved by unbundling (1.2.1).** namazso replied 2026-10-17: unmodified redistribution of PawnIO is fine on its own, but bundling it in a GPL-3.0 app breaks GPL-3's Installation Information clause (they hold copyright on a GPL patch in LibreHardwareMonitor); GPL-3 projects like OpenRGB link to pawnio.eu instead. Done on `main`: no PawnIO in fetch_deps/build/installer/zip, "Enable CPU sensors" opens pawnio.eu, site/README/docs updated (DECISIONS.md row). **Owner decisions pending:** (a) tag `v1.2.1` (publishes the release; the website's footer already says 1.2.1, downloads still point at v1.2.0 until then); (b) what to do with the v1.2.0 release assets, which still bundle PawnIO (replace/delete/leave); (c) update winget PR #453922 (points at the v1.2.0 Setup.exe) to 1.2.1; (d) update `bucket/taskvane.json` in Ahsuu27488/scoop-bucket (and `packaging/` manifests here) to 1.2.1. Also reply to namazso (in the owner's Reminders).
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
