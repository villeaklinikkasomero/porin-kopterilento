// ---------- HUD ----------
const mini = $('mini'), mx = mini.getContext('2d'), miniImg = new Image(); miniImg.src = './mini.jpg';
let hudT = 0;
function hud(dt) {
  if (toastT > 0) { toastT -= dt; if (toastT <= 0) $('toast').classList.remove('on'); }
  hudT -= dt; if (hudT > 0) return; hudT = 0.1;
  const sp = Math.hypot(S.vx, S.vy, S.vz) * 3.6;
  $('gs').textContent = Math.round(sp); $('ga').textContent = Math.max(0, Math.round(S.alt - SKID));
  let deg = (S.yaw * 180 / Math.PI) % 360; if (deg < 0) deg += 360; $('gh').textContent = DIRS[Math.round(deg / 45) % 8];
  const hp = $('hp').firstElementChild; hp.style.width = S.hp + '%'; hp.style.background = S.hp > 50 ? 'var(--ok)' : S.hp > 25 ? 'var(--accent)' : 'var(--bad)';
  const st = nearestStreet(S.x, S.y); $('sn').textContent = st || '';
  let pl = '', pd = 150; for (const p of CITY.places) { const d = Math.hypot(p.x - S.x, p.y - S.y); if (d < pd) { pd = d; pl = p.n; } }
  if (!pl && S.y > 470 && S.y < 640 && Math.abs(S.x) < HW) pl = 'Kokemäenjoki';
  $('sp').textContent = pl && pl !== st ? pl : '';
  const tg = target(), d = Math.hypot(tg.x - S.x, tg.y - S.y);
  if (VEH === 'car' && !WALK.on) navHud(); else $('nav').style.display = 'none';
  if (WALK.in) { $('sn').textContent = WALK.in.name; $('sp').textContent = WALK.in.room; }
  $('md').textContent = tourDone ? '–' : d < 1000 ? Math.round(d / 5) * 5 + ' m' : (d / 1000).toFixed(1) + ' km';
  $('mtime').textContent = fmtT(tourT) + (best ? '' : ''); $('mk').textContent = 'Päivän kierros ' + DAY.label + (best ? ' · paras ' + fmtT(best) : '');
  // minimap (north up, 700 m across)
  const W = mini.width, R = 350, sc = W / (2 * R);
  mx.fillStyle = '#5c6a55'; mx.fillRect(0, 0, W, W);
  if (miniImg.complete && miniImg.naturalWidth) {
    const ix = (S.x - R - OX0) / OXS * miniImg.naturalWidth, iy = (OY1 - (S.y + R)) / OYS * miniImg.naturalHeight;
    mx.drawImage(miniImg, ix, iy, 2 * R / OXS * miniImg.naturalWidth, 2 * R / OYS * miniImg.naturalHeight, 0, 0, W, W);
  }
  if (VEH === 'car' && NAV.route && !tourDone) {   // the route on the minimap
    mx.strokeStyle = 'rgba(64,160,255,.9)'; mx.lineWidth = 6; mx.lineJoin = mx.lineCap = 'round'; mx.beginPath();
    mx.moveTo(W / 2, W / 2); for (const q of NAV.route) mx.lineTo(W / 2 + (q.x - S.x) * sc, W / 2 - (q.y - S.y) * sc); mx.stroke();
  }
  if (!tourDone) {
    let tx = (tg.x - S.x) * sc, ty = -(tg.y - S.y) * sc; const m = Math.hypot(tx, ty), lim = W / 2 - 14; const off = m > lim; if (off) { tx *= lim / m; ty *= lim / m; }
    mx.fillStyle = '#ffc928'; mx.strokeStyle = '#16110a'; mx.lineWidth = 3; mx.beginPath(); mx.arc(W / 2 + tx, W / 2 + ty, off ? 8 : 12, 0, 7); mx.fill(); mx.stroke();
  }
  mx.save(); mx.translate(W / 2, W / 2); mx.rotate(S.yaw); mx.fillStyle = '#fff'; mx.strokeStyle = '#0e161e'; mx.lineWidth = 3; mx.beginPath(); mx.moveTo(0, -16); mx.lineTo(11, 12); mx.lineTo(0, 6); mx.lineTo(-11, 12); mx.closePath(); mx.fill(); mx.stroke(); mx.restore();
  mx.fillStyle = 'rgba(14,22,30,.7)'; mx.fillRect(W - 34, 6, 28, 28); mx.fillStyle = '#fff'; mx.font = '700 20px system-ui, sans-serif'; mx.textAlign = 'center'; mx.textBaseline = 'middle'; mx.fillText('P', W - 20, 21);
}

// navigator panel: an arrow for the next turn, the distance to it and the street to turn into
const navc = $('navc'), nvx = navc.getContext('2d');
function drawArrow(turn, end) {
  const W = navc.width; nvx.clearRect(0, 0, W, W); nvx.save(); nvx.translate(W / 2, W * 0.78);
  nvx.strokeStyle = '#fff'; nvx.fillStyle = '#fff'; nvx.lineWidth = 11; nvx.lineCap = 'round'; nvx.lineJoin = 'round';
  if (end) { nvx.beginPath(); nvx.moveTo(0, 0); nvx.lineTo(0, -W * 0.38); nvx.stroke(); nvx.beginPath(); nvx.arc(0, -W * 0.52, 13, 0, 7); nvx.fillStyle = '#ffc928'; nvx.fill(); nvx.restore(); return; }
  const a = Math.max(-2.6, Math.min(2.6, turn)), L1 = W * 0.3, L2 = W * 0.3, ex = Math.sin(a) * L2, ey = -L1 - Math.cos(a) * L2;
  nvx.beginPath(); nvx.moveTo(0, 0); nvx.lineTo(0, -L1); nvx.lineTo(ex, ey); nvx.stroke();
  nvx.translate(ex, ey); nvx.rotate(a); nvx.beginPath(); nvx.moveTo(0, -17); nvx.lineTo(15, 4); nvx.lineTo(-15, 4); nvx.closePath(); nvx.fill(); nvx.restore();
}
function navHud() {
  const el = $('nav'); if (!started || tourDone || !NAV.route) { el.style.display = 'none'; return; }
  const m = NAV.next(CAR.x, CAR.y, CAR.yaw); if (!m) { el.style.display = 'none'; return; }
  el.style.display = 'flex';
  const dd = m.d < 1000 ? (m.d < 100 ? Math.round(m.d / 5) * 5 : Math.round(m.d / 10) * 10) + ' m' : (m.d / 1000).toFixed(1) + ' km';
  if (m.end) { drawArrow(0, true); $('navd').textContent = dd; $('navn').textContent = target().n; return; }
  drawArrow(m.turn, false); $('navd').textContent = dd;
  const dir = Math.abs(m.turn) > 2.4 ? 'Käänny ympäri' : m.turn > 0 ? (m.turn < 0.9 ? 'Loivasti oikealle' : 'Oikealle') : (m.turn > -0.9 ? 'Loivasti vasemmalle' : 'Vasemmalle');
  $('navn').textContent = dir + (m.n ? ' – ' + m.n : '');
}

