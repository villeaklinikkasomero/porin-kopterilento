function walkOutAt(x, y, yaw) {      // leaving the jump plane: on foot beside it (the helicopter / car stays where it was left)
  Object.assign(WALK, { on: true, in: false, x, y, z: carGround(x, y) ?? TZs(x, y), yaw, v: 0, vs: 0 }); document.body.classList.add('walk'); scene.add(walkG); walkG.visible = true; loadWalker(); RADIO.mute();
  camera.near = 0.25; camera.updateProjectionMatrix(); if (camMode === 2) camMode = 0; }
window.__game = { TZg, outerMat, touchIn, carGround, carG, bldTopAt, fadeDo, toast, walkOutAt, walkG, loadWalker, get camMode() { return camMode; }, get actx() { return actx; }, get soundOn() { return soundOn; },
  world: (x, y) => { if (performance.now() - HR.last > 500) { HR.last = performance.now(); hrUpdate(x, y); TEXLOD.update(x, y); streamUpdate(x, y); TREES.update(x, y); GRASS.update(); } GRASS.tick(performance.now() / 1000); },
  WALK, IN, PLACES, placeDoor, walkAction, sceneIn, door: churchDoor, S, begin, keys, camera, renderer, scene, roofAt, TZs, tour: () => ({ tourIdx, tourOn, tourDone, tourT, n: TOUR.length }), setTour: i => { tourIdx = i; tourOn = true; setTarget(); }, setCam: m => camMode = m, step, snap: () => { camPos.set(S.x - Math.sin(S.yaw) * 21, S.alt + 7.5, -S.y + Math.cos(S.yaw) * 21); camLook.set(S.x + Math.sin(S.yaw) * 14, S.alt + 1.5, -S.y - Math.cos(S.yaw) * 14); } };
terrainizeScene(); setInterval(terrainizeScene, 1000);
requestAnimationFrame(frame);
