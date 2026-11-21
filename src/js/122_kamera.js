// ---------- camera ----------
const camPos = new THREE.Vector3(HOME.x, 60, -HOME.y + 120), camLook = new THREE.Vector3(HOME.x, 5, -HOME.y), tmp = new THREE.Vector3(), tmp2 = new THREE.Vector3();
let introA = 0;
function updateCamera(dt) {
  const sn = Math.sin(S.yaw), cs = Math.cos(S.yaw);
  if (!started) { // slow orbit around the square
    introA += dt * 0.12; camera.position.set(HOME.x + Math.sin(introA) * 210, 120, -HOME.y + Math.cos(introA) * 210); camera.lookAt(HOME.x, 10, -HOME.y); return;
  }
  if (window.__kameraKoukku && window.__kameraKoukku(camera, dt)) return;      // 21.11.2026: tarinan kamera (drooni M05, tarina/mekaniikat.js)
  if (window.__jump && window.__jump.on) return window.__jump.cam(dt, camMode);      // parachute jump
  if (window.__plane && window.__plane.on) return window.__plane.cam(dt, camMode);      // jump plane: cockpit / chase / top-down
  if (window.__bus && window.__bus.cam(dt)) return;      // riding a live bus
  if (WALK.on) return walkCamera(dt);
  if (VEH === 'car') {
    if (camMode === 1) { // driver's seat (left-hand drive)
      const rx = Math.cos(S.yaw), ry = -Math.sin(S.yaw);
      const cm = CAR.cam || [0, 0, 0], cf = cm[2] - 0.22, cl = 0.37 + cm[0];
      camera.position.set(CAR.x + sn * cf - rx * cl, CAR.z + 1.17 + cm[1], -(CAR.y + cs * cf - ry * cl)); camera.rotation.order = 'YXZ'; camera.rotation.set(CAR.pitch - 0.05, -S.yaw, -CAR.roll * 0.8); return;
    }
    if (camMode === 2) { tmp.set(CAR.x, CAR.z + 90, -CAR.y + 1); camPos.lerp(tmp, Math.min(1, dt * 4)); camera.position.copy(camPos); camera.up.set(sn, 0, -cs); camera.lookAt(CAR.x, CAR.z, -CAR.y); camera.up.set(0, 1, 0); return; }
    const hl = inHall(CAR.x, CAR.y), bus = CAR.type === 'bus', back = hl ? 4.6 : bus ? 17 : 7.8, up = hl ? 1.9 : bus ? 5.6 : 2.9; tmp.set(CAR.x - sn * back, CAR.z + up, -CAR.y + cs * back);   // under the hall's ceiling the camera comes down and closer
    const gb = carGround(tmp.x, -tmp.z); if (gb !== null && tmp.y < gb + 1.2) tmp.y = gb + 1.2;
    camPos.lerp(tmp, 1 - Math.exp(-dt * 6)); tmp2.set(CAR.x + sn * 6, CAR.z + 1.1, -CAR.y - cs * 6); camLook.lerp(tmp2, 1 - Math.exp(-dt * 9));
    camera.position.copy(camPos); camera.lookAt(camLook); return;
  }
  if (camMode === 1) { // cockpit
    camera.position.set(S.x + sn * 1.6, S.alt + 0.9, -S.y - cs * 1.6); camera.rotation.order = 'YXZ'; camera.rotation.set(S.pitch * 0.6 - 0.12, -S.yaw, S.roll * 0.7); return;
  }
  if (camMode === 2) { // top-down
    tmp.set(S.x, S.alt + 230, -S.y + 1); camPos.lerp(tmp, Math.min(1, dt * 4)); camera.position.copy(camPos); camera.up.set(sn, 0, -cs); camera.lookAt(S.x, S.alt, -S.y); camera.up.set(0, 1, 0); return;
  }
  const back = 21, up = 7.5;
  tmp.set(S.x - sn * back, S.alt + up, -S.y + cs * back);
  // keep the chase camera above roofs behind the helicopter
  const rb = roofAt(tmp.x, -tmp.z); if (tmp.y < rb + 3) tmp.y = rb + 3;
  camPos.lerp(tmp, 1 - Math.exp(-dt * 4.5)); if (camPos.y < 2) camPos.y = 2;
  tmp2.set(S.x + sn * 14, S.alt + 1.5, -S.y - cs * 14); camLook.lerp(tmp2, 1 - Math.exp(-dt * 7));
  camera.position.copy(camPos); camera.lookAt(camLook);
}

