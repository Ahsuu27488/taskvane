import { existsSync, readFileSync } from 'node:fs';
import { resolve } from 'node:path';

export const SITE = {
  name: 'Taskvane',
  url: 'https://taskvane.ahsandev.site',
  tagline: 'A better Task Manager for Windows 11',
  description:
    'Taskvane is a free, open-source Task Manager alternative for Windows 11 and 10. See CPU, GPU, memory, disk and network usage plus CPU and GPU temperatures and power draw in watts, in one fast app.',
  repo: 'https://github.com/Ahsuu27488/taskvane',
  author: {
    name: 'Muhammad Ahsan',
    url: 'https://taskvane.ahsandev.site/about/',
    github: 'https://github.com/Ahsuu27488',
    location: 'Nawabshah, Pakistan',
  },
  license: 'GPL-3.0',
};

// Version from app.py, so the site and the app can't disagree.
// app.py is the repo root; builds may run from website/ or from the repo root.
const appPyPath = [resolve(process.cwd(), '..', 'app.py'), resolve(process.cwd(), 'app.py')].find((p) => existsSync(p));
const appPy = appPyPath ? readFileSync(appPyPath, 'utf8') : '';
export const APP_VERSION = /^VERSION = "([\d.]+)"/m.exec(appPy)?.[1] ?? '1.2.0';

export interface Release {
  version: string;
  date: string;
  url: string;
  setup: { name: string; url: string; size: number };
  portable: { name: string; url: string; size: number };
  checksums: string;
}

let cached: Release | undefined;

/** Latest GitHub release, fetched once at build time (falls back to app.py's version). */
export async function getRelease(): Promise<Release> {
  if (cached) return cached;
  const fallback = (v: string): Release => ({
    version: v,
    date: '',
    url: `${SITE.repo}/releases/tag/v${v}`,
    setup: { name: `Taskvane-${v}-Setup.exe`, url: `${SITE.repo}/releases/download/v${v}/Taskvane-${v}-Setup.exe`, size: 0 },
    portable: { name: `Taskvane-${v}-Portable.zip`, url: `${SITE.repo}/releases/download/v${v}/Taskvane-${v}-Portable.zip`, size: 0 },
    checksums: `${SITE.repo}/releases/download/v${v}/SHA256SUMS.txt`,
  });
  try {
    const headers: Record<string, string> = { Accept: 'application/vnd.github+json' };
    if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
    const res = await fetch('https://api.github.com/repos/Ahsuu27488/taskvane/releases/latest', { headers });
    if (!res.ok) throw new Error(String(res.status));
    const r = await res.json();
    const v = String(r.tag_name).replace(/^v/, '');
    const asset = (re: RegExp) => r.assets.find((a: any) => re.test(a.name));
    const s = asset(/Setup\.exe$/), p = asset(/Portable\.zip$/), c = asset(/SHA256SUMS/);
    const base = fallback(v);
    cached = {
      version: v,
      date: String(r.published_at).slice(0, 10),
      url: r.html_url,
      setup: s ? { name: s.name, url: s.browser_download_url, size: s.size } : base.setup,
      portable: p ? { name: p.name, url: p.browser_download_url, size: p.size } : base.portable,
      checksums: c ? c.browser_download_url : base.checksums,
    };
  } catch {
    cached = fallback(APP_VERSION);
  }
  return cached;
}

export const mb = (bytes: number) => (bytes ? `${(bytes / 1048576).toFixed(0)} MB` : '');
