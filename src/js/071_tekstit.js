// ---------- text helpers ----------
function textCanvas(text, { size = 44, color = '#fff', stroke = 'rgba(8,14,20,.9)', weight = 700, pad = 12, bg = null } = {}) {
  const c = document.createElement('canvas'), x = c.getContext('2d');
  const font = `${weight} ${size}px ui-sans-serif, system-ui, "Segoe UI", Roboto, Arial, sans-serif`;
  x.font = font; const w = Math.ceil(x.measureText(text).width) + pad * 2 + 8, h = Math.ceil(size * 1.4);
  c.width = w; c.height = h; x.font = font; x.textBaseline = 'middle'; x.textAlign = 'center';
  if (bg) { x.fillStyle = bg; x.beginPath(); x.roundRect(0, 0, w, h, h * 0.28); x.fill(); }
  else { x.lineJoin = 'round'; x.lineWidth = size * 0.2; x.strokeStyle = stroke; x.strokeText(text, w / 2, h / 2 + 1); }
  x.fillStyle = color; x.fillText(text, w / 2, h / 2 + 1);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return { tex: t, aspect: w / h };
}

