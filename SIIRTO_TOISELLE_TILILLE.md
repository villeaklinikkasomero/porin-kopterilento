# Porin kopterilento – siirto toiselle Claude-tilille (11.11.2026 klo 13.35)

Liitä tämä tiedosto uuden keskustelun alkuun ja pyydä Claudea lukemaan myös repon `SIIRTO.md` ja `pipeline/README.md`.

## Mikä projekti on
Selaimessa toimiva 3D-helikopteripeli Porin keskustan yllä (three.js r160). Realistisuus tulee avoimesta datasta:
MML:n 3D-rakennukset (LoD2) ja korkeusmalli, OSM, Porin kaupungin ilmakuva (WMS) ja kaupungin valokuvat, sekä Blender-mallit.

## Missä kaikki on
- **GitHub:** `villeaklinikkasomero/porin-kopterilento`. Paikallinen kansio on `C:\Users\ville.somero\Documents\GitHub\porin-kopterilento`, ja muutokset viedään GitHub Desktopilla.
  Kaikki pelin muutokset klo 12 asti ovat GitHubissa: kauppatorin valokuvajulkisivut, päivän kierros ja top-10.
- **Claude-artifakti** "Porin kopterilento", slug `b9ac93cd-98e1-4f31-9f51-c80da5b7706a`. **Artifakti kuuluu vanhalle tilille: uusi tili ei voi päivittää sitä.**
  Uudella tilillä julkaistaan uusi artifakti repon tiedostoista (kaikki repon juuren tiedostot + `ot/`-kansio, yhteensä noin 150 Mt).
  Top-10-tulostaulu käyttää artifaktin tietokantaa (`db`), joten se pitää ottaa uudessa artifaktissa käyttöön uudelleen:
  säännöt `runs` read view / write owner ja `runs/{self}` write interact, lisäksi `user`-kyky.
- **Kaupungin valokuvat:** SharePoint-kansio Kuvat_kopterilento (268 kuvaa, 17 aluetta). Kreditointi "Porin kaupunki".
  Alkuperäisiä kuvia ei viedä GitHubiin.
- **Kesken, ei vielä GitHubissa:**
  1. Repon kansiossa `pipeline/` on AWS-versio grafiikkaputkesta (lisätty tiedostoina, ei commitoitu).
  2. Uusin **Modal-versio** on paketissa `porikit_pipeline.zip`, joka puretaan repon juureen vanhan `pipeline/`-kansion päälle.
     Lisäksi repoon tulevat `blender/gpu_hook.py`, sekä muutetut `blender/gen.py`, `blender/zones.py` ja `blender/lm.py`, `index.html` (lukee `phs.json`) ja `phs.json` (`{}`).
     Nämä on jo kopioitu repo-kansioon, mutta niitä ei ole commitoitu.
  3. `porikit_data.tgz` on Blender-ajojen datapaketti (MML-pickle-tiedostot, joki), joka viedään Modal Volumeen.

## Pelin tila
- Koko alueella tarkka ilmakuva: 88 tiiltä 512 m, ladataan kopterin lähellä. Pehmeät joenrannat korkeusmallista. Eteläranta uudistettu Taavisiltaan asti. Barco-laiva Blender-mallina.
- Kauppatorilla viisi julkisivua kaupungin valokuvista (`ph_*.jpg`, `PHS` index.html:ssä) ja tiilikiveys. Talot 603, 604, 1726, 1599 ja 602 on poistettu Blender-kortteleista tori0, tori3 ja tori4.
- **Päivän kierros:** 36 maamerkin pooli, Suomen päivämäärällä arvotaan 10. Top-10 viisimerkkisellä nimimerkillä.
- Autot ovat vielä vanhat laatikot ja Blender-autot (`cars.js`, 3 tyyppiä). Käyttäjä haluaa realistiset eurooppalaiset autot (viistoperä, farmari, katumaasturi, pakettiauto, kuorma-auto) hillityissä väreissä, Blenderissä itse mallinnettuina.

## Grafiikkaputki porikit (`pipeline/`)
- `porikit/facade.py`: julkisivun oikaisu katoamispisteillä, kerros- ja jaksorytmi, peittävien kohteiden hylkäys, talon korkuinen nauha. Toimii hyvin, kun ihminen antaa talon neljä kulmaa. Täysautomaattinen tila sekoittaa samassa tasossa olevat talot.
- `porikit review`: selaimessa toimiva tarkistustyökalu (localhost:8800). Käytössä kuva, neljä klikkausta, talo kartalta, ÷2/×2 ja hyväksyntä. Komento `porikit export` vie tulokset peliin (`ph_<id>.jpg` + `phs.json`).
- `modal_app.py`: GPU-työt Modalissa. Työ lähtee heti jonoon lisäämisestä, kerrallaan ajetaan yksi L4-kone EU-alueella, ja tunnin välein tarkistetaan jono. Tulokset menevät Volumeen `pori-data/results/<päivä>`, ja GitHub Action tekee niistä päivän pull requestin.
- AWS-vaihtoehto (`Dockerfile`, `infra/`) on olemassa, mutta käyttäjän AWS-tilissä oli ongelmia. **Valittu: Modal.**
- **Testaamatta:** ensimmäinen `modal deploy` ja GPU-renderöinti.

## Seuraavat askeleet (käyttäjän toiveet)
1. Pura `porikit_pipeline.zip` repoon, commitoi ja vie GitHubiin.
2. Modal-käyttöönotto käyttäjän kanssa (`pipeline/README.md`): tili, `modal setup`, `modal deploy`, data Volumeen, GitHub-avaimet. Korjaa mahdolliset virheet.
3. **Kuvatyönkulun täysi automatisointi:**
   - kameran paikannus kuvasta (kadunnimi → renderöidyt näkymät pelin 3D-mallista → LightGlue-tyyppinen täsmäys tai kattolinjojen vertailu → PnP)
   - LoD2-seinät heijastetaan kuvaan, jolloin klikkauksia ei tarvita ja talot erottuvat toisistaan
   - segmentointi (puut, autot, ihmiset) ja paikkaus
   - mittakaava 3D-mallista
   - automaattinen laaduntarkistus
   - kasvojen ja rekisterikilpien sumennus.
   
   Testaa ensin kauppatorin kuvilla, joiden oikeat vastaukset ovat `ph_*.jpg`.
4. Keskustan kadut valokuvista: Gallen-Kallelankatu, Annankatu/Lyseo, Länsipuisto, Mikonkatu, Katariinankatu (puutalot).
5. Torin kellopaviljonki, veistokset ja istutuspuut. Pohjoissivun valkoinen talo 1728.
6. Realistiset eurooppalaiset autot Blenderissä.

## Tärkeät huomiot
- Koordinaatit ovat pelimetrejä: x = (lon − 21.796) · 53278, y = (lat − 61.486) · 111437. Three.js-paikka on (x, korkeus, −y).
- Rakennusindeksit viittaavat `city.js`:n järjestykseen, joten `city.js`:ää ei saa generoida uudelleen tarkistamatta indeksejä.
- Työtilan komentorivi ei pääse MML:ään, OSM:ään tai kaupungin palveluihin. Haku tehdään käyttäjän Claude-selaimella → Lataukset-kansioon → `device_stage_files`. XML-sivulla latauslinkki tehdään `createElementNS(xhtml)`-kutsulla.
- Lisenssiehtojen hyväksynnät (esim. MML-tilaukset) tekee käyttäjä itse.
- GitHub-push vain käyttäjän pyynnöstä. Tiedostojen poisto käyttäjän koneelta vain luvalla.
- Käyttäjä haluaa vastaukset suomeksi, lyhyesti, ja kuvat tai kuvakaappaukset todisteeksi muutoksista.
