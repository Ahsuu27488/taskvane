// Minimal canvas time-series chart with crosshair + tooltip. No dependencies.
class TimeChart {
  /**
   * @param {HTMLElement} host  container; the chart fills it
   * @param {object} o  { series:[{key,label,color}], max?:number, fmt:(v)=>string, area?:bool, axis?:bool, grid?:bool }
   */
  constructor(host, o) {
    this.o = Object.assign({ area: true, axis: true, grid: true }, o);
    this.host = host;
    host.classList.add('chart');
    this.c = document.createElement('canvas');
    host.appendChild(this.c);
    if (this.o.axis) {
      this.tip = document.createElement('div');
      this.tip.className = 'tip';
      host.appendChild(this.tip);
      this.c.addEventListener('mousemove', e => { this.hx = e.offsetX; this.draw(); });
      this.c.addEventListener('mouseleave', () => { this.hx = null; this.tip.style.display = 'none'; this.draw(); });
    }
    this.t = []; this.d = {};
    this.ro = new ResizeObserver(() => this.draw());
    this.ro.observe(host);
  }

  destroy() { this.ro.disconnect(); this.host.innerHTML = ''; }

  set(t, data, span) { this.t = t; this.d = data; this.span = span; this.draw(); }

  draw() {
    const { c, o } = this, dpr = devicePixelRatio || 1;
    const W = this.host.clientWidth, H = this.host.clientHeight;
    if (!W || !H) return;
    if (c.width !== Math.round(W * dpr) || c.height !== Math.round(H * dpr)) {
      c.width = Math.round(W * dpr); c.height = Math.round(H * dpr);
      c.style.width = W + 'px'; c.style.height = H + 'px';
    }
    const g = c.getContext('2d');
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, W, H);
    const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
    const padL = o.axis ? 48 : 0, padB = o.axis ? 18 : 0, padT = o.axis ? 8 : 2;
    const w = W - padL, h = H - padB - padT;

    const vals = o.series.flatMap(s => (this.d[s.key] || []).filter(v => v != null));
    let top = o.max ?? (vals.length ? niceMax(Math.max(1e-9, ...vals) * 1.1) : (o.emptyMax ?? 1));
    if (o.min != null && top <= o.min) top = o.min + 1;
    const bottom = o.min ?? 0;
    const now = this.t.length ? this.t[this.t.length - 1] : Date.now() / 1000;
    const span = this.span || 60;
    const X = t => padL + w - ((now - t) / span) * w;
    const Y = v => padT + h - ((Math.min(v, top) - bottom) / (top - bottom)) * h;

    // grid + y labels (recessive)
    if (o.grid) {
      g.strokeStyle = css('--grid'); g.lineWidth = 1; g.fillStyle = css('--text-3');
      g.font = '11px "Segoe UI Variable", "Segoe UI", sans-serif'; g.textAlign = 'right'; g.textBaseline = 'middle';
      for (let i = 0; i <= 4; i++) {
        const v = bottom + (top - bottom) * i / 4, y = Math.round(Y(v)) + .5;
        g.beginPath(); g.moveTo(padL, y); g.lineTo(W, y); g.stroke();
        if (o.axis) g.fillText(o.fmt(v, true), padL - 8, y);
      }
      if (o.axis) {
        g.textAlign = 'center'; g.textBaseline = 'top';
        const lbl = s => s >= 60 ? Math.round(s / 60) + 'm' : s + 's';
        for (let i = 0; i <= 4; i++) {
          const s = Math.round(span * i / 4), x = padL + w - (i / 4) * w;
          g.textAlign = i === 0 ? 'right' : i === 4 ? 'left' : 'center';
          g.fillText(i === 0 ? 'now' : '-' + lbl(s), x, H - padB + 4);
        }
      }
    }

    // series
    o.series.forEach((s, si) => {
      const arr = this.d[s.key] || [];
      g.beginPath();
      let started = false, first = null, last = null;
      for (let i = 0; i < arr.length; i++) {
        const v = arr[i];
        if (v == null) { started = false; continue; }
        const x = X(this.t[i]), y = Y(v);
        if (x < padL - 2) continue;
        if (!started) { g.moveTo(x, y); started = true; first = first ?? [x, y]; } else g.lineTo(x, y);
        last = [x, y];
      }
      g.strokeStyle = s.color; g.lineWidth = 2; g.lineJoin = 'round'; g.stroke();
      if (o.area && si === 0 && first && last) {
        g.lineTo(last[0], padT + h); g.lineTo(first[0], padT + h); g.closePath();
        const gr = g.createLinearGradient(0, padT, 0, padT + h);
        gr.addColorStop(0, s.color + '40'); gr.addColorStop(1, s.color + '00');
        g.fillStyle = gr; g.fill();
      }
    });

    if (!vals.length && o.emptyText) {
      g.fillStyle = css('--text-3'); g.textAlign = 'center'; g.textBaseline = 'middle';
      g.font = '13px "Segoe UI Variable", "Segoe UI", sans-serif';
      const text = typeof o.emptyText === 'function' ? o.emptyText() : o.emptyText;
      text.split('\n').forEach((ln, i, a) => g.fillText(ln, padL + w / 2, padT + h / 2 + (i - (a.length - 1) / 2) * 18));
      return;
    }

    // crosshair + tooltip
    if (this.hx != null && this.t.length && this.hx > padL) {
      const target = now - ((padL + w - this.hx) / w) * span;
      let bi = 0, bd = Infinity;
      this.t.forEach((t, i) => { const d = Math.abs(t - target); if (d < bd) { bd = d; bi = i; } });
      const x = X(this.t[bi]);
      g.strokeStyle = css('--text-3'); g.lineWidth = 1; g.setLineDash([3, 3]);
      g.beginPath(); g.moveTo(x, padT); g.lineTo(x, padT + h); g.stroke(); g.setLineDash([]);
      const rows = o.series.map(s => {
        const v = (this.d[s.key] || [])[bi];
        if (v != null) {
          g.beginPath(); g.arc(x, Y(v), 4, 0, Math.PI * 2);
          g.fillStyle = s.color; g.fill(); g.lineWidth = 2; g.strokeStyle = css('--surface'); g.stroke();
        }
        return `<div><i style="background:${s.color}"></i>${s.label}<b>${v == null ? '–' : o.fmt(v)}</b></div>`;
      });
      const ago = Math.round(now - this.t[bi]);
      this.tip.innerHTML = `<div class="tip-h">${ago ? ago + 's ago' : 'now'}</div>` + rows.join('');
      this.tip.style.display = 'block';
      const tw = this.tip.offsetWidth;
      this.tip.style.left = (x + 12 + tw > W ? x - tw - 12 : x + 12) + 'px';
      this.tip.style.top = padT + 'px';
    }
  }
}

function niceMax(v) {
  const p = Math.pow(10, Math.floor(Math.log10(v))), n = v / p;
  return (n <= 1 ? 1 : n <= 2 ? 2 : n <= 2.5 ? 2.5 : n <= 5 ? 5 : 10) * p;
}

// Tiny sparkline for list items / cards (no axes, no hover).
function sparkline(canvas, arr, color, max) {
  const dpr = devicePixelRatio || 1, W = canvas.clientWidth, H = canvas.clientHeight;
  if (!W || !H) return;
  if (canvas.width !== W * dpr) { canvas.width = W * dpr; canvas.height = H * dpr; }
  const g = canvas.getContext('2d');
  g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, H);
  const v = arr.filter(x => x != null);
  if (v.length < 2) return;
  const top = max ?? Math.max(1e-9, ...v) * 1.15, N = 60, step = W / (N - 1);
  const pts = arr.slice(-N).map((y, i, a) => [W - (a.length - 1 - i) * step, H - 1 - (Math.min(y ?? 0, top) / top) * (H - 3)]);
  g.beginPath(); pts.forEach(([x, y], i) => i ? g.lineTo(x, y) : g.moveTo(x, y));
  g.strokeStyle = color; g.lineWidth = 1.5; g.stroke();
  g.lineTo(pts.at(-1)[0], H); g.lineTo(pts[0][0], H); g.closePath();
  g.fillStyle = color + '30'; g.fill();
}
