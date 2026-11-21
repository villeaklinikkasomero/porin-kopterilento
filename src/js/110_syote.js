// ---------- input ----------
addEventListener('keydown', e => {
  if (e.target && e.target.tagName === 'INPUT') { if (e.code === 'Enter') { e.target.blur(); LB.save(); } return; }
  if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) e.preventDefault();
  if (e.repeat) return; keys.add(e.code);
  if (!started) { if (e.code === 'Enter' && !$('go').disabled) begin(); return; }
  if (e.code === 'KeyC') camMode = (camMode + 1) % 3;
  if (e.code === 'Enter' || e.code === 'NumpadEnter' || (e.code === 'KeyF' && (WALK.on || VEH === 'car'))) walkAction();
  if (e.code === 'KeyT') LB.show(!LB.open);
  if (e.code === 'KeyM') toggleSound();
  if (e.code === 'KeyR' && !WALK.on) RADIO.next();
  if (e.code === 'KeyY' && window.__ride) window.__ride.accept();
  if (e.code === 'KeyN' && window.__bus) window.__bus.bell();      // bus: stop button (B is dancing on foot)
  if (e.code === 'KeyH' && WALK.on && !WALK.in && window.__npc) window.__npc.greet();
  if (e.code === 'KeyB' && WALK.on && !WALK.in) DANCE.toggle();      // music on foot: the people near dance
  if (e.code === 'KeyN') newTour();
});
addEventListener('keyup', e => keys.delete(e.code));
addEventListener('blur', () => keys.clear());
const touchIn = { f: 0, t: 0, l: 0 };
{
  const stick = $('stick'), knob = $('knob'); let id = null;
  const mv = e => { const r = stick.getBoundingClientRect(); let dx = (e.clientX - r.left - r.width / 2) / (r.width / 2), dy = (e.clientY - r.top - r.height / 2) / (r.height / 2); const m = Math.hypot(dx, dy); if (m > 1) { dx /= m; dy /= m; }
    knob.style.transform = `translate(${dx * 38}px,${dy * 38}px)`; touchIn.t = dx; touchIn.f = -dy; };
  stick.addEventListener('pointerdown', e => { id = e.pointerId; stick.setPointerCapture(id); mv(e); });
  stick.addEventListener('pointermove', e => { if (e.pointerId === id) mv(e); });
  const end = e => { if (e.pointerId === id) { id = null; knob.style.transform = ''; touchIn.t = touchIn.f = 0; } };
  stick.addEventListener('pointerup', end); stick.addEventListener('pointercancel', end);
  for (const [el, v] of [[$('tup'), 1], [$('tdn'), -1]]) {
    el.addEventListener('pointerdown', e => { el.setPointerCapture(e.pointerId); touchIn.l = v; el.classList.add('on'); });
    const up = () => { touchIn.l = 0; el.classList.remove('on'); }; el.addEventListener('pointerup', up); el.addEventListener('pointercancel', up);
  }
}
function readInput() {
  const k = c => keys.has(c) ? 1 : 0;
  input.f = k('KeyW') + k('ArrowUp') - k('KeyS') - k('ArrowDown') + touchIn.f;
  input.t = k('KeyD') + k('ArrowRight') - k('KeyA') - k('ArrowLeft') + touchIn.t;
  input.s = k('KeyE') - k('KeyQ');
  input.l = k('Space') + k('KeyR') - k('ShiftLeft') - k('ShiftRight') - k('KeyF') + touchIn.l;
  for (const a of ['f', 't', 's', 'l']) input[a] = Math.max(-1, Math.min(1, input[a]));
  if (window.__syoteLukko) input.f = input.t = input.s = input.l = 0;      // 21.11.2026: tarina ohjaa (esim. drooni M05, tarina/mekaniikat.js)
}

