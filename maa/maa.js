// maa/maa.js – maan pinta materiaaleina lähellä pelaajaa (21.11.2026, MAAN_PINTA_SUUNNITELMA.md vaihe 2).
//
// Mitä tekee: tarkkojen ilmakuvalaattojen (src/js/033_ilmakuva_tarkka.js, HR.t) maamateriaaliin lisätään varjostin, joka 0–150 m säteellä
// (puhelimella 0–90 m) piirtää maan maankäyttökartan (maa/peite/peite_I_J.png, 0,5 m, 16 luokkaa) mukaisina PBR-materiaaleina (maa/tex/*):
//   - luokkien rajoilla korkeuspohjainen sekoitus (ORM:n B-kanava), raja hieman kohinalla rikottu, ei suoraa 0,5 m porrasta
//   - tiilauksen rikkominen: kaksi siirrettyä näytettä kohinamaskilla + makrovaihtelu kirkkaudessa
//   - valaistus normaalikartasta (aurinko samassa suunnassa kuin ilmakuvan varjot, src/js/020_renderoija.js), AO
//   - keskietäisyydellä (25–150 m) ilmakuvan sumea väri antaa vain sävyn (rajattu ±20 %), kaukana pelkkä ilmakuva
//   - luokat ilmakuva/vesi/rata piirretään ilmakuvana (vesi ja rata ovat omia moduulejaan)
// Autot, varjot ja latvukset katoavat lähietäisyydeltä, koska väri tulee materiaalista eikä kuvasta.
// Puhelin (isTouch): _m-tekstuurit (512 px), ei normaalikarttaa eikä toista näytettä, säde 90 m.
//
// Kutsu: src/js/0337_maa.js (P = { HR, renderer, isTouch }). Laattojen materiaalit luo 033; tämä moduuli vain laajentaa niitä (onBeforeCompile).
// Testaus: window.__maa.pois() / .paalle() vertailuun, window.__maa.tila() lataustila.
import * as THREE from '../three.module.min.js';

// maa/tex: kerrokset tekstuuritaulukossa. kirkkaus = tools/maa/tekstuurit.py:n tavoitekirkkaus (sRGB), toisto metreinä (tex.json)
const KERROKSET = ['ajorata', 'pysakointi', 'jalkakaytava', 'betoni', 'kiveys', 'laatoitus', 'nurmi', 'multa'];
const TEXI = { ajorata: [3.0, 0.30], pysakointi: [3.0, 0.33], jalkakaytava: [2.5, 0.48], betoni: [2.5, 0.50], kiveys: [2.0, 0.42], laatoitus: [2.0, 0.50], nurmi: [2.0, 0.30], multa: [2.5, 0.25] };
// maapeitteen luokka (maa/peite/peite.json) -> [kerros tai null = ilmakuva, sävy (lineaarinen kerroin), toisto-kerroin]
// Puuttuvat tekstuurit (sora, hiekka, metsä, niitty, puu) korvataan toistaiseksi sävytetyllä lähimmällä; kun ambientCG-zipit on ladattu
// ja tools/maa/tekstuurit.py ajettu, lisää ne KERROKSET-listaan ja vaihda tähän.
const LUOKAT = [
  [null],                                         // 0 ilmakuva (ei tietoa)
  ['ajorata', [1, 1, 1], 1],                      // 1 ajorata
  ['jalkakaytava', [1, 1, 1], 1],                 // 2 jalkakäytävä / piha
  ['kiveys', [1, 1, 1], 1],                       // 3 kiveys
  ['pysakointi', [1, 1, 1], 1],                   // 4 pysäköinti
  ['nurmi', [1.1, 1.12, 1.0], 1],                // 5 nurmi (hieman kirkkaampi: testikuvissa tumma)
  ['betoni', [1.08, 0.98, 0.82], 0.6],            // 6 sora (väliaikainen: betoni lämpimänä, tiheämpi)
  ['jalkakaytava', [1.45, 1.25, 0.88], 0.8],      // 7 hiekka (väliaikainen)
  ['multa', [1, 1, 1], 1],                        // 8 multa / istutus
  ['multa', [0.82, 0.86, 0.72], 1.3],             // 9 metsänpohja (väliaikainen)
  ['nurmi', [1.18, 1.10, 0.78], 1.25],            // 10 niitty (väliaikainen: kellertävämpi nurmi)
  ['jalkakaytava', [1, 1, 1], 1],                 // 11 rakennuksen juuri: piha (rakennus peittää)
  [null],                                         // 12 vesi (vesi/vesi.js)
  [null],                                         // 13 rata (rata/rata.js piirtää sepelin)
  ['nurmi', [0.95, 1.05, 0.95], 1],               // 14 urheilu
  ['laatoitus', [0.85, 0.66, 0.48], 1],           // 15 puu (väliaikainen)
];
// maapeite-PNG:n paletti (maapeite.py) -> luokka
const PALETTI = [[255, 0, 255], [60, 60, 64], [150, 150, 155], [175, 120, 95], [95, 95, 120], [90, 170, 70], [200, 180, 140], [235, 215, 160],
  [110, 80, 50], [40, 95, 45], [160, 190, 90], [200, 60, 60], [60, 110, 200], [120, 100, 90], [200, 90, 40], [150, 110, 70]];

export default function kaynnista(P) {
  const { HR, renderer, ROOFT } = P, M = !!P.isTouch, S = M ? 512 : 1024, SN = 512, PX = 1024;
  const R0 = M ? 60 : 110, R1 = M ? 90 : 150;
  const sRGBlin = v => Math.pow(v, 2.2);

  // ---- tekstuuritaulukot (albedo sRGB, normaali, ORM) ----
  const taulukko = (koko, srgb) => { const t = new THREE.DataArrayTexture(new Uint8Array(koko * koko * 4 * KERROKSET.length), koko, koko, KERROKSET.length);
    t.format = THREE.RGBAFormat; t.type = THREE.UnsignedByteType; t.wrapS = t.wrapT = THREE.RepeatWrapping; t.magFilter = THREE.LinearFilter;
    t.minFilter = THREE.LinearMipmapLinearFilter; t.generateMipmaps = true; t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
    if (srgb) t.colorSpace = THREE.SRGBColorSpace; return t; };
  const TA = taulukko(S, true), TN = taulukko(SN, false), TO = taulukko(SN, false);
  const cv = document.createElement('canvas'), cx = cv.getContext('2d', { willReadFrequently: true });
  const lataaKuva = url => new Promise((ok, ei) => { const im = new Image(); im.onload = () => ok(im); im.onerror = () => ei(new Error(url)); im.src = url; });
  const tila = { tex: 0, texVirheet: [], laatat: 0, peite: 0, peiteVirheet: [] };
  let texValmis = false;
  Promise.all(KERROKSET.flatMap((n, k) => [['a', TA, S], ['n', TN, SN], ['orm', TO, SN]].map(async ([laji, T, koko]) => {
    // normaali ja ORM: puhelimella vain ORM (AO + korkeus) – normaalikarttaa ei käytetä
    if (M && laji === 'n') return;
    const kokoUrl = (laji === 'a' && !M) || koko === 1024 ? '' : '_m';
    const im = await lataaKuva(`./maa/tex/${n}_${laji}${M ? '_m' : kokoUrl}.jpg`);
    cv.width = cv.height = koko; cx.drawImage(im, 0, 0, koko, koko);
    T.image.data.set(cx.getImageData(0, 0, koko, koko).data, k * koko * koko * 4); tila.tex++;
  }).map(p => p.catch(e => tila.texVirheet.push(e.message))))).then(() => {
    TA.needsUpdate = TN.needsUpdate = TO.needsUpdate = true; texValmis = true;
    for (const u of kaikki) u.uMaaOn.value = (paalla && u.uMaaP.value) ? 1 : 0;
  });

  // ---- luokkataulukot varjostimelle ----
  const uL = [], uTint = [], uRep = [], uKirk = [];
  for (const [n, tint, rk] of LUOKAT) {
    const k = n ? KERROKSET.indexOf(n) : -1; uL.push(k);
    uTint.push(new THREE.Vector3(...(tint || [1, 1, 1]))); uRep.push(n ? TEXI[n][0] * rk : 1);
    const lum = n ? TEXI[n][1] * (0.2126 * tint[0] + 0.7152 * tint[1] + 0.0722 * tint[2]) : 0.4; uKirk.push(sRGBlin(Math.min(0.95, lum)));
  }

  // ---- maapeitelaatat: PNG (paletti) -> R8-luokkatekstuuri ----
  const pal = new Map(PALETTI.map((c, k) => [(c[0] << 16) | (c[1] << 8) | c[2], k]));
  const lahin = (r, g, b) => { let p = 0, pd = 1e9; PALETTI.forEach((c, k) => { const d = (c[0] - r) ** 2 + (c[1] - g) ** 2 + (c[2] - b) ** 2; if (d < pd) { pd = d; p = k; } }); return p; };
  const peiteVälimuisti = new Map();
  const lataaPeite = key => {
    if (peiteVälimuisti.has(key)) return peiteVälimuisti.get(key);
    const lupaus = fetch(`./maa/peite/peite_${key}.png`).then(r => { if (!r.ok) throw new Error('peite ' + key + ' ' + r.status); return r.blob(); })
      .then(b => createImageBitmap(b, { colorSpaceConversion: 'none', premultiplyAlpha: 'none' }))
      .then(bm => { const c = document.createElement('canvas'); c.width = c.height = PX; const g = c.getContext('2d', { willReadFrequently: true });
        g.drawImage(bm, 0, 0); const d = g.getImageData(0, 0, PX, PX).data, o = new Uint8Array(PX * PX);
        for (let i = 0, j = 0; i < o.length; i++, j += 4) { const v = (d[j] << 16) | (d[j + 1] << 8) | d[j + 2]; const k = pal.get(v); o[i] = k !== undefined ? k : lahin(d[j], d[j + 1], d[j + 2]); }
        const t = new THREE.DataTexture(o, PX, PX, THREE.RedFormat, THREE.UnsignedByteType); t.magFilter = t.minFilter = THREE.NearestFilter; t.generateMipmaps = false;
        t.flipY = false; t.needsUpdate = true; tila.peite++; return t; })
      .catch(e => { tila.peiteVirheet.push(e.message); peiteVälimuisti.delete(key); return null; });
    peiteVälimuisti.set(key, lupaus); return lupaus;
  };

  // ---- varjostin ----
  const L = new THREE.Vector3(0.79, 0.81, 0.62).normalize();      // aurinko kuten 020_renderoija.js (ilmakuvan varjot luoteeseen)
  const GLSL_YHT = `
    varying vec3 vMw;
    uniform float uMaaOn; uniform sampler2D uMaaP; uniform vec2 uMaaT; uniform vec2 uMaaR; uniform vec3 uMaaL3;
    uniform highp sampler2DArray uMaaA; uniform highp sampler2DArray uMaaN; uniform highp sampler2DArray uMaaO;
    uniform int uMaaL[16]; uniform vec3 uMaaTint[16]; uniform float uMaaRep[16]; uniform float uMaaKirk[16];
    float mHash(vec2 p) { p = fract(p * vec2(123.34, 456.21)); p += dot(p, p + 45.32); return fract(p.x * p.y); }
    float mNoise(vec2 p) { vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
      return mix(mix(mHash(i), mHash(i + vec2(1, 0)), f.x), mix(mHash(i + vec2(0, 1)), mHash(i + vec2(1, 1)), f.x), f.y); }
    int mCls(ivec2 p) { p = clamp(p, ivec2(0), ivec2(${PX - 1})); return int(texelFetch(uMaaP, p, 0).r * 255.0 + 0.5); }
    // yhden luokan materiaali: albedo (lin), normaali (tangenttiavaruus), korkeus, AO
    void mMat(int k, vec2 wp, vec3 photo, out vec3 alb, out vec3 nrm, out float h, out float ao) {
      int L = uMaaL[k];
      if (L < 0) { alb = photo; nrm = vec3(0, 0, 1); h = 0.45; ao = 1.0; return; }
      float rep = uMaaRep[k], fl = float(L);
      vec2 uv = vec2(wp.x, -wp.y) / rep;
      vec3 a = texture(uMaaA, vec3(uv, fl)).rgb; vec4 o = texture(uMaaO, vec3(uv, fl));
      #ifndef MAA_PUHELIN
        vec3 n = texture(uMaaN, vec3(uv, fl)).xyz;
        // tiilauksen rikkominen: toinen näyte siirrettynä ja hieman eri mittakaavassa, kohinamaskilla
        float s = smoothstep(0.32, 0.68, mNoise(wp / (rep * 3.7) + fl * 7.13));
        vec2 uv2 = uv * 0.857 + vec2(0.371, 0.613) + fl * 0.13;
        a = mix(a, texture(uMaaA, vec3(uv2, fl)).rgb, s); o = mix(o, texture(uMaaO, vec3(uv2, fl)), s); n = mix(n, texture(uMaaN, vec3(uv2, fl)).xyz, s);
        nrm = normalize(n * 2.0 - 1.0);
      #else
        nrm = vec3(0, 0, 1);
      #endif
      float mv = 0.86 + 0.28 * mNoise(wp / 11.0 + fl * 3.1) + 0.08 * (mNoise(wp / 2.7 + 9.0) - 0.5);    // makrovaihtelu
      alb = a * uMaaTint[k] * mv; h = o.b; ao = o.r;
    }`;
  const GLSL_FRAG = `
    #ifdef USE_MAP
    {
      float md = length(vMw - cameraPosition);
      float near = (1.0 - smoothstep(uMaaR.x, uMaaR.y, md)) * uMaaOn;
      if (near > 0.001) {
        vec3 photo = diffuseColor.rgb;
        vec2 wp = vec2(vMw.x, -vMw.z);
        // luokkarajan rikkominen: näytepistettä siirretään kohinalla (±0,35 m) -> raja ei ole 0,5 m porras
        vec2 jit = (vec2(mNoise(wp * 0.9), mNoise(wp * 0.9 + 17.3)) - 0.5) * 0.7 + (vec2(mNoise(wp * 3.1 + 4.0), mNoise(wp * 3.1 - 8.0)) - 0.5) * 0.25;
        vec2 tp = (vec2(wp.x - uMaaT.x, uMaaT.y - wp.y) + jit) * 2.0 - 0.5;
        ivec2 b0 = ivec2(floor(tp)); vec2 f = fract(tp);
        int c0 = mCls(b0), c1 = mCls(b0 + ivec2(1, 0)), c2 = mCls(b0 + ivec2(0, 1)), c3 = mCls(b0 + ivec2(1, 1));
        vec3 col, nT; float ao;
        if (c0 == c1 && c0 == c2 && c0 == c3) { float h; mMat(c0, wp, photo, col, nT, h, ao); }
        else {
          int cs[4]; cs[0] = c0; cs[1] = c1; cs[2] = c2; cs[3] = c3;
          float ws[4]; ws[0] = (1.0 - f.x) * (1.0 - f.y); ws[1] = f.x * (1.0 - f.y); ws[2] = (1.0 - f.x) * f.y; ws[3] = f.x * f.y;
          for (int i = 1; i < 4; i++) for (int j = 0; j < i; j++) if (cs[i] == cs[j] && ws[j] >= 0.0) { ws[j] += ws[i]; ws[i] = -1.0; break; }
          vec3 A[4], N[4]; float H[4], O[4], hm = -1.0;
          for (int i = 0; i < 4; i++) { if (ws[i] < 0.0) continue; mMat(cs[i], wp, photo, A[i], N[i], H[i], O[i]); H[i] = H[i] * 0.6 + ws[i]; hm = max(hm, H[i]); }
          float bs = 0.0; col = vec3(0); nT = vec3(0); ao = 0.0;
          for (int i = 0; i < 4; i++) { if (ws[i] < 0.0) continue; float bw = max(H[i] - hm + 0.18, 0.0); col += A[i] * bw; nT += N[i] * bw; ao += O[i] * bw; bs += bw; }
          col /= bs; nT = normalize(nT); ao /= bs;
        }
        // valaistus: geometrinen normaali + normaalikartta; tasainen maa = 1,0 (ilmakuva on valaisematon, joten sama kirkkaustaso)
        vec3 Ng = normalize(cross(dFdx(vMw), dFdy(vMw))); if (Ng.y < 0.0) Ng = -Ng;
        vec3 Nw = normalize(vec3(1, 0, 0) * nT.x + vec3(0, 0, -1) * nT.y + Ng * nT.z);
        float amb = 0.62, sk = 0.7, ref = amb + sk * max(dot(Ng, uMaaL3), 0.05);
        float sh = (amb + sk * max(dot(Nw, uMaaL3), 0.0)) / ref;
        col *= sh * mix(1.0, ao, 0.75);
        // keskietäisyys: ilmakuvan sumea sävy (vain kirkkaus, rajattu) -> kaukaa yhtenäinen ilmakuvan kanssa
        int cc = c0; if (uMaaL[cc] >= 0) {
          vec3 pb = textureLod(map, vMapUv, 4.5).rgb; float lp = dot(pb, vec3(0.2126, 0.7152, 0.0722));
          float t = clamp(lp / max(uMaaKirk[cc], 0.01), 0.8, 1.2);
          col *= mix(1.0, t, smoothstep(25.0, uMaaR.x, md) * 0.85);
        }
        diffuseColor.rgb = mix(photo, col, near);
      }
    }
    #endif`;

  const kaikki = new Set();
  const laajenna = (m, key) => {
    if (m.userData.maa) return; m.userData.maa = key;
    const [i, j] = key.split('_').map(Number), x0 = HR.X0 + i * HR.S, ytop = HR.Y0 + (j + 1) * HR.S;
    const U = { uMaaOn: { value: 0 }, uMaaP: { value: null }, uMaaT: { value: new THREE.Vector2(x0, ytop) }, uMaaR: { value: new THREE.Vector2(R0, R1) },
      uMaaL3: { value: L }, uMaaA: { value: TA }, uMaaN: { value: TN }, uMaaO: { value: TO },
      uMaaL: { value: uL }, uMaaTint: { value: uTint }, uMaaRep: { value: uRep }, uMaaKirk: { value: uKirk } };
    m.userData.maaU = U; kaikki.add(U);
    const vanha = m.onBeforeCompile;
    m.onBeforeCompile = (sh, r) => {
      if (vanha) vanha.call(m, sh, r);
      Object.assign(sh.uniforms, U);
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying vec3 vMw;')
        .replace('#include <project_vertex>', '#include <project_vertex>\nvMw = (modelMatrix * vec4(transformed, 1.0)).xyz;');
      sh.fragmentShader = (M ? '#define MAA_PUHELIN\n' : '') + sh.fragmentShader.replace('#include <common>', '#include <common>\n' + GLSL_YHT)
        .replace('#include <alphamap_fragment>', GLSL_FRAG + '\n#include <alphamap_fragment>');
    };
    const vk = m.customProgramCacheKey ? m.customProgramCacheKey.bind(m) : null;
    m.customProgramCacheKey = () => (vk ? vk() : '') + '|maa1' + (M ? 'm' : '');
    m.needsUpdate = true; tila.laatat++;
    lataaPeite(key).then(t => { if (!t || !kaikki.has(U)) return; U.uMaaP.value = t; U.uMaaOn.value = texValmis && paalla ? 1 : 0; });
  };
  let paalla = true;
  // 033 luo laatat etäisyyden mukaan; laajennetaan uudet heti kun ne tulevat (laatta piirtyy vasta kun ilmakuva on latautunut)
  const kierros = () => {
    const nyt = new Set();
    for (const [key, rec] of HR.t) { nyt.add(rec.m); if (!rec.m.userData.maa) laajenna(rec.m, key); }
    // 0335 (Luvianpuistokadun käytävä) ja muut ROOFT-maapinnat (userData.maa): 033 vaihtaa niille tarkan laatan materiaalin (groundTileMat)
    if (ROOFT) for (const [key, L] of ROOFT) { if (!HR.t.has(key)) continue; for (const me of L) { if (!me.userData || !me.userData.maa) continue; const m = me.material;
      if (m && m.map && m !== me.userData.fb) { nyt.add(m); if (!m.userData.maa) laajenna(m, key); } } }
    for (const U of kaikki) { let elossa = false; for (const m of nyt) if (m.userData.maaU === U) { elossa = true; break; } if (!elossa) kaikki.delete(U); }
    // peitelaattojen välimuisti: pidetään vain lähellä olevat (HR.t:n avaimet)
    for (const k of [...peiteVälimuisti.keys()]) if (!HR.t.has(k)) { peiteVälimuisti.get(k).then(t => t && t.dispose()); peiteVälimuisti.delete(k); }
  };
  setInterval(kierros, 400); kierros();

  window.__maa = {
    tila: () => ({ ...tila, texValmis, laattoja: kaikki.size, puhelin: M, sade: [R0, R1] }),
    pois() { paalla = false; for (const U of kaikki) U.uMaaOn.value = 0; },
    paalle() { paalla = true; for (const U of kaikki) U.uMaaOn.value = (texValmis && U.uMaaP.value) ? 1 : 0; },
  };
}
