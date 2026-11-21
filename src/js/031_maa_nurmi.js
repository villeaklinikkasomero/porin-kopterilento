// ---------- ground detail: grass texture where the photo is green ----------
const grassTex = (() => {
  const N = 256, c = document.createElement('canvas'); c.width = c.height = N; const g = c.getContext('2d'), d = g.createImageData(N, N);
  let sd = 7; const rnd = () => (sd = (sd * 16807) % 2147483647) / 2147483647;
  const v = new Float32Array(N * N); for (let i = 0; i < N * N; i++) v[i] = rnd();
  for (let k = 0; k < 2600; k++) { let x = rnd() * N, y = rnd() * N; const a = rnd() * 6.28, L = 3 + rnd() * 7, b = 0.4 + rnd() * 0.6;   // short blades
    for (let t = 0; t < L; t++) { const xi = ((x | 0) % N + N) % N, yi = ((y | 0) % N + N) % N; v[yi * N + xi] = v[yi * N + xi] * 0.4 + b; x += Math.cos(a) * 0.7; y += Math.sin(a) * 0.7; } }
  const w = new Float32Array(N * N);                               // light blur so it reads as turf, not static
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) { let s2 = 0; for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) s2 += v[((y + dy + N) % N) * N + (x + dx + N) % N]; w[y * N + x] = s2 / 9; }
  for (let i = 0; i < N * N; i++) { const q = Math.max(0, Math.min(255, w[i] * 255)); d.data[i * 4] = d.data[i * 4 + 1] = d.data[i * 4 + 2] = q; d.data[i * 4 + 3] = 255; }
  g.putImageData(d, 0, 0); const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.anisotropy = 8; return t; })();
function grassify(mat) {
  mat.onBeforeCompile = sh => {
    sh.uniforms.grassTex = { value: grassTex };
    sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vGw;').replace('#include <project_vertex>', '#include <project_vertex>\nvGw = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying vec3 vGw; uniform sampler2D grassTex;').replace('#include <map_fragment>', `#include <map_fragment>
      { vec3 cc = diffuseColor.rgb; float gr = smoothstep(0.004, 0.03, cc.g - max(cc.r, cc.b) * 0.97) * smoothstep(0.9, 0.5, cc.g * 3.0 - cc.r - cc.b);
        float dist = length(vGw - cameraPosition); float fade = 1.0 - smoothstep(70.0, 320.0, dist);
        float n1 = texture2D(grassTex, vGw.xz * 0.42).r, n2 = texture2D(grassTex, vGw.xz * 0.061 + 0.37).r, n3 = texture2D(grassTex, vGw.xz * 1.7).r;
        float det = 0.62 + 0.38 * n1 + 0.30 * (n2 - 0.5) + 0.22 * (n3 - 0.5) * (1.0 - smoothstep(10.0, 45.0, dist));
        diffuseColor.rgb = mix(cc, cc * det * vec3(0.97, 1.03, 0.93), gr * fade); }`);
  }; mat.needsUpdate = true; return mat;
}
grassify(groundMat); grassify(outerMat);
