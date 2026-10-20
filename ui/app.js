'use strict';
const $ = id => document.getElementById(id);
const $$ = (sel, root = document) => [...root.querySelectorAll(sel)];
const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
let api;

// ---------------------------------------------------------------- state
let S = null, H = null, procs = [], settings = {}, page = 'overview', perfDev = 'cpu';
const ranges = { ov: 300, perf: 60, pw: 300 };

// ---------------------------------------------------------------- formatting
const fmtB = (b, suf = '') => {
  if (b == null || isNaN(b)) return '–';
  const u = ['B', 'KB', 'MB', 'GB', 'TB']; let i = 0;
  while (Math.abs(b) >= 1024 && i < 4) { b /= 1024; i++; }
  return (i === 0 ? Math.round(b) : b.toFixed(b < 10 ? 1 : 0)) + ' ' + u[i] + suf;
};
const fmtRate = b => fmtB(b, '/s');
const pct = v => v == null ? '–' : v.toFixed(v < 10 && v > 0 ? 1 : 0) + '%';
const fmtW = w => w == null ? '–' : w.toFixed(1) + ' W';
const fmtDur = s => { if (s == null) return '–'; s = Math.floor(s); const d = Math.floor(s / 86400), h = Math.floor(s % 86400 / 3600), m = Math.floor(s % 3600 / 60); return (d ? d + 'd ' : '') + (d || h ? h + 'h ' : '') + m + 'm'; };
const toUnit = c => settings.unit === 'F' ? c * 9 / 5 + 32 : c;
const fmtT = c => c == null ? '–' : Math.round(toUnit(c)) + (settings.unit === 'F' ? ' °F' : ' °C');
const big = (v, unit) => `${v}<small>${unit}</small>`;

function tempStatus(c, hot = 85) {
  if (c == null) return null;
  if (c >= hot + 10) return { k: 'critical', l: 'Critical' };
  if (c >= hot) return { k: 'serious', l: 'Hot' };
  if (c >= hot - 15) return { k: 'warning', l: 'Warm' };
  return { k: 'good', l: 'Normal' };
}
const statusPill = s => s ? `<span class="status"><span class="dot" style="background:var(--${s.k})"></span>${s.l}</span>` : '';
const meter = (p, color) => `<div class="meter"><i style="width:${Math.max(0, Math.min(100, p || 0))}%;background:${color}"></i></div>`;
const row = (k, v, extra = '') => `<div class="r"><span class="k" title="${esc(k)}">${esc(k)}</span><span class="v">${v}</span>${extra}</div>`;

function toast(msg, ms = 3200) { const t = $('toast'); t.textContent = msg; t.classList.add('show'); clearTimeout(t._h); t._h = setTimeout(() => t.classList.remove('show'), ms); }

// ---------------------------------------------------------------- navigation
function go(p) {
  page = p;
  $$('nav a').forEach(a => a.classList.toggle('active', a.dataset.page === p));
  $$('.page').forEach(s => s.classList.toggle('active', s.id === 'p-' + p));
  if (p === 'startup') loadStartup();
  if (p === 'processes') loadProcs();
  if (p === 'sensors') loadSensors();
  render();
}
$$('nav a').forEach(a => a.onclick = () => go(a.dataset.page));
$$('[data-goto]').forEach(el => el.onclick = () => { if (el.dataset.goto === 'power') return go('power'); perfDev = el.dataset.goto; go('performance'); });

$$('.seg[data-range]').forEach(seg => seg.onclick = e => {
  const b = e.target.closest('button'); if (!b) return;
  $$('button', seg).forEach(x => x.classList.toggle('on', x === b));
  ranges[seg.dataset.range] = +b.dataset.s; refresh();
});

// ---------------------------------------------------------------- charts
const fmtPct = v => Math.round(v) + '%';
const ovChart = new TimeChart($('ovChart'), { max: 100, fmt: fmtPct, area: false, series: [
  { key: 'cpu', label: 'CPU', color: css('--c-cpu') }, { key: 'mem', label: 'Memory', color: css('--c-mem') }, { key: 'gpu', label: 'GPU', color: css('--c-gpu') }] });
const noPowerText = () => S?.admin
  ? 'No power sensor is reporting.\nWhole-system draw is measured at the battery while unplugged.'
  : 'Plugged in: Windows doesn\'t report whole-system power on AC.\nUnplug to measure it from the battery, or restart as administrator for CPU package power.';
const pwChart = new TimeChart($('pwChart'), { fmt: v => v.toFixed(1) + ' W', emptyMax: 40, emptyText: noPowerText, series: [{ key: 'power', label: 'Power', color: css('--c-pwr') }] });
let pfChart = null, pfChartKey = null;

// ---------------------------------------------------------------- polling
let refreshing = false;
async function refresh() {
  if (refreshing) return;  // never stack calls if Python is slow to answer
  refreshing = true;
  try {
    const span = Math.max(60, page === 'overview' ? ranges.ov : page === 'performance' ? ranges.perf : page === 'power' ? ranges.pw : 60);
    [S, H] = await Promise.all([api.get_stats(), api.get_history(span)]);
    render();
  } catch (e) { console.error(e); }
  finally { refreshing = false; }
}

function render() {
  if (!S || !S.system || S.system.cpu == null) return;
  renderChrome();
  if (page === 'overview') renderOverview();
  if (page === 'performance') renderPerf();
  if (page === 'power') renderPower();
}

function sliceH(seconds) {
  if (!H || !H.t.length) return { t: [], d: H || {} };
  const cutoff = H.t[H.t.length - 1] - seconds;
  const i = H.t.findIndex(t => t >= cutoff);
  const d = {}; for (const k in H) d[k] = H[k].slice(i);
  return { t: d.t, d };
}

const gpus = () => S.hw.gpus || [];
const partsLabel = () => (S.hw.power_parts || []).join(' + ') + ' package' + ((S.hw.power_parts || []).length > 1 ? 's' : '');
const cpuGHz = () => { const c = (S.hw.core_clocks || []).filter(x => x > 0); return c.length ? c.reduce((a, b) => a + b, 0) / c.length / 1000 : (S.system.freq ? S.system.freq / 1000 : null); };
const mainGpu = () => gpus().find(g => g.discrete) || gpus()[0];

function renderChrome() {
  $('adminBadge').innerHTML = S.admin
    ? `<span class="dot" style="background:var(--good)"></span>Administrator mode`
    : `<span class="dot" style="background:var(--text-3)"></span>Standard mode`;
  const st = cpuSensorState();
  $('adminBanner').hidden = !st;
  if (st) setHTML($('adminBanner'), st);
  const up = updateState();
  $('updateBanner').hidden = !up;
  if (up) setHTML($('updateBanner'), up);
}

// A newer release found by the daily check (Python side). Notify only: the user downloads it.
let updateDismissed = null;  // hidden for this session with ×; "Skip this version" persists
function updateState() {
  const u = S.update;
  if (!u || u.version === updateDismissed) return null;
  return `<div class="grow"><b>Taskvane ${esc(u.version)} is available.</b> <span class="hint">You have ${esc(S.version)}. Installed with winget or Scoop? Run <code>winget upgrade Ahsuu27488.Taskvane</code> or <code>scoop update taskvane</code> instead.</span></div>
    <button class="btn" data-url="${esc(u.url)}">What's new</button><button class="btn primary" data-url="https://taskvane.ahsandev.site/download/">Download</button>
    <button class="btn" data-act="skipUpdate">Skip this version</button><button class="btn icon" data-act="dismissUpdate" title="Hide until next start" aria-label="Hide">×</button>`;
}

// Only touch the DOM when content changes, so buttons inside stay clickable.
function setHTML(el, html) { if (el._html !== html) { el._html = html; el.innerHTML = html; } }

// What's blocking CPU temperature / CPU power, and the one action that fixes it.
function cpuSensorState() {
  const pw = S.pawnio || {}, bannerBtn = (label, act) => `<button class="btn primary" data-act="${act}">${label}</button>`;
  if (!S.lhm.ok) return `<div class="grow"><b>The sensor engine couldn't start.</b> <span class="hint">${esc(S.lhm.error)}</span></div><button class="btn" data-act="openLog">Open log</button>`;
  if (S.hw.cpu_temp != null) return null;                       // all good
  if (!S.lhm.count) return null;                                // helper still warming up
  if (!pw.installed || pw.outdated)
    return `<div class="grow"><b>${pw.outdated ? 'CPU sensors need a newer PawnIO driver.' : 'CPU temperature and CPU power are off.'}</b> <span class="hint">They need the free, signed PawnIO driver. ${pw.outdated ? 'Update' : 'Install'} it from its author's site (pawnio.eu), then restart Taskvane as administrator.</span></div>${bannerBtn(pw.outdated ? 'Update PawnIO' : 'Enable CPU sensors', 'cpuSensors')}`;
  if (!S.admin)
    return `<div class="grow"><b>CPU temperature and CPU power need administrator mode.</b> <span class="hint">The PawnIO driver is installed; Windows only lets elevated apps use it.</span></div>${bannerBtn('Restart as administrator', 'admin')}`;
  return `<div class="grow"><b>CPU sensors aren't reporting.</b> <span class="hint">Running as administrator with PawnIO ${esc(pw.version || '')} installed, but no CPU readings yet. If this persists, restart Windows.</span></div><button class="btn" data-act="openLog">Open log</button>`;
}

// ---------------------------------------------------------------- overview
function renderOverview() {
  const s = S.system, hw = S.hw, g = mainGpu(), b = hw.battery;
  $('ovSub').textContent = s.cpu_name;
  $('ovUptime').textContent = 'Up ' + fmtDur(Date.now() / 1000 - s.boot);
  const h60 = sliceH(60).d;

  // CPU
  $('tCpu').innerHTML = big(Math.round(s.cpu), '%');
  $('tCpuR').textContent = hw.cpu_temp != null ? fmtT(hw.cpu_temp) : (cpuGHz() ? cpuGHz().toFixed(2) + ' GHz' : '');
  $('tCpuD').textContent = `${s.physical} cores · ${s.logical} threads · ${s.procs} processes`;
  sparkline($('sCpu'), h60.cpu || [], css('--c-cpu'), 100);
  // Memory
  $('tMem').innerHTML = big((s.mem.used / 2 ** 30).toFixed(1), 'GB');
  $('tMemR').textContent = pct(s.mem.percent);
  $('tMemD').textContent = `of ${fmtB(s.mem.total)} · ${fmtB(s.mem.available)} available`;
  sparkline($('sMem'), h60.mem || [], css('--c-mem'), 100);
  // GPU
  if (g) {
    $('tGpu').innerHTML = big(Math.round(g.load ?? 0), '%');
    $('tGpuR').textContent = g.temp != null ? fmtT(g.temp) : '';
    $('tGpuD').textContent = g.name.replace(/^NVIDIA GeForce |^AMD Radeon |^Intel\(R\) /, '') + (g.mem_total ? ` · ${(g.mem_used / 1024).toFixed(1)} / ${(g.mem_total / 1024).toFixed(1)} GB` : '');
    sparkline($('sGpu'), h60.gpu || [], css('--c-gpu'), 100);
  } else { $('tGpu').textContent = '–'; $('tGpuD').textContent = 'No GPU sensors'; }
  // Power
  if (hw.power_w != null) {
    $('tPwr').innerHTML = big(hw.power_w.toFixed(1), 'W');
    $('tPwrD').textContent = hw.power_src === 'battery' ? 'Whole system, from battery' : partsLabel();
  } else {
    $('tPwr').textContent = '–';
    $('tPwrD').textContent = b?.plugged ? 'Plugged in: unplug or run as admin' : 'No power sensors';
  }
  $('tPwrR').textContent = b?.percent != null ? `${b.plugged ? 'Plugged in' : 'Battery'} ${Math.round(b.percent)}%` : '';
  sparkline($('sPwr'), h60.power || [], css('--c-pwr'));

  // activity chart
  const r = sliceH(ranges.ov); ovChart.set(r.t, r.d, ranges.ov);

  // temperatures
  const temps = collectTemps();
  $('ovTemps').innerHTML = temps.length ? temps.slice(0, 6).map(t => row(t.label, `${statusPill(tempStatus(t.c, t.hot))}${fmtT(t.c)}`, meter(t.c, css('--' + tempStatus(t.c, t.hot).k)))).join('')
    : `<div class="empty">No temperature sensors found.</div>`;
  $('tempMeta').textContent = temps.length ? 'hottest ' + fmtT(Math.max(...temps.map(t => t.c))) : '';

  // power card
  const pr = [];
  if (b) {
    pr.push(row('Battery', `${Math.round(b.percent ?? 0)}%`, meter(b.percent, b.percent < 20 ? css('--critical') : css('--good'))));
    if (b.discharge_w) pr.push(row('Time left at this rate', b.remaining_wh ? fmtDur(b.remaining_wh / b.discharge_w * 3600) : fmtDur(b.secs_left)));
    if (b.charge_w) pr.push(row('Charging at', fmtW(b.charge_w)));
    if (b.health) pr.push(row('Battery health', pct(b.health)));
  }
  if (hw.cpu_power) pr.push(row('CPU package', fmtW(hw.cpu_power)));
  if (S.session_wh > 0.005) pr.push(row('Used on battery this session', S.session_wh.toFixed(2) + ' Wh'));
  $('ovPower').innerHTML = pr.join('') || '<div class="empty">No battery.</div>';
  $('ovPwrMeta').textContent = b ? (b.plugged ? 'Plugged in' : 'On battery') : '';

  renderInsights(temps);
  renderTop();
}

function collectTemps() {
  const hw = S.hw, t = [];
  if (hw.cpu_temp != null) t.push({ label: 'CPU', c: hw.cpu_temp, hot: 85 });
  gpus().forEach(g => {
    const short = g.name.replace(/^NVIDIA GeForce |^AMD Radeon |^Intel\(R\) /, '');
    if (g.temp != null) t.push({ label: `GPU · ${short}`, c: g.temp, hot: 83 });
    if (g.hotspot != null) t.push({ label: `GPU hot spot · ${short}`, c: g.hotspot, hot: 95 });
  });
  (hw.storage || []).forEach(d => t.push({ label: d.name, c: d.temp, hot: 60 }));
  return t.sort((a, b) => b.c - a.c);
}

function renderInsights(temps) {
  const out = [], s = S.system, b = S.hw.battery;
  const groups = groupProcs(procs).sort((a, b) => b.mem - a.mem);
  if (groups[0]) out.push(`<b>${esc(groups[0].name)}</b> uses the most memory: ${fmtB(groups[0].mem)}${groups[0].children.length > 1 ? ` across ${groups[0].children.length} processes` : ''}`);
  const hot = temps.find(t => tempStatus(t.c, t.hot).k !== 'good');
  if (hot) out.push(`<span class="dot" style="background:var(--${tempStatus(hot.c, hot.hot).k})"></span><b>${esc(hot.label)}</b> is ${tempStatus(hot.c, hot.hot).l.toLowerCase()} at ${fmtT(hot.c)}`);
  if (b?.health && b.health < 80) out.push(`<span class="dot" style="background:var(--warning)"></span>Battery holds <b>${pct(b.health)}</b> of its design capacity`);
  if (s.mem.percent > 85) out.push(`<span class="dot" style="background:var(--warning)"></span>Memory is <b>${pct(s.mem.percent)}</b> full`);
  const full = (s.drives || []).find(d => d.percent > 90);
  if (full) out.push(`<span class="dot" style="background:var(--warning)"></span>Drive <b>${esc(full.mount)}</b> has only ${fmtB(full.free)} free`);
  $('insights').innerHTML = out.map(x => `<div class="insight">${x}</div>`).join('');
}

let topBy = 'cpu';
$('topBy').onclick = e => { const b = e.target.closest('button'); if (!b) return; topBy = b.dataset.k; $$('#topBy button').forEach(x => x.classList.toggle('on', x === b)); renderTop(); };
function renderTop() {
  const g = groupProcs(procs).filter(x => x.name !== 'System Idle Process').sort((a, b) => b[topBy] - a[topBy]).slice(0, 6);
  const max = Math.max(1e-9, ...g.map(x => x[topBy]));
  const fmt = topBy === 'cpu' ? pct : topBy === 'mem' ? fmtB : fmtRate;
  const color = topBy === 'cpu' ? css('--c-cpu') : topBy === 'mem' ? css('--c-mem') : css('--c-disk');
  $('ovTop').innerHTML = g.map(x => row(x.name, fmt(x[topBy]), meter(x[topBy] / max * 100, color))
    .replace('</span><span class="v">', `${x.children.length > 1 ? ` <span class="count">${x.children.length}</span>` : ''}</span><span class="v">`)).join('') || '<div class="empty">Loading…</div>';
}

// ---------------------------------------------------------------- performance
function devList() {
  const s = S.system, hw = S.hw, list = [];
  list.push({ id: 'cpu', name: 'CPU', sub: `${pct(s.cpu)}  ${cpuGHz() ? cpuGHz().toFixed(2) + ' GHz' : ''}${hw.cpu_temp != null ? '  ' + fmtT(hw.cpu_temp) : ''}`, key: 'cpu', color: css('--c-cpu'), max: 100 });
  list.push({ id: 'mem', name: 'Memory', sub: `${(s.mem.used / 2 ** 30).toFixed(1)}/${(s.mem.total / 2 ** 30).toFixed(1)} GB (${pct(s.mem.percent)})`, key: 'mem', color: css('--c-mem'), max: 100 });
  gpus().forEach((g, i) => list.push({ id: 'gpu' + i, name: 'GPU ' + i, sub: `${g.name.replace(/^NVIDIA GeForce |^Intel\(R\) /, '')}  ${pct(g.load)}${g.temp != null ? '  ' + fmtT(g.temp) : ''}`, key: 'gpu' + i, color: css('--c-gpu'), max: 100, gpu: g }));
  list.push({ id: 'disk', name: 'Disk', sub: `R ${fmtRate(s.disk_r)}  W ${fmtRate(s.disk_w)}`, key: 'disk_r', key2: 'disk_w', color: css('--c-disk') });
  list.push({ id: 'net', name: 'Network', sub: `↓ ${fmtRate(s.net_down)}  ↑ ${fmtRate(s.net_up)}`, key: 'net_down', key2: 'net_up', color: css('--c-net') });
  if (hw.power_w != null || hw.battery) list.push({ id: 'power', name: 'Power', sub: hw.power_w != null ? fmtW(hw.power_w) : 'Plugged in', key: 'power', color: css('--c-pwr') });
  return list;
}

function renderPerf() {
  const list = devList(), h60 = sliceH(60).d;
  if (!list.find(d => d.id === perfDev)) perfDev = 'cpu';
  const host = $('devices');
  if (host.dataset.ids !== list.map(d => d.id).join()) {
    host.dataset.ids = list.map(d => d.id).join();
    host.innerHTML = list.map(d => `<div class="dev" data-id="${d.id}"><canvas></canvas><div style="min-width:0"><div class="n"></div><div class="d"></div></div></div>`).join('');
    $$('.dev', host).forEach(el => el.onclick = () => { perfDev = el.dataset.id; renderPerf(); });
  }
  list.forEach(d => {
    const el = host.querySelector(`[data-id="${d.id}"]`);
    el.classList.toggle('active', d.id === perfDev);
    el.querySelector('.n').textContent = d.name;
    el.querySelector('.d').textContent = d.sub;
    const series = d.key ? h60[d.key] || [] : [];
    sparkline(el.querySelector('canvas'), d.key2 ? series.map((v, i) => (v || 0) + (h60[d.key2][i] || 0)) : series, d.color, d.max);
  });

  const d = list.find(x => x.id === perfDev), s = S.system, hw = S.hw;
  const cfg = perfConfig(d);
  if (pfChartKey !== perfDev) {
    if (pfChart) pfChart.destroy();
    pfChart = new TimeChart($('pfChart'), cfg.chart);
    pfChartKey = perfDev;
    $('pfLegend').innerHTML = cfg.chart.series.length > 1 ? cfg.chart.series.map(x => `<span><i style="background:${x.color}"></i>${x.label}</span>`).join('') : '';
  }
  const r = sliceH(ranges.perf); pfChart.set(r.t, r.d, ranges.perf);
  $('pfTitle').textContent = cfg.title; $('pfSub').textContent = cfg.sub;
  $('pfStats').innerHTML = cfg.stats.map(([k, v]) => `<div><label>${esc(k)}</label><b title="${esc(v)}">${esc(v)}</b></div>`).join('');
  $('pfExtraCard').hidden = !cfg.extra;
  if (cfg.extra) {
    $('pfExtraTitle').textContent = cfg.extraTitle;
    const ex = $('pfExtra');
    if (ex._last !== cfg.extra) {
      ex._last = cfg.extra;
      ex.querySelector('#gpuTempChart')?._chart?.destroy();
      ex.innerHTML = cfg.extra;
    }
  }
}

function perfConfig(d) {
  const s = S.system, hw = S.hw;
  const pctChart = (key, label, color) => ({ max: 100, fmt: fmtPct, series: [{ key, label, color }] });
  const hist = k => (sliceH(ranges.perf).d[k] || []).filter(v => v != null);
  const avg = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
  const peak = a => a.length ? Math.max(...a) : null;
  switch (d.id) {
    case 'cpu': {
      const temps = hw.core_temps || [], clocks = hw.core_clocks || [];
      return {
        title: 'CPU', sub: s.cpu_name, chart: pctChart('cpu', 'CPU', css('--c-cpu')),
        stats: [['Utilization', pct(s.cpu)], ['Average', pct(avg(hist('cpu')))], ['Peak', pct(peak(hist('cpu')))],
          ['Speed', cpuGHz() ? cpuGHz().toFixed(2) + ' GHz' : '–'], ['Base speed', s.freq_max ? (s.freq_max / 1000).toFixed(2) + ' GHz' : '–'],
          ['Temperature', fmtT(hw.cpu_temp)], ['Package power', fmtW(hw.cpu_power)],
          ['Cores', s.physical], ['Logical processors', s.logical], ['Processes', s.procs]],
        extraTitle: 'Logical processors',
        extra: `<div class="cores">${s.cores.map((v, i) => {
          const core = Math.floor(i / (s.logical / s.physical));
          const extra = [temps[core] != null ? fmtT(temps[core]) : null, clocks[core] ? (clocks[core] / 1000).toFixed(2) + ' GHz' : null].filter(Boolean).join(' · ');
          return `<div class="core"><div class="fill" style="height:${v}%"></div><span>CPU ${i}</span><b>${Math.round(v)}%</b>${extra ? `<span>${extra}</span>` : ''}</div>`;
        }).join('')}</div>`,
      };
    }
    case 'mem':
      return {
        title: 'Memory', sub: fmtB(s.mem.total) + ' installed', chart: pctChart('mem', 'Memory', css('--c-mem')),
        stats: [['In use', fmtB(s.mem.used)], ['Available', fmtB(s.mem.available)], ['Usage', pct(s.mem.percent)], ['Peak usage', pct(peak(hist('mem')))],
          ['Page file used', fmtB(s.swap.used)], ['Page file size', fmtB(s.swap.total)]],
        extraTitle: 'Biggest memory users',
        extra: `<div class="toplist">${groupProcs(procs).sort((a, b) => b.mem - a.mem).slice(0, 8).map(x => row(x.name, fmtB(x.mem), meter(x.mem / s.mem.total * 100 * 4, css('--c-mem')))).join('')}</div>`,
      };
    case 'disk': {
      const drives = s.drives || [];
      return {
        title: 'Disk', sub: drives.map(x => x.mount).join('  '),
        chart: { fmt: v => fmtRate(v), series: [{ key: 'disk_r', label: 'Read', color: css('--s1') }, { key: 'disk_w', label: 'Write', color: css('--s2') }], area: false },
        stats: [['Read', fmtRate(s.disk_r)], ['Write', fmtRate(s.disk_w)], ['Peak read', fmtRate(peak(hist('disk_r')))], ['Peak write', fmtRate(peak(hist('disk_w')))],
          ...(hw.storage || []).map(x => [x.name, fmtT(x.temp)])],
        extraTitle: 'Drives',
        extra: `<div class="rows">${drives.map(x => row(`${x.mount}  ${x.fs}`, `${fmtB(x.free)} free of ${fmtB(x.total)}`, meter(x.percent, x.percent > 90 ? css('--critical') : css('--c-disk')))).join('')}</div>`,
      };
    }
    case 'net':
      return {
        title: 'Network', sub: 'All adapters',
        chart: { fmt: v => fmtRate(v), series: [{ key: 'net_down', label: 'Download', color: css('--s1') }, { key: 'net_up', label: 'Upload', color: css('--s2') }], area: false },
        stats: [['Download', fmtRate(s.net_down)], ['Upload', fmtRate(s.net_up)], ['Peak download', fmtRate(peak(hist('net_down')))], ['Peak upload', fmtRate(peak(hist('net_up')))],
          ['Received since boot', fmtB(s.net_total.recv)], ['Sent since boot', fmtB(s.net_total.sent)]],
      };
    case 'power': {
      const b = hw.battery || {};
      return {
        title: 'Power', sub: hw.power_src === 'battery' ? 'Whole-system draw measured at the battery' : partsLabel() + ' (whole system needs battery power)',
        chart: { fmt: v => v.toFixed(1) + ' W', emptyMax: 40, emptyText: noPowerText, series: [{ key: 'power', label: 'Power', color: css('--c-pwr') }] },
        stats: [['Now', fmtW(hw.power_w)], ['Average', fmtW(avg(hist('power')))], ['Peak', fmtW(peak(hist('power')))], ['CPU package', fmtW(hw.cpu_power)],
          ['Battery', b.percent != null ? pct(b.percent) : '–'], ['Session energy', S.session_wh.toFixed(2) + ' Wh']],
      };
    }
    default: { // gpu
      const g = d.gpu, hasTemp = g.temp != null;
      return {
        title: g.name, sub: (g.discrete ? 'Dedicated GPU' : 'Integrated GPU') + ' · ' + g.load_label + ' utilization',
        chart: pctChart(d.key, g.load_label, css('--c-gpu')),
        stats: [['Utilization', pct(g.load)], ['Temperature', fmtT(g.temp)], ['Hot spot', fmtT(g.hotspot)], ['Core clock', g.clock ? Math.round(g.clock) + ' MHz' : '–'],
          [g.shared_mem ? 'Shared memory' : 'Video memory', g.mem_total ? `${fmtB(g.mem_used * 2 ** 20)} / ${fmtB(g.mem_total * 2 ** 20)}` : '–'], ['Power', fmtW(g.power)]],
        extraTitle: hasTemp ? 'Temperature' : null,
        extra: hasTemp && g === mainGpu() ? `<div class="chart" id="gpuTempChart" style="height:140px"></div>` : null,
      };
    }
  }
}
// GPU temp mini-chart lives in the extra card; refresh after each perf render
const _renderPerf = renderPerf;
renderPerf = function () {
  _renderPerf();
  const host = $('gpuTempChart');
  if (host) {
    if (!host._chart) host._chart = new TimeChart(host, { fmt: v => fmtT(v), min: 20, series: [{ key: 'gpu_temp', label: 'GPU temp', color: css('--c-gpu') }], area: false });
    const r = sliceH(ranges.perf); host._chart.set(r.t, r.d, ranges.perf);
  }
};

// ---------------------------------------------------------------- power page
function renderPower() {
  const hw = S.hw, b = hw.battery;
  const tiles = [
    ['Power draw', hw.power_w != null ? big(hw.power_w.toFixed(1), 'W') : '–', hw.power_src === 'battery' ? 'Whole system' : hw.power_src ? partsLabel() : (b?.plugged ? 'Unplug to measure the whole system' : 'No sensor'), 'var(--c-pwr)'],
    ['Battery', b?.percent != null ? big(Math.round(b.percent), '%') : '–', b ? (b.plugged ? (b.charge_w ? `Charging at ${fmtW(b.charge_w)}` : 'Plugged in') : 'On battery') : 'No battery', 'var(--good)'],
    ['Time remaining', b?.discharge_w && b.remaining_wh ? fmtDur(b.remaining_wh / b.discharge_w * 3600) : (b?.secs_left ? fmtDur(b.secs_left) : '–'), 'At the current draw', 'var(--c-cpu)'],
    ['Battery health', b?.health ? big(Math.round(b.health), '%') : '–', b?.full_wh ? `${b.full_wh.toFixed(1)} of ${b.design_wh.toFixed(1)} Wh design` : '', 'var(--c-disk)'],
  ];
  $('pwTiles').innerHTML = tiles.map(([l, v, d, c]) => `<div class="card tile"><div class="label"><span class="sw" style="background:${c}"></span>${l}</div><div class="value">${v}</div><div class="detail">${esc(d)}</div></div>`).join('');
  const r = sliceH(ranges.pw); pwChart.set(r.t, r.d, ranges.pw);
  $('pwSrc').textContent = hw.power_src === 'battery' ? 'measured at the battery' : hw.power_src === 'components' ? partsLabel() : '';
  if (b) {
    $('batName').textContent = b.name || '';
    $('pwBattery').innerHTML = [
      row('Charge', b.remaining_wh ? `${b.remaining_wh.toFixed(1)} Wh · ${Math.round(b.percent)}%` : pct(b.percent), meter(b.percent, b.percent < 20 ? css('--critical') : css('--good'))),
      b.health ? row('Capacity vs design', `${b.full_wh.toFixed(1)} / ${b.design_wh.toFixed(1)} Wh`, meter(b.health, css('--c-disk'))) : '',
      b.wear != null ? row('Wear', pct(b.wear)) : '',
      b.discharge_w ? row('Discharge rate', fmtW(b.discharge_w)) : '',
      b.charge_w ? row('Charge rate', fmtW(b.charge_w)) : '',
      b.voltage ? row('Voltage', b.voltage.toFixed(2) + ' V') : '',
      row('Used on battery this session', S.session_wh.toFixed(2) + ' Wh'),
    ].join('');
  } else $('pwBattery').innerHTML = '<div class="empty">No battery detected.</div>';
}

// ---------------------------------------------------------------- processes
let prView = 'apps', sortK = 'cpu', sortDir = -1, selected = null, expanded = new Set();

let loadingProcs = false;
async function loadProcs() {
  if (loadingProcs) return;
  loadingProcs = true;
  try { procs = await api.get_processes(); } catch { return; } finally { loadingProcs = false; }
  if (page === 'processes') renderProcs();
}

function groupProcs(list) {
  const m = new Map();
  for (const p of list) {
    if (p.pid === 0) continue;
    const key = p.desc || p.name.replace(/\.exe$/i, '');
    let g = m.get(key);
    if (!g) m.set(key, g = { key, name: key, exe: p.exe, user: p.user, cpu: 0, mem: 0, io_rate: 0, threads: 0, children: [] });
    g.cpu += p.cpu; g.mem += p.mem; g.io_rate += p.io_rate; g.threads += p.threads; g.children.push(p);
    if (g.user !== p.user) g.user = '';
  }
  for (const g of m.values()) g.pid = g.children.length === 1 ? g.children[0].pid : null;
  return [...m.values()];
}

function cmp(a, b) {
  const x = a[sortK], y = b[sortK];
  return (typeof x === 'string' || typeof y === 'string' ? String(x ?? '').localeCompare(String(y ?? '')) : (x ?? -1) - (y ?? -1)) * sortDir;
}

function heat(v, max, rgb) {
  const a = Math.min(1, v / max) * .45;
  return a > .02 ? `style="--heat:rgba(${rgb},${a.toFixed(2)})"` : '';
}

function renderProcs() {
  const q = $('prQ').value.trim().toLowerCase();
  const match = p => !q || p.name.toLowerCase().includes(q) || (p.desc || '').toLowerCase().includes(q) || String(p.pid).includes(q) || (p.user || '').toLowerCase().includes(q) || (p.exe || '').toLowerCase().includes(q);
  const s = S?.system;
  if (s) {
    $('hCpu').textContent = pct(s.cpu); $('hMem').textContent = pct(s.mem.percent);
    $('hDisk').textContent = fmtRate(s.disk_r + s.disk_w);
  }
  $$('#p-processes th').forEach(th => { th.classList.toggle('sorted', th.dataset.k === sortK); th.dataset.dir = sortDir > 0 ? '▲' : '▼'; });
  const cells = (p, cls, nameHtml) => `<tr class="${cls}${selected && selected.id === (p.key || p.pid) ? ' sel' : ''}" data-id="${esc(p.key || p.pid)}">
    <td class="l name">${nameHtml}</td><td class="l">${esc(p.user || '')}</td><td>${p.pid ?? ''}</td>
    <td class="h" ${heat(p.cpu, 40, '57,135,229')}>${pct(p.cpu)}</td>
    <td class="h" ${heat(p.mem, 2 ** 31, '144,133,233')}>${fmtB(p.mem)}</td>
    <td class="h" ${heat(p.io_rate, 20 * 2 ** 20, '25,158,112')}>${p.io_rate > 1 ? fmtRate(p.io_rate) : '0'}</td><td>${p.threads}</td></tr>`;
  let html = '', count;
  if (prView === 'apps') {
    const groups = groupProcs(procs).filter(g => match(g) || g.children.some(match)).sort(cmp);
    count = groups.length + ' apps · ' + procs.length + ' processes';
    for (const g of groups) {
      const multi = g.children.length > 1, open = expanded.has(g.key);
      html += cells(g, 'grp', `<span class="tw" data-tw="${esc(g.key)}">${multi ? (open ? '▾' : '▸') : ''}</span>${esc(g.name)}${multi ? ` <span class="exe">(${g.children.length})</span>` : ''}`);
      if (multi && open) for (const p of [...g.children].sort(cmp)) html += cells(p, 'child', `${esc(p.name)}`);
    }
  } else {
    const rows = procs.filter(p => p.pid !== 0 && match(p)).sort(cmp);
    count = rows.length + ' processes';
    for (const p of rows.slice(0, 600)) html += cells(p, '', `${esc(p.name)}${p.desc ? `<span class="exe">${esc(p.desc)}</span>` : ''}`);
  }
  $('prCount').textContent = count;
  $('prBody').innerHTML = html;
  $('prEnd').disabled = !selected;
}

function lookup(id) {
  const n = Number(id);
  if (!isNaN(n) && String(n) === id) { const p = procs.find(x => x.pid === n); return p && { id: n, pids: [n], name: p.name, exe: p.exe, single: p }; }
  const g = groupProcs(procs).find(x => x.key === id);
  return g && { id, pids: g.children.map(c => c.pid), name: g.name, exe: g.exe, single: g.children.length === 1 ? g.children[0] : null };
}

$('prQ').oninput = renderProcs;
$('prView').onclick = e => { const b = e.target.closest('button'); if (!b) return; prView = b.dataset.v; $$('#prView button').forEach(x => x.classList.toggle('on', x === b)); selected = null; renderProcs(); };
$$('#p-processes th[data-k]').forEach(th => th.onclick = () => {
  const k = th.dataset.k; sortDir = sortK === k ? -sortDir : (['name', 'user'].includes(k) ? 1 : -1); sortK = k; renderProcs();
});
$('prBody').onclick = e => {
  const tw = e.target.closest('[data-tw]');
  if (tw) { const k = tw.dataset.tw; expanded.has(k) ? expanded.delete(k) : expanded.add(k); renderProcs(); return; }
  const tr = e.target.closest('tr'); if (!tr) return;
  selected = lookup(tr.dataset.id); renderProcs();
};
$('prBody').ondblclick = e => { const tr = e.target.closest('tr'); if (!tr) return; selected = lookup(tr.dataset.id); if (selected?.single) openDrawer(selected.single.pid); else if (selected) { expanded.add(tr.dataset.id); renderProcs(); } };
$('prBody').oncontextmenu = e => {
  e.preventDefault();
  const tr = e.target.closest('tr'); if (!tr) return;
  selected = lookup(tr.dataset.id); renderProcs(); if (selected) showCtx(e.clientX, e.clientY, selected);
};
$('prEnd').onclick = () => selected && endSel(selected, false);
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { hideCtx(); $('drawer').classList.remove('open'); }
  if (e.key === 'Delete' && page === 'processes' && selected && document.activeElement.tagName !== 'INPUT') endSel(selected, false);
  if (e.ctrlKey && e.key === 'f' && page === 'processes') { e.preventDefault(); $('prQ').focus(); }
});

async function endSel(sel, tree) {
  const what = sel.pids.length > 1 ? `${sel.name} (${sel.pids.length} processes)` : `${sel.name} (PID ${sel.pids[0]})`;
  if (!confirm(`End ${tree ? 'process tree of ' : ''}${what}?\n\nUnsaved work in this app will be lost.`)) return;
  let ok = 0, err = null;
  for (const pid of sel.pids) { const r = await api.end_process(pid, tree); r.ok ? ok++ : (err = r.error); }
  toast(ok ? `Ended ${sel.name}${ok > 1 ? ` (${ok} processes)` : ''}` : `Couldn't end ${sel.name}: ${err}`);
  selected = null; $('drawer').classList.remove('open'); loadProcs();
}

const PRI = [['realtime', 'Realtime'], ['high', 'High'], ['above', 'Above normal'], ['normal', 'Normal'], ['below', 'Below normal'], ['idle', 'Low']];
async function showCtx(x, y, sel) {
  const m = $('ctx');
  let cur = null;
  if (sel.single) { const d = await api.process_details(sel.single.pid); cur = d.ok ? d.data.priority : null; }
  m.innerHTML = `
    <button data-c="end">End task</button>
    ${sel.single ? '<button data-c="tree">End process tree</button>' : ''}
    <hr>
    ${sel.single ? `<div class="sub"><button>Set priority ▸</button><div class="ctx">${PRI.map(([k, l]) => `<button data-c="pri" data-p="${k}" class="${k === cur ? 'cur' : ''}">${l}</button>`).join('')}</div></div>` : ''}
    <button data-c="loc" ${sel.exe ? '' : 'disabled'}>Open file location</button>
    <button data-c="web">Search online</button>
    ${sel.single ? '<button data-c="det">Properties</button>' : ''}`;
  m.style.display = 'block';
  m.style.left = Math.min(x, innerWidth - m.offsetWidth - 8) + 'px';
  m.style.top = Math.min(y, innerHeight - m.offsetHeight - 8) + 'px';
  m.onclick = async e => {
    const b = e.target.closest('[data-c]'); if (!b) return; hideCtx();
    const c = b.dataset.c;
    if (c === 'end') endSel(sel, false);
    if (c === 'tree') endSel(sel, true);
    if (c === 'pri') { const r = await api.set_priority(sel.single.pid, b.dataset.p); toast(r.ok ? 'Priority set to ' + b.textContent : r.error); }
    if (c === 'loc') { const r = await api.open_location(sel.exe); if (!r.ok) toast(r.error); }
    if (c === 'web') api.open_url('https://www.bing.com/search?q=' + encodeURIComponent(sel.single?.name || sel.name));
    if (c === 'det') openDrawer(sel.single.pid);
  };
}
function hideCtx() { $('ctx').style.display = 'none'; }
document.addEventListener('click', e => { if (!e.target.closest('#ctx')) hideCtx(); if (!e.target.closest('#drawer') && !e.target.closest('#prBody')) $('drawer').classList.remove('open'); });

async function openDrawer(pid) {
  const r = await api.process_details(pid);
  const dr = $('drawer');
  if (!r.ok) { toast(r.error); return; }
  const d = r.data, kv = (k, v) => v == null || v === '' ? '' : `<label>${k}</label><span>${esc(v)}</span>`;
  dr.innerHTML = `<h2>${esc(d.desc || d.name)}</h2><div class="hint">${esc(d.name)} · PID ${d.pid}</div>
    <div class="kv">
      ${kv('Status', d.status)}${kv('User', d.user)}${kv('Started', new Date(d.created * 1000).toLocaleString())}
      ${kv('Priority', (PRI.find(x => x[0] === d.priority) || [0, d.priority])[1])}
      ${kv('Parent', d.parent ? `${d.parent} (${d.ppid})` : d.ppid)}${kv('Child processes', d.children)}
      ${kv('Threads', d.threads)}${kv('Handles', d.handles)}${kv('Connections', d.connections)}${kv('CPU affinity', d.affinity && d.affinity + ' processors')}
      ${kv('Working set', d.mem.working != null && fmtB(d.mem.working))}${kv('Private bytes', d.mem.private != null && fmtB(d.mem.private))}${kv('Peak working set', d.mem.peak != null && fmtB(d.mem.peak))}
      ${kv('Path', d.exe)}${kv('Command line', d.cmdline)}${kv('Working dir', d.cwd)}
    </div>
    <div class="acts"><button class="btn danger" id="dEnd">End task</button><button class="btn" id="dTree">End tree</button><button class="btn" id="dLoc" ${d.exe ? '' : 'disabled'}>Open file location</button></div>`;
  dr.classList.add('open');
  const sel = { id: pid, pids: [pid], name: d.name, exe: d.exe, single: { pid, name: d.name } };
  $('dEnd').onclick = () => endSel(sel, false);
  $('dTree').onclick = () => endSel(sel, true);
  $('dLoc').onclick = () => api.open_location(d.exe);
}

// ---------------------------------------------------------------- sensors
async function loadSensors() {
  if (page !== 'sensors') return;
  const list = await api.get_sensors();
  const q = $('snQ').value.trim().toLowerCase();
  const units = { Temperature: 'temp', Power: ' W', Fan: ' RPM', Clock: ' MHz', Load: '%', Voltage: ' V', Energy: ' mWh', Data: ' GB', SmallData: ' MB', Throughput: '/s', Level: '%', Control: '%', Factor: '' };
  const fv = (s, v) => s.type === 'Temperature' ? fmtT(v) : s.type === 'Throughput' ? fmtRate(v) : (Math.abs(v) >= 100 ? Math.round(v) : v.toFixed(Math.abs(v) < 10 ? 2 : 1)) + units[s.type];
  const groups = new Map();
  // Power sensors stuck at exactly 0 all session aren't readable (e.g. CPU power without admin) — hide them.
  const live = list.filter(s => !(s.type === 'Power' && s.max === 0 && s.min === 0));
  live.filter(s => !q || (s.hw + ' ' + s.sub + ' ' + s.name + ' ' + s.type).toLowerCase().includes(q)).forEach(s => {
    if (!groups.has(s.hw)) groups.set(s.hw, new Map());
    const byType = groups.get(s.hw);
    if (!byType.has(s.type)) byType.set(s.type, []);
    byType.get(s.type).push(s);
  });
  const order = ['Temperature', 'Power', 'Load', 'Clock', 'Fan', 'Voltage', 'Energy', 'Level', 'SmallData', 'Data', 'Throughput', 'Control', 'Factor'];
  $('snGroups').innerHTML = [...groups].map(([hw, byType]) => `<div class="card sgroup"><div class="card-h"><h2>${esc(hw)}</h2></div><table>
    <thead><tr><th class="l">Sensor</th><th>Value</th><th>Min</th><th>Max</th></tr></thead><tbody>
    ${[...byType].sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0])).map(([type, ss]) =>
      `<tr><td class="l" colspan="4" style="color:var(--text-3);font-size:11px;padding-top:10px">${type === 'SmallData' ? 'DATA' : type.toUpperCase()}</td></tr>` +
      ss.map(s => `<tr><td class="l">${esc(s.sub ? s.sub + ' · ' : '')}${esc(s.name)}</td><td><b>${fv(s, s.value)}</b>${s.type === 'Temperature' && !/Distance to TjMax/i.test(s.name) ? ' ' + statusPill(tempStatus(s.value)) : ''}</td><td>${fv(s, s.min)}</td><td>${fv(s, s.max)}</td></tr>`).join('')).join('')}
    </tbody></table></div>`).join('') || '<div class="empty">No sensors match.</div>';
  $('snCount').textContent = live.length + ' sensors';
  const st = S && cpuSensorState();
  $('snBanner').hidden = !st;
  if (st) setHTML($('snBanner'), st);
}
$('snQ').oninput = loadSensors;

// ---------------------------------------------------------------- startup
async function loadStartup() {
  const items = await api.startup_apps();
  $('suCount').textContent = `${items.filter(i => i.enabled).length} of ${items.length} enabled`;
  $('suList').innerHTML = items.map(i => `<div class="li"><div style="min-width:0"><div class="t">${esc(i.desc || i.name)}</div><div class="s" title="${esc(i.command)}">${esc(i.command)}</div></div>
    <span class="pill">${i.scope === 'user' ? 'This user' : 'All users'} · ${esc(i.source)}</span>
    <label class="switch"><input type="checkbox" data-su="${esc(i.id)}" ${i.enabled ? 'checked' : ''}><span></span></label></div>`).join('') || '<div class="empty">No startup apps.</div>';
}
$('suList').onchange = async e => {
  const cb = e.target.closest('[data-su]'); if (!cb) return;
  const r = await api.set_startup(cb.dataset.su, cb.checked);
  if (!r.ok) { cb.checked = !cb.checked; toast(r.error); } else { toast(cb.checked ? 'Enabled at startup' : 'Disabled at startup'); loadStartup(); }
};

// ---------------------------------------------------------------- settings
function getPath(o, p) { return p.split('.').reduce((a, k) => a?.[k], o); }
function setPath(o, p, v) { const ks = p.split('.'); const last = ks.pop(); ks.reduce((a, k) => a[k] ??= {}, o)[last] = v; }

async function loadSettings() {
  settings = await api.get_settings();
  $$('[data-set]').forEach(el => {
    const v = getPath(settings, el.dataset.set);
    if (el.type === 'checkbox') el.checked = !!v; else el.value = v ?? '';
  });
  $$('#unitSeg button').forEach(b => b.classList.toggle('on', b.dataset.u === settings.unit));
  // creating/removing the elevated task needs admin rights
  const aa = document.querySelector('[data-set="admin_auto"]');
  aa.disabled = !settings.is_admin;
  $('adminAutoDesc').textContent = settings.is_admin
    ? 'Keeps CPU temperature and power on, with no UAC prompt each time (uses an elevated scheduled task)'
    : 'Available in administrator mode: restart as administrator to change this';
}
document.addEventListener('change', async e => {
  const el = e.target.closest('[data-set]'); if (!el) return;
  setPath(settings, el.dataset.set, el.type === 'checkbox' ? el.checked : el.type === 'number' ? +el.value : el.value);
  const r = await api.save_settings(settings);
  if (r && r.ok === false) { toast(r.error); await loadSettings(); }
});
$('unitSeg').onclick = async e => { const b = e.target.closest('button'); if (!b) return; settings.unit = b.dataset.u; await api.save_settings(settings); loadSettings(); render(); };

// global actions
document.addEventListener('click', async e => {
  const a = e.target.closest('[data-act]'); if (!a) return;
  const act = a.dataset.act;
  if (act === 'admin') { const r = await api.relaunch_admin(); if (!r.ok) toast('Administrator restart was cancelled.'); }
  if (act === 'cpuSensors') {
    a.disabled = true;
    const r = await api.enable_cpu_sensors();
    a.disabled = false;
    if (r.opened) toast("Opened pawnio.eu. Install PawnIO from its author's site, then restart Taskvane as administrator.", 9000);
    else if (!r.ok) toast('Administrator restart was cancelled.');
    else if (S?.admin) toast('CPU sensors are starting…');
    else toast('Restarting as administrator…');
  }
  if (act === 'openLog') api.open_log();
  if (act === 'dismissUpdate' && S?.update) { updateDismissed = S.update.version; renderChrome(); }
  if (act === 'skipUpdate' && S?.update) { await api.skip_update(S.update.version); updateDismissed = S.update.version; renderChrome(); toast(`You won't be told about ${S.update.version} again.`); }
  if (act === 'export') { const r = await api.export_history(); if (r.ok) toast('Saved ' + r.path); else if (r.error) toast(r.error); }
  if (act === 'resetMinMax') { await api.reset_minmax(); loadSensors(); }
  if (act === 'refreshStartup') loadStartup();
});
document.addEventListener('click', e => {
  const u = e.target.closest('[data-url]'); if (u) api.open_url(u.dataset.url);
});
$('miniBtn').onclick = () => api.toggle_mini();

function renderSettingsInfo() {
  if (!S) return;
  $('adminDesc').textContent = S.admin ? 'Running as administrator: all sensors available.' : 'Needed for CPU temperature, CPU power and ending system processes.';
  $('adminBtn').hidden = S.admin;
  $('engineDesc').textContent = S.lhm.ok
    ? `LibreHardwareMonitor · ${S.lhm.count} sensors · CPU sensors ${S.hw.cpu_temp != null ? 'active' : 'off'}${S.lhm.restarts ? ` · helper restarted ${S.lhm.restarts}×` : ''} · v${S.version}`
    : 'Not available: ' + S.lhm.error;
  $('aboutVersion').textContent = 'Version ' + S.version;
  $('updateDesc').textContent = S.update ? `Version ${S.update.version} is available.` : '';
  const pw = S.pawnio || {};
  $('pawnioDesc').textContent = pw.installed ? `Installed${pw.version ? ' · version ' + pw.version : ''}${pw.outdated ? ' · update available' : ''}` : "Not installed. Needed for CPU temperature and CPU power; install it from its author's site.";
  $('pawnioBtn').hidden = pw.installed && !pw.outdated;
  $('pawnioBtn').textContent = pw.outdated ? 'Update at pawnio.eu' : 'Get it at pawnio.eu';
}

// ---------------------------------------------------------------- boot
async function boot() {
  api = window.pywebview.api;
  window.addEventListener('error', e => api.log_js_error(`${e.message} @ ${e.filename}:${e.lineno}`));
  window.addEventListener('unhandledrejection', e => api.log_js_error('promise: ' + (e.reason?.stack || e.reason)));
  await loadSettings();
  const notice = await api.take_notice();
  if (notice) setTimeout(() => toast(notice), 600);
  await refresh(); loadProcs();
  setInterval(() => { refresh(); renderSettingsInfo(); if (page === 'sensors') loadSensors(); }, 1000);
  setInterval(loadProcs, 2000);
}
window.addEventListener('pywebviewready', boot);
// called from Python when the window is re-shown from the tray
window.taskvaneGo = p => go(p);
