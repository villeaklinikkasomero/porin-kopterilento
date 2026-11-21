// ---------- loop ----------
let lastT = performance.now(), bt = 0;
function frame(now) {
  const dt = Math.min(0.05, (now - lastT) / 1000); lastT = now; bt += dt;
  step(dt); cars.update(dt); if (window.__npc) window.__npc.update(dt); if (window.__statueTick) window.__statueTick(dt); if (window.__birdTick) window.__birdTick(dt); if (window.__raceTick) window.__raceTick(dt); if (window.__rideTick) window.__rideTick(dt); if (window.__busTick) window.__busTick(dt); if (window.__efpoTick) window.__efpoTick(dt); window.__takeTick(dt); updateCamera(dt); hud(dt);
  const r1 = beacon.getObjectByName('ring'), r2 = beacon.getObjectByName('ring2'); const pu = 1 + Math.sin(bt * 3) * 0.06; r1.scale.setScalar(pu); r2.scale.setScalar(0.72 + (bt * 0.5 % 1) * 0.5); r2.material.opacity = 0.8 - (bt * 0.5 % 1) * 0.8;
  for (const sp of sprites) { const d = sp.position.distanceTo(camera.position), far = sp.userData.big ? 2600 : 1100;
    const o = Math.min(1, Math.max(0, (d - 70) / 110)) * Math.min(1, Math.max(0, (far - d) / 250)); sp.visible = o > 0.02; sp.material.opacity = o; }
  renderer.render(WALK.in ? sceneIn : scene, camera);
  requestAnimationFrame(frame);
}

