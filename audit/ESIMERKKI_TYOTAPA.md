# Esimerkki: miten yksi katu käydään läpi (Valtakatu 13.11.2026)

Tämä on mallitiedosto seuraavalle istunnolle: täsmälleen sama työtapa ja oikeat koodiesimerkit, joilla Antinkatu, Yrjönkatu
ja Valtakatu tehtiin. Lue ensin `SIIRTO_TOISELLE_TILILLE.md`, sitten tämä.

---

## 0. Periaatteet (älä ohita)

1. **Katso aina pari:** pelin kuva ja Street View samasta pisteestä ja suunnasta. Älä arvaa muistista tai vanhoista viistokuvista.
2. **Tunnista talo varmasti** ennen muutosta: keltainen tarra (id) + jalanjälki `city.js` (p/10 = metrit) suhteessa kameraan.
   Väärään taloon tehty korjaus on pahempi kuin ei korjausta (esim. Valtakatu 9: tarra näytti 1716, oikea talo oli 1574).
3. **Pienin riittävä korjaus:** väri/kerrosluku → `styles.json`; klassinen talo → `SPECK`; moderni julkisivu → `SPEC`.
4. **Leivo paikallisesti ja vertaa** samasta kuvakulmasta ennen kuin kirjoitat mitään käyttäjän kansioon.
5. **Älä muuta käyttäjän hyväksymiä asioita:** KARHU-värit (kivi.py), Airionkulma 603 valokuvajulkisivu. Kysy ensin.
6. **Kirjoita kansioon uudella tiedostonimellä outputsista** ja tarkista koko `device_list_dir`:llä (kerran kirjoittui vanha sisältö).
7. **Commit/push tekee käyttäjä** GitHub Desktopissa – sinä et voi. Kerro aina tarkasti, mitkä tiedostot.

---

## 1. Kuvauspisteet (views.json)

```python
# kadun keskilinja city.js:n teistä (r: n = nimi, p = metreinä!), piste 40 m välein, kaksi näkymää / piste
import json, math
from shapely.geometry import LineString
from shapely.ops import unary_union, linemerge
s = open('pori/city.js').read(); C = json.loads(s[s.index('{'):s.rindex('}')+1])
ls = [LineString([(e['p'][k], e['p'][k+1]) for k in range(0, len(e['p']), 2)]) for e in C['r'] if e.get('n') == 'Valtakatu']
m = linemerge(unary_union(ls)); G = list(m.geoms) if m.geom_type == 'MultiLineString' else [m]
V = []; c = 0
for L in G:
    for k in range(int(L.length // 40) + 1):
        d = min(L.length - 1, 8 + k * 40); p = L.interpolate(d)
        q = L.interpolate(min(L.length, d + 2)); r = L.interpolate(max(0, d - 2))
        ang = math.degrees(math.atan2(q.x - r.x, q.y - r.y)) % 360
        for side, off in (('A', -55), ('B', 55)):           # molemmat kadun puolet viistosti
            V.append(dict(k=f'V{c:02d}{side}', x=round(p.x, 1), y=round(p.y, 1), h=round((ang + off) % 360),
                          lat=round(p.y / 111437 + 61.486, 6), lon=round(p.x / 53278 + 21.796, 6)))
        c += 1
json.dump(V, open('work/views.json', 'w'))
```

Huom. yksiköt: **rakennusten** `p` on desimetreinä (jaa 10:llä), **teiden** `p` on jo metreinä.

## 2. Kuvaparit selaimessa

1. Liitä `audit/shot.js` pelin välilehteen (javascript_tool) – määrittää `window.__shot(x, y, suunta)` ja id-tarrat.
2. `python3 audit/nb.py 10 12` → browser_batch-lista (2 näkymää / erä, 50 s raja). Aloita erä `resize_window seed 1280×720`.
3. Street View: `https://www.google.com/maps/@?api=1&map_action=pano&viewpoint=LAT,LON&heading=H&pitch=12&fov=90`, odota 5 s.

## 3. Muistiinpanot (malli: audit/valta_notes.txt)

```
V03A 1535/1517 Valtakatu 26: game LOW BLANK WALL (h 3.8/7.5 wrong) -> styles hh 19.5/25.5 (fixed, zones2 'hh')
V03B 1351: was lyseo pink -> real 4 krs ochre-beige plain (fixed); 1353 stays Lyseo
V05A 1451 Valtakatu 24: real rust-red panels – KARHU colour owner-approved -> NOT changed, asked user
V14A UNSURE: real 1-krs ochre (1294/1577?), game 2-krs arched -> uusintakierros
```
Yksi rivi / näkymä: näkymä, id, mitä todellisuudessa, mitä pelissä, mitä tehtiin. Epävarmat → "uusintakierros".

---

## 4. Korjausmallit (oikeat esimerkit tältä päivältä)

### 4a. Väri, kerrosluku, materiaali → `styles.json`
```json
"1351": {"w": "#d8c69c", "f": 4, "sv": 1, "note": "Valtakatu (Lyseon kortteli), 4 krs vaalea okra rappaus (SV 13.11.2026)"}
"1398": {"w": "#d3cdbf", "sv": 1}
"221":  {"k": "metal", ...}          // pelti, ei tiiltä (look_mat: metal → ei automaattista tiiltä)
```
Avaimet: `w` väri, `k` render/brick/wood/metal, `f` kerrokset, `sv: 1` = tarkistettu Street View'sta, `note` lähde + päivä.

### 4b. Väärä korkeus (ei LoD2:ta) → `styles.json` `hh`
```json
"1535": {"hh": 19.5, "note": "Valtakatu 26, 6 krs tiili + lasitetut parvekkeet (city.js h 3.8 väärin)"}
```
zones2.py lukee `hh`:n ja korvaa `B[i]['h']`:n (vain jos LoD2-kuorta ei ole).

### 4c. Klassinen talo ilman kaaria tms. → `kivi.py` `SPECK`
```python
SPECK[1574] = classic_spec(1574, wall='#e3d7b9', trim='#f4f1ea', rust=False, garch=False, hood=None, pil=False)
# Valtakatu 9: small 1-storey stucco house with a gable, plain windows (Street View 13.11.2026)
```
`garch=False` poistaa kaariovet/-ikkunat, `rust=False` rustiikan, `hood=None` ikkunalistat, `pil=False` pilasterit.

### 4d. Moderni julkisivu → `zones.py` `SPEC` (lay + fit)
```python
# 1581  Valtakatu 7 tower (Street View 13.11.2026): white walls, orange-red panels under the windows in bands, shops below
_V7P = dict(sill=0.9, wh=1.45, nx=2, frame=M('#3a3d40', 0.4, 0.4))
SPEC[1581] = dict(P=dict(wall=M('#e6e4de'), spandrel=M('#c4623f', 0.6), sign=SIGNS, gwall=M('#34373a', 0.4),
                         fascia=M('#e6e4de'), gframe=ALU),
                  layout=lay(25, 'ribbon', gh=4.2, bw=3.0, fh=3.0, P=_V7P),
                  fit=lambda lay_, H, street: lay(H, 'ribbon', gh=4.2 if H > 6 else 0, bw=3.0, fh=3.0, P=_V7P))
```
`fit` sovittaa kerrokset LoD2-kuoren todelliseen korkeuteen. Tiilijulkisivu: `MT('#b8653f', 'brick', 0.8)`.
Parvekkeet: `lay(H, 'punched', ..., cols=every(3, 'B'))`.

### 4e. Katutason liiketila / paviljonki
```python
SPEC[1720] = dict(P=dict(wall=M('#d9d8d3'), sign=SIGNS, gwall=M('#34373a', 0.4), fascia=M('#2f5e45', 0.6),
                         plinth=M('#3a3d40'), gframe=ALU),
                  layout=dict(bw=3.2, rows=[(4.7, 'shop', 'G')], cols=lambda c, nb: 'W', P={}))
```

### 4f. Uusi julkisivutyyppi (moduuli) – Porin Talon "pikseli"-kasetit
```python
_PXC = [M('#a9b2c6', 0.35, 0.45), M('#c3c8d6', 0.35, 0.45), M('#8796ad', 0.35, 0.45), M('#d6d9e1', 0.35, 0.45)]
def m_pixel(mb, col, P):
    bw, fh = mb.bw, mb.fh; nu, nv = 2, 3; cw, ch = bw / nu, fh / nv; r = mb.rnd
    wu = r.randrange(nu) if r.random() < 0.55 else -1
    for a in range(nu):
        for b in range(nv):
            if a == wu: continue
            mb.prot(a*cw+.01, b*ch+.01, (a+1)*cw-.01, (b+1)*ch-.01, r.choice((0.02, 0.06, 0.1)), r.choice(_PXC))
    # + kapea kerroskorkea ikkuna sarakkeeseen wu (ks. zones.py)
MODS['pixel'] = m_pixel
```
`mb.q` = tasainen pinta (syvyys negatiivinen = syvennys), `mb.prot` = ulkoneva laatta, `mb.rnd` = toistettava satunnaisuus.

---

## 5. Tarkistus ennen kirjoitusta

```bash
python3 kivi.py kl0 4                                  # kivilohko, 4 näytettä (~100 s)
# city-lohko:
python3 -c "import sys,json; sys.path.insert(0,'.'); import kivi; Z=json.load(open('pori/city_zones.json'))['zones']; \
            kivi.build_and_bake('c067', Z['c067']['ids'], 4, spec=kivi.spec_for)"
cx=$(grep -o "x = [-0-9.]*" out/bl_kl0.js | cut -d' ' -f3); cy=$(grep -o "y = [-0-9.]*" out/bl_kl0.js | cut -d' ' -f3)
python3 audit/rshot.py out/kl0.glb $cx $cy /home/claude/work/kl0 "-431.2,323.1,1.8,49,10"   # x,y,z,suunta,pitch; ABSOLUUTTINEN polku
python3 audit/diag3.py c067                            # mustat laatat
```
Vertaa renderöintiä Street View -kuvaan. Vasta kun ne vastaavat, kirjoita tiedostot kansioon.

## 6. Modal-ajon jälkeen

- Lokin lopussa pitää lukea **`done: N/N ok`**. `0/127` = kaatui (13.11: `No module named 'chamfer'`).
- Uudet `blender/*.py`-moduulit: pipeline/porikit/jobs.py kopioi kiinteän listan HOMEen, muut HOME/blender/ → zones2.py lisää
  `./blender` sys.pathiin. Testaa import myös siitä hakemistorakenteesta.
- collect → PR → merge → Render päivittyy → Ctrl+F5.

## 7. Raportti käyttäjälle (malli)

> Valtakatu on käyty läpi. Tärkeimmät korjaukset: Valtakatu 26 oli matala umpiseinä (väärä korkeus kartta-aineistossa) →
> nyt 6-kerroksinen tiilitalo. … Kysymys sinulle: Valtakatu 24 … muutetaanko? Uusintakierrokselle: … 
> Commitoi ja pushaa: styles.json, blender/zones.py, blender/kivi.py. Aja: `bake kl0 kivi3 tori0 --samples 64` + `city 64 c`.

Lyhyesti, suomeksi, ensin lopputulos, sitten avoimet kysymykset, sitten tarkat tiedostot ja ajokomennot.

---

## 8. Opit Itsenäisyydenkadulta ja Paanakedonkadulta (13.11.2026)

### 8a. Kuvaparit ilman pelin välilehteä: paikallinen renderöinti
- Pelikuvan voi ottaa paikallisesta pelistä (`game/gshot_v.mjs`, `python3 -m http.server 8765` hakemistossa `/home/claude/game`).
  Symlinkkaa paikallisesti leivottu lohko `game/bl_<zone>.js -> out/bl_<zone>.js` ja `game/styles.json -> pori/styles.json`.
- **Odota, että lohkot ovat latautuneet** (`__stream`: kaikki 260 m säteellä `st` 2 tai 3). Muuten kuvaan tulee karkea
  varalaatikko eikä oikea malli, ja vertailu on väärä.
- Piilota helikopteri ennen kuvaa (ryhmä `userData.noT`, `rotation.order === 'YXZ'`).
- Street View -kuva: odota 2 s → pieni kuvakaappaus → odota **4 s** → kuva skaalassa 0.5. Lyhyempi odotus antaa sumean kuvan.
- Säteenheitto (`work/ray.py`) kertoo, mihin taloon kukin kohta näkymässä osuu (−45…+45°). Käytä sitä tarran rinnalla.

### 8b. Tunnistus
- **Lähin kuva ratkaisee.** Sama talo voi näyttää eri väriltä 30 m ja 6 m päästä (vastavalo). 938: 32 m:stä "valkoinen",
  6 m:stä punainen vaja → punainen oikein. 741/734: vastavalossa "valkoinen", oikeasti siniharmaa.
- Jos kaksi näkymää on ristiriidassa, merkitse **UUSINTA** äläkä arvaa (1687 korjattiin vasta pelivertailun jälkeen).
- Tarkista, mikä seinä kamerasta oikeasti näkyy: kierretyssä jalanjäljessä "kadun puoli" voi olla lyhyt päätyseinä.

### 8c. Kerrokset ja ikkunat (käyttäjä 13.11.2026)
- **Ullakkokerros ei ole täysi kerros.** Puolitoistakerroksinen puutalo = `f: 1, u: 1` (ullakon pienet ikkunat päädyssä),
  ei `f: 2` (piirtää kaksi täyskorkeaa ikkunariviä). Katso, onko ylempi ikkunarivi yhtä korkea kuin alempi.
- `city.py house_spec` käyttää kerroslukua nyt myös, kun talo on Street View -tarkistettu (`sv: 1`), ei vain Y-pakin taloille.
- **Ikkunamäärä:** puutaloissa ikkunaväli on oletuksena 2,9 m (ja joka kolmas väli umpinainen). Laske ikkunat Street Viewsta ja
  aseta `styles.json` `wb` = ikkunaväli metreinä, esim. 7 ikkunaa / 27 m → `wb: 2.6`. Tarkista renderöinnistä.
- `hh`: väärä korkeus ilman LoD2-kuorta (esim. 510: city.js h 3 m, oikeasti 4 krs → `hh: 12`).

### 8d. Julkisivutyyppi, ei pelkkä väri
- Jos talolla ei ole SPECiä, `auto()` arpoo julkisivun (parvekkeet, nauhaikkunat) – väri ei korjaa sitä. Kun tyyppi on väärä,
  kirjoita `zones.py` `SPEC`. Valmiita palasia (zones.py loppu):
  - `_sv_lay(H, gh, fh, cols, P, gmod, gP)` + `_stk(k)` + `_GL` = lasitetut parvekepinot (`gloggia`), tumma pohjakerros `gP=dict(wall=_DK)`
  - `m_passage` = porttikäytävä (syvä syvennys katutasossa), `MODS['classic_pil']` = pilasterit vain nurkkiin
  - `_scale_fit(layout)` = rivit skaalautuvat LoD2-kuoren korkeuteen; `cornice_all` = reunalista myös pihan puolelle
- **Liikehallit** ovat umpinaisia: `_hall(M(väri))` (`lay(H, plain=True)`), muuten niihin tulee kerrostalon ikkunarivit.
- **Kaksivärinen julkisivu / osa seinästä eri väriä:** `runalt=lambda x, y: osa_spec if ehto(x, y) else None` **ja**
  `splitruns=True` (ilman sitä koko seinä saa yhden värin). Käytä ehdossa LoD2-kuoren kulmia (`RAW[i]`), ei city.js-jalanjälkeä
  (ne voivat poiketa 4–6 m). Esimerkki: `_597b()` (Leo's: sininen sisäänkäyntiosa, muu harmaa).
- Puutalot kerrostalolohkoissa: `zones2.spec_for` antaa `k: wood` + `sv: 1` -talolle puutalon julkisivun (`city.house_spec`).
- Syvennykset ovat oikeaa geometriaa: ikkuna-aukot, ovisyvennys, lasitetut parvekkeet 1,5 m, sisäänvedetty liiketila
  (`grecess`), porttikäytävä. Ulkonevat: reunalista, ikkunalistat (`hood`), pilasterit. Tarkista ne parista erikseen.

### 8g. Ikkunoiden määrä ja katutason käyttö – merkitse JOKAISELLE talolle (käyttäjä 13.11.2026)
Joka muistiinpanoriville kirjataan kaksi asiaa, vaikka väri olisi jo oikein:
1. **Ikkunamäärä:** kerrokset (ikkunarivit, katutaso mukaan lukien) ja ikkunoita / kerros näkyvällä sivulla tai päädyssä,
   sekä parvekkeiden rytmi (esim. "6 krs, päädyssä 3 ikkunaa/krs, parvekepino joka 3. akselilla").
   Pelissä: `bw` = akseliväli (seinän pituus / ikkunamäärä), `_stk(k)` = parveke joka k:nnella akselilla, puutaloille `wb`.
2. **Katutason käyttö:** *asunnot* (tavalliset ikkunat + porraskäytävän ovet) vai *liiketila* (näyteikkunat, kyltit, lasiovet,
   nosto-ovet). Tämä on yleisin virhe: auto() piirtää helposti asuntoikkunat liiketilan paikalle tai päinvastoin.
   - Liiketila katutasossa → SPEC `gh=3.6–4.2` + `'shop'`-rivi (`gwall`, `fascia`, `sign`), tai yksikerroksinen myymälä
     `rows=[(H, 'shop', 'G')]` (esim. 2302, 2324).
   - Kylttinauhan väri talteen (`fascia`), esim. 2327: oranssit kylttinauhat 7 liiketilan päällä.
   - Asunnot katutasossa → ei shop-riviä (`gh=0`), kirjaa "asunnot katutasossa (ei liiketiloja)".
   - Verstas / autokorjaamo: isot ruutuikkunat yhdessä rivissä (esim. 2321), halli ilman ikkunoita → `_hall`.
3. Kerrosluku tarkistetaan ikkunariveistä, ei arvata korkeudesta: 2327 oli f3 → todellisuudessa 2 krs; 2321 f2 → 1 krs.
4. Kaukaa (> 50 m) tehty tunnistus on epävarma: sama id voi osua eri rakennukseen lähempää katsottuna (2322). Ristiriita →
   poista muutos ja merkitse uusintakierrokselle.

### 8h. Vanhojen talojen koristeet (Kivi-Pori ja muut ennen 1950 rakennetut, käyttäjä 14.11.2026)
Kirjaa ja tarkista jokaisesta vanhasta kivitalosta erikseen (pelkkä väri ei riitä):
- **Ikkunapielet:** ikkunalistat ja -kehykset (`hood`: suora lista / päätykolmio / kaari), ikkunapenkit, korvakkeet.
- **Reunapielet ja nurkat:** nurkkapilasterit tai -rustiikka (`pil`, `classic_pil` = vain nurkkiin, `rust` = katutason rustiikka).
- **Vaakalistat:** räystäslista (`cornice`, hammaslista `dentils`), kerroslistat, sokkeli (`plinth_h`, väri).
- **Muut koristeet:** peilit eli upotetut paneelit ikkunoiden alla tai välissä (`panels`), kaari-ikkunat ja -ovet (`garch`), erkkerit, parvekkeiden konsolit.
Korjaus `kivi.py` `SPECK` (`classic_spec(...)`). Jos talossa ei ole jotain koristetta, se otetaan pois (`hood=None`, `pil=False`, `rust=False`):
väärä koriste on yhtä paha kuin puuttuva. Muistiinpanoon esim. "1574: suorat ikkunalistat, ei pilastereita, räystäslista + hammaslista, harmaa graniittisokkeli 0,6 m".

### 8e. Värit
- `m: 1` (ilmakuvasta mitattu) poistetaan, kun väri tarkistetaan Street Viewsta.
- Vaaleat ja kylläiset värit tummuvat bakessa varjon puolella: sininen 597 piti kirkastaa (`#3d82f0`) ja harmaa halli vaalentaa.

### 8f. Työjärjestys yhdellä kadulla
1. views.json → säteenheitto (`work/near_p.py`: vain näkymät, joissa talo < 60 m).
2. Street View 5 näkymää / erä → muistiinpanot + styles.json heti.
3. Paikallinen bake muuttuneille lohkoille → pelikuvat samoista pisteistä → parikuvat (`work/pairs_p.py`).
4. Korjaa parikuvista näkyvät virheet (tyyppi, kerrokset, ikkunat, kaksiväriset julkisivut) → bake → uusi parikuva.
5. Kirjoita kansioon vasta tarkistuksen jälkeen; kerro käyttäjälle tiedostot ja `city 64 …` -komento.
