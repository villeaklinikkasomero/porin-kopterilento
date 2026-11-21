// ---------- tall grass: instanced tufts on the green parts of the aerial image, only near the camera ----------
// Two rings of tufts on fixed world grids that wrap around the camera (no swimming), height from the photo's greenness, swaying in the wind.
// 21.11.2026 (omistaja: "Kirjurissa rannalla tämä ei seuraa rannan muotoja"): tupsut seisoivat tasoitetun kentän (THS) korkeudella, mutta maa piirretään
// todellisesta maasta (THG) – rannan luiskissa ja kaivannoissa tupsut leijuivat jopa 2 m maan yllä. Nyt korkeus THG:stä.
const maaTexG = (() => { const n = TER.nx * TER.ny, d = new Uint16Array(n); for (let i = 0; i < n; i++) d[i] = THREE.DataUtils.toHalfFloat(THG[i] / 10);
  const t = new THREE.DataTexture(d, TER.nx, TER.ny, THREE.RedFormat, THREE.HalfFloatType); t.minFilter = t.magFilter = THREE.LinearFilter; t.needsUpdate = true; return t; })();
const GRASS = (() => {
  const mk = (blades, seed) => { let s = seed; const r = () => (s = (s * 16807) % 2147483647) / 2147483647; const P = [];
    for (let b = 0; b < blades; b++) { const a = r() * 6.283, d = Math.sqrt(r()) * 0.3, bx = Math.cos(a) * d, bz = Math.sin(a) * d, o = r() * 6.283, w = 0.045 + r() * 0.04, l = 0.15 + r() * 0.25, la = a + (r() - 0.5);
      const hb = 0.65 + r() * 0.35;   // blade height share
      P.push(bx - Math.cos(o) * w, 0, bz - Math.sin(o) * w, bx + Math.cos(o) * w, 0, bz + Math.sin(o) * w, bx + Math.cos(la) * l, hb, bz + Math.sin(la) * l); }
    const g = new THREE.InstancedBufferGeometry(); g.setAttribute('position', new THREE.Float32BufferAttribute(P, 3)); return g; };
  const VS = `
    attribute vec3 iOff; uniform sampler2D uOrto, tHeight, uRM; uniform vec4 uRB; uniform vec4 tGrid; uniform vec2 tSize; uniform vec4 uCore; uniform vec4 uRing; uniform vec2 uTile; uniform float uT;
    varying vec3 vC; varying float vFog;
    void main() {
      vec2 cam = vec2(cameraPosition.x, -cameraPosition.z), p = iOff.xy;
      vec2 w = p + uTile.x * floor((cam - p) / uTile.x + 0.5);
      float d = length(w - cam);
      float fade = smoothstep(uRing.x, uRing.y, d) * (1.0 - smoothstep(uRing.z, uRing.w, d));
      vec2 ou = vec2((w.x + uCore.x) / (2.0 * uCore.x), (w.y - uCore.y) / uCore.z);
      vec3 c = texture2D(uOrto, ou).rgb;
      vec2 du = vec2(1.6 / (2.0 * uCore.x), 0.0), dv = vec2(0.0, 1.6 / uCore.z);   // lawn only where the photo is green all around (no tufts on paving, kerbs or parked cars)
      vec3 c1 = texture2D(uOrto, ou + du).rgb, c2 = texture2D(uOrto, ou - du).rgb, c3 = texture2D(uOrto, ou + dv).rgb, c4 = texture2D(uOrto, ou - dv).rgb;
      float gmin = min(min(c.g - max(c.r, c.b), c1.g - max(c1.r, c1.b)), min(min(c2.g - max(c2.r, c2.b), c3.g - max(c3.r, c3.b)), c4.g - max(c4.r, c4.b)));
      float inside = step(0.0, ou.x) * step(ou.x, 1.0) * step(0.0, ou.y) * step(ou.y, 1.0);
      vec2 ru = (w - uRB.xy) / uRB.zw; if (uRB.z > 0.0 && ru.x > 0.0 && ru.x < 1.0 && ru.y > 0.0 && ru.y < 1.0 && texture2D(uRM, ru).g > 0.4) inside = 0.0;   // street surfaces
      float gr = smoothstep(0.015, 0.04, gmin) * smoothstep(1.25, 0.75, c.g * 3.0 - c.r - c.b);   // 21.11.2026: raja 0.9/0.5 -> 1.25/0.75, koska sävykorjattu ilmakuva (maa/ot_s) on vihreämpi
      float rnd = fract(iOff.z * 7.13), h = (0.14 + 0.22 * rnd) * uTile.y * gr * fade * inside * smoothstep(0.02, 0.09, c.g);   // 21.11.2026 (omistaja: "heinää lyhentää"): 0,5–1,3 m -> 0,14–0,36 m (nurmikko)
      if (h < 0.04) { gl_Position = vec4(2.0, 2.0, 2.0, 1.0); return; }
      float a = iOff.z * 6.2832, ca = cos(a), sa = sin(a);
      vec3 lp = position; lp.xz = vec2(ca * lp.x - sa * lp.z, sa * lp.x + ca * lp.z) * (0.75 + 0.5 * uTile.y);
      lp.y *= h;
      float sway = (sin(uT * 1.6 + w.x * 0.21 + w.y * 0.17) * 0.6 + sin(uT * 3.3 + w.x * 1.1 - w.y * 0.7) * 0.25) * 0.16 * position.y * h;
      lp.x += sway; lp.z += sway * 0.45;
      vec2 tUv = vec2(((w.x - tGrid.x) / tGrid.z + 0.5) / tSize.x, ((w.y - tGrid.y) / tGrid.z + 0.5) / tSize.y);
      vec3 wp = vec3(w.x + lp.x, texture2D(tHeight, tUv).r + lp.y + 0.03, -w.y + lp.z);
      vec4 mv = viewMatrix * vec4(wp, 1.0); vFog = -mv.z;
      // 21.11.2026 (maan pinta): tupsujen väri maa.js:n nurmitekstuurista (maa/tex/nurmi_a, lin. keskiarvo × sävy 1.1/1.12/1.0), ilmakuvasta vain vähän –
      // ennen tupsut olivat sävykorjatun ilmakuvan värisiä ja selvästi vaaleampia kuin uusi nurmi
      vec3 gN = mix(vec3(0.070, 0.090, 0.019), c * vec3(0.55, 0.6, 0.45), 0.2);
      vC = mix(gN * 0.55, gN * vec3(1.45, 1.45, 1.2) + vec3(0.004, 0.008, 0.0), position.y) * mix(vec3(0.9, 1.0, 0.85), vec3(1.15, 1.08, 0.8), rnd);
      gl_Position = projectionMatrix * mv;
    }`;
  const FS = `
    uniform vec3 fogColor; uniform float fogDensity; varying vec3 vC; varying float vFog;
    void main() { float f = 1.0 - exp(-fogDensity * fogDensity * vFog * vFog); gl_FragColor = vec4(mix(vC, fogColor, f), 1.0);
      #include <colorspace_fragment>
    }`;
  const lin = new THREE.Color(scene.fog.color);   // Color holds linear values already
  const layers = [], low = isTouch;
  for (const [T, step, ring, scale, blades] of [[84, low ? 0.7 : 0.45, [0, 0, 34, 42], 1.0, 9], [260, low ? 2.0 : 1.2, [34, 42, 105, 125], 1.5, 10]]) {
    const n = Math.round(T / step), g = mk(blades, 11 + blades), off = new Float32Array(n * n * 3); let sd = 99 + T;
    const r = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
    for (let j = 0, k = 0; j < n; j++) for (let i = 0; i < n; i++, k += 3) { off[k] = (i + r()) * step; off[k + 1] = (j + r()) * step; off[k + 2] = r() * 1000; }
    g.setAttribute('iOff', new THREE.InstancedBufferAttribute(off, 3)); g.instanceCount = n * n;
    const m = new THREE.ShaderMaterial({ vertexShader: VS, fragmentShader: FS, side: THREE.DoubleSide, uniforms: {
      uOrto: { value: orto }, tHeight: { value: maaTexG }, tGrid: { value: new THREE.Vector4(TER.x0, TER.y0, TER.g, 0) }, tSize: { value: new THREE.Vector2(TER.nx, TER.ny) },
      uCore: { value: new THREE.Vector4(HW, YS, YSPAN, 0) }, uRing: { value: new THREE.Vector4(...ring) }, uTile: { value: new THREE.Vector2(T, scale) }, uT: { value: 0 }, uRM: { value: null }, uRB: { value: new THREE.Vector4(0, 0, 0, 0) },
      fogColor: { value: lin }, fogDensity: { value: scene.fog.density || 0 } } });
    const me = noT(new THREE.Mesh(g, m)); me.frustumCulled = false; me.visible = false; scene.add(me); layers.push(me);
  }
  return { layers, mask(t, b) { for (const me of layers) { me.material.uniforms.uRM.value = t; me.material.uniforms.uRB.value = b; } }, update() {   // only when flying low enough to see blades
    const cx = camera.position.x, cy = -camera.position.z, agl = camera.position.y - TZs(cx, cy), on = agl < 170 && inCore(cx, cy);
    for (const me of layers) me.visible = on; },
    tick(t) { for (const me of layers) me.material.uniforms.uT.value = t; } };
})();
function waterify(mat) {          // sky reflection grows towards grazing angles, a faint ripple breaks it up
  mat.onBeforeCompile = sh => {
    sh.uniforms.grassTex = { value: grassTex };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vGw;').replace('#include <project_vertex>', '#include <project_vertex>\nvGw = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vGw; uniform sampler2D grassTex;').replace('#include <map_fragment>', `#include <map_fragment>
      { vec3 v = normalize(cameraPosition - vGw); float rip = texture2D(grassTex, vGw.xz * 0.05).r * 0.6 + texture2D(grassTex, vGw.xz * 0.013 + 0.5).r * 0.4;
        float fr = clamp(pow(1.0 - v.y, 3.0) * 0.85 + 0.18 + (rip - 0.5) * 0.12, 0.0, 0.92);
        vec3 sky = mix(vec3(0.30, 0.38, 0.46), vec3(0.62, 0.72, 0.84), 1.0 - v.y);
        diffuseColor.rgb = mix(diffuseColor.rgb * vec3(0.9, 1.0, 1.05) + 0.03, sky, fr); }`);
  }; mat.needsUpdate = true; return mat;
}
