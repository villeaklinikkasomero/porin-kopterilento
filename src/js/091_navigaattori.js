// ---------- navigator for the car: shortest route on the street graph, the next turn as an arrow ----------
const NAV = { route: null, t: 0, tgt: null }; window.__nav = NAV;
{
  const nodes = new Map(), key = (x, y) => x + ',' + y;
  const node = (x, y) => { const k = key(x, y); if (!nodes.has(k)) nodes.set(k, { x, y, e: [] }); return nodes.get(k); };
  CITY.r.forEach((r, ri) => { if (!r.k) return;
    for (let i = 0; i + 3 < r.p.length; i += 2) { const a = node(r.p[i], r.p[i + 1]), b = node(r.p[i + 2], r.p[i + 3]); if (a === b) continue;
      const L = Math.hypot(b.x - a.x, b.y - a.y), si = i / 2; a.e.push({ to: b, L, n: r.n || '', ri, si, fw: true }); b.e.push({ to: a, L, n: r.n || '', ri, si, fw: false }); } });
  const list = [...nodes.values()].filter(n => n.e.length);
  const nearSeg = (x, y) => { let best = null, bd = 1e18;
    for (const a of list) { if (Math.abs(a.x - x) > 150 || Math.abs(a.y - y) > 150) continue;
      for (const e of a.e) { const b = e.to, dx = b.x - a.x, dy = b.y - a.y, t = Math.max(0, Math.min(1, ((x - a.x) * dx + (y - a.y) * dy) / (dx * dx + dy * dy || 1))), px = a.x + dx * t, py = a.y + dy * t, d = (px - x) ** 2 + (py - y) ** 2;
        if (d < bd) { bd = d; best = { a, b, t, px, py, n: e.n, d: Math.sqrt(d), ri: e.ri, si: e.si, fwd: e.fw }; } } }
    return best; };
  const nearNode = (x, y) => { let best = null, bd = 1e18; for (const a of list) { const d = (a.x - x) ** 2 + (a.y - y) ** 2; if (d < bd) { bd = d; best = a; } } return best; };
  NAV.seg = nearSeg;
  NAV.plan = (x, y, tx, ty, free) => {
    const s0 = nearSeg(x, y), goal = nearNode(tx, ty); if (!s0 || !goal) return null;
    const dist = new Map(), prev = new Map(), H = [];
    const push = (n, d, p, pn) => { if (d < (dist.get(n) ?? 1e18)) { dist.set(n, d); prev.set(n, [p, pn]); H.push([d, n]); let i = H.length - 1; while (i > 0) { const j = (i - 1) >> 1; if (H[j][0] <= H[i][0]) break; [H[i], H[j]] = [H[j], H[i]]; i = j; } } };
    const pop = () => { const top = H[0], last = H.pop(); if (H.length) { H[0] = last; let i = 0; for (;;) { const l = 2 * i + 1, r = l + 1; let m = i; if (l < H.length && H[l][0] < H[m][0]) m = l; if (r < H.length && H[r][0] < H[m][0]) m = r; if (m === i) break; [H[i], H[m]] = [H[m], H[i]]; i = m; } } return top; };
    const L = Math.hypot(s0.b.x - s0.a.x, s0.b.y - s0.a.y);
    const okA = owOk(s0.ri, s0.si, !s0.fwd), okB = owOk(s0.ri, s0.si, s0.fwd);
    if (okA) push(s0.a, s0.t * L, null, s0.n); if (okB || !okA) push(s0.b, (1 - s0.t) * L, null, s0.n);
    const done = new Set();
    while (H.length) { const [d, n] = pop(); if (done.has(n)) continue; done.add(n); if (n === goal) break;
      for (const e of n.e) if (!done.has(e.to) && (free || owOk(e.ri, e.si, e.fw))) push(e.to, d + e.L, n, e.n); }   // one-way streets only forwards
    if (!prev.has(goal)) return free ? null : NAV.plan(x, y, tx, ty, true);
    const pts = []; let n = goal; while (n) { const [p, nm] = prev.get(n); pts.push({ x: n.x, y: n.y, n: nm, deg: n.e.length }); n = p; }
    pts.push({ x: s0.px, y: s0.py, n: s0.n, deg: 2 }); pts.reverse();
    pts.push({ x: tx, y: ty, n: '', deg: 1 });
    return pts;
  };
  // the next manoeuvre along the route from the car: { turn: signed angle (rad, + = right), d: metres to it, n: street after it }
  NAV.next = (x, y, yaw) => {
    const R = NAV.route; if (!R || R.length < 2) return null;
    let k = 1, acc = Math.hypot(R[1].x - x, R[1].y - y);
    const head = (a, b) => Math.atan2(b.x - a.x, b.y - a.y);
    for (; k < R.length - 1; k++) {
      const h1 = head(R[k - 1], R[k]), h2 = head(R[k], R[k + 1]); let dh = h2 - h1; dh = Math.atan2(Math.sin(dh), Math.cos(dh));
      const seg = Math.hypot(R[k + 1].x - R[k].x, R[k + 1].y - R[k].y);
      if (Math.abs(dh) > 0.52 && R[k].deg >= 3 && seg > 4) return { turn: dh, d: acc, n: R[k + 1].n };
      acc += seg;
    }
    return { turn: 0, d: acc, n: '', end: true };
  };
  NAV.off = (x, y) => { const R = NAV.route; if (!R) return 1e9; let bd = 1e9;
    for (let i = 0; i + 1 < R.length; i++) { const a = R[i], b = R[i + 1], dx = b.x - a.x, dy = b.y - a.y, t = Math.max(0, Math.min(1, ((x - a.x) * dx + (y - a.y) * dy) / (dx * dx + dy * dy || 1)));
      bd = Math.min(bd, Math.hypot(a.x + dx * t - x, a.y + dy * t - y)); } return bd; };
  NAV.update = (dt, tg) => {
    NAV.t -= dt; const moved = !NAV.tgt || NAV.tgt.x !== tg.x || NAV.tgt.y !== tg.y;
    if (moved || NAV.t <= 0 && NAV.off(CAR.x, CAR.y) > 18) { NAV.route = NAV.plan(CAR.x, CAR.y, tg.x, tg.y); NAV.tgt = tg; NAV.t = 1.5; }
    else if (NAV.t <= 0) NAV.t = 1.5;
    // drop the route points already passed
    const R = NAV.route; if (R) while (R.length > 2 && Math.hypot(R[1].x - CAR.x, R[1].y - CAR.y) < 9) R.shift();
  };
}

