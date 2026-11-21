// ---------- renderer / scene ----------
// Baked model textures by distance: every Blender model carries a 2048 px atlas (22 MB on the GPU with mipmaps) and there are over forty of them,
// which ran integrated GPUs out of texture memory (black ground, missing parts). Far models now hold a 512 px copy; only the nearest few get the full atlas.
const TEXLOD = { L: [], N: isTouch ? 3 : 8, R: 420,
  add(map, x, y) { const im = map && map.image; if (!im || !(im.width > 512)) return;
    const mk = n => { const c = document.createElement('canvas'); c.width = c.height = n; c.getContext('2d').drawImage(im, 0, 0, n, n); return c; };
    const small = mk(isTouch ? 256 : 512); let full = im; if (isTouch && im.width > 1024) { full = mk(1024); if (im.close) im.close(); }
    map.image = small; map.flipY = false; map.needsUpdate = true; this.L.push({ map, full, small, x, y, big: false }); },
  update(cx, cy) { const L = this.L; if (!L.length) return;
    for (const e of L) e.d = Math.hypot(e.x - cx, e.y - cy);
    const near = L.filter(e => e.d < this.R).sort((a, b) => a.d - b.d).slice(0, this.N);
    const up = near.find(e => !e.big), down = L.find(e => e.big && !near.includes(e) && e.d > this.R + 120);
    const e = down || up; if (!e) return;   // one switch per call; free before allocating
    e.big = !e.big; e.map.dispose(); e.map.image = e.big ? e.full : e.small; e.map.needsUpdate = true; } };
const renderer = new THREE.WebGLRenderer({ canvas: $('gl'), antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio || 1, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
const scene = new THREE.Scene();
const SKY = new THREE.Color(0xa9cbe6);
scene.background = SKY;
scene.fog = new THREE.Fog(SKY, 600, 3400);
const camera = new THREE.PerspectiveCamera(62, 1, 1, 7000);
function resize() { const w = innerWidth, h = innerHeight; renderer.setSize(w, h, false); camera.aspect = w / h; camera.updateProjectionMatrix(); }
addEventListener('resize', resize); resize();

scene.add(new THREE.HemisphereLight(0xfff0da, 0xd2c6b2, 2.65));   // warm fill: the oblique photos are the colour reference, and there even the shade sides read cream   // lighter shade side: pale render read as olive in shadow
const sun = new THREE.DirectionalLight(0xffedd2, 1.0); sun.position.set(0.79, 0.81, 0.62);   // matches the sun in the aerial image (shadows fall north-west)
const TREES = { update: () => {} };   // leaf-card trees near the helicopter
const STREAM = window.__stream = [];   // whole-city blocks loaded by distance (streamUpdate)
// aerial haze: distant blocks fade into the sky colour instead of ending at a hard fog line
renderer.toneMapping = THREE.NoToneMapping;   // ACES and AgX were tried: both wash out the baked colours and the aerial photo
scene.fog = new THREE.FogExp2(0xb4cfe4, 0.00042);
// (a sky reflection on dark window texels was tried here: it veiled dark facades in white, so baked blocks are drawn as baked)
function glassify(m) { return m; }
// brick bond (Poly Haven red_brick_03, CC0; luminance only) on the brick-red surfaces of the old brick landmarks: world-space, so no UVs needed,
// and only where the surface is brick red and vertical (the building's own colour and the baked light stay)
const DETB = new THREE.TextureLoader().load('./det_brick.jpg'); DETB.wrapS = DETB.wrapT = THREE.RepeatWrapping; DETB.anisotropy = 4;
// render grain (det_plaster.jpg) on light, unsaturated walls; brick bond on brick-red walls.  Used on every Blender block (the baked atlases are
// shrunk to 1024 px in the game, which washes the brick and render texture out) - 13.11.2026, user: brick missing on Fiini
const DETP = new THREE.TextureLoader().load('./det_plaster.jpg'); DETP.wrapS = DETP.wrapT = THREE.RepeatWrapping; DETP.anisotropy = 4;
function brickify(m) {
  m.onBeforeCompile = sh => { sh.uniforms.detB = { value: DETB }; sh.uniforms.detP = { value: DETP };
    sh.vertexShader = 'attribute float tNB;\nvarying float vNB;\nvarying vec3 vBW;\nvarying vec3 vBN;\n' + sh.vertexShader.replace('#include <begin_vertex>', '#include <begin_vertex>\nvNB = tNB; vBW = ( modelMatrix * vec4( position, 1.0 ) ).xyz; vBN = normalize( mat3( modelMatrix ) * normal );');
    sh.fragmentShader = 'uniform sampler2D detB;\nuniform sampler2D detP;\nvarying float vNB;\nvarying vec3 vBW;\nvarying vec3 vBN;\n' + sh.fragmentShader.replace('#include <alphamap_fragment>',
      '{ vec3 bc = diffuseColor.rgb; float red = clamp( ( bc.r / ( max( bc.g, bc.b ) + 0.015 ) - 1.3 ) * 2.0, 0.0, 1.0 ) * ( 1.0 - abs( vBN.y ) ) * ( 1.0 - vNB );\n' +
      '  vec2 buv = abs( vBN.x ) > abs( vBN.z ) ? vBW.zy : vBW.xy; float bd = texture2D( detB, buv / 2.2 ).r;\n' +
      '  diffuseColor.rgb *= 1.0 + ( bd - 0.5 ) * 1.7 * red; diffuseColor.r *= 1.0 + ( bd - 0.5 ) * 0.25 * red;\n' +
      '  float mx = max( bc.r, max( bc.g, bc.b ) ), mn = min( bc.r, min( bc.g, bc.b ) ), sat = ( mx - mn ) / ( mx + 0.02 );\n' +
      '  float pl = smoothstep( 0.42, 0.68, mx ) * ( 1.0 - smoothstep( 0.12, 0.3, sat ) ) * ( 1.0 - abs( vBN.y ) ) * ( 1.0 - red );\n' +
      '  diffuseColor.rgb *= 1.0 + ( texture2D( detP, buv / 3.0 ).r - 0.5 ) * 0.4 * pl; }\n#include <alphamap_fragment>'); };
  m.customProgramCacheKey = () => 'brickify' + (m.map ? 'm' : '') + m.type;
  return m;
}
const BRICKLM = new Set(['tehdas', 'kehraamo', 'puuvilla', 'vesitorni', 'isokappeli', 'pienikappeli']);   // Blender landmarks in red brick

// sky dome
{
  const g = new THREE.SphereGeometry(6000, 24, 12);
  const c = []; const p = g.attributes.position; const top = new THREE.Color(0x3f86cf), hor = SKY;
  for (let i = 0; i < p.count; i++) { const t = Math.max(0, p.getY(i) / 6000); const col = hor.clone().lerp(top, Math.pow(t, 0.55)); c.push(col.r, col.g, col.b); }
  g.setAttribute('color', new THREE.Float32BufferAttribute(c, 3));
  scene.add(new THREE.Mesh(g, new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide, fog: false, depthWrite: false })));
}

// 19.11.2026 (owner: "a thin veil of cloud"): cirrus as a second shell inside the dome. Stretched fbm, warped once so the streaks curl, projected as a flat
// layer far overhead; it thins towards the horizon and drifts slowly. No texture, one draw call.
{
  const cm = new THREE.ShaderMaterial({ side: THREE.BackSide, transparent: true, depthWrite: false, fog: false, uniforms: { uT: { value: 0 } },
    vertexShader: 'varying vec3 vD; void main(){ vD = position; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }',
    fragmentShader: `varying vec3 vD; uniform float uT;
      float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
      float n(vec2 p){ vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f); return mix(mix(h(i), h(i + vec2(1, 0)), f.x), mix(h(i + vec2(0, 1)), h(i + vec2(1, 1)), f.x), f.y); }
      float fbm(vec2 p){ float a = 0.5, s = 0.0; for (int i = 0; i < 5; i++) { s += a * n(p); p = p * 2.03 + 17.0; a *= 0.5; } return s; }
      void main(){ vec3 d = normalize(vD); if (d.y < 0.02) discard;
        vec2 p = d.xz / (d.y + 0.16) + vec2(uT * 0.004, uT * 0.0015);
        vec2 q = vec2(p.x * 0.55 + p.y * 0.25, p.y * 1.7 - p.x * 0.5);            /* stretched along the wind */
        float w = fbm(q * 0.9 + 3.0), c = fbm(q * 1.6 + vec2(w * 1.6, w * 0.7)), big = fbm(p * 0.35 + 9.0);
        float a = smoothstep(0.46, 0.78, c) * smoothstep(0.34, 0.62, big) * smoothstep(0.03, 0.3, d.y) * 0.62;
        gl_FragColor = vec4(1.0, 1.0, 1.0, a); }` });
  const me = new THREE.Mesh(new THREE.SphereGeometry(5900, 32, 16), cm); me.userData.noT = true; me.renderOrder = -1; me.frustumCulled = false;
  me.onBeforeRender = () => { cm.uniforms.uT.value = performance.now() / 1000; }; scene.add(me);
}

