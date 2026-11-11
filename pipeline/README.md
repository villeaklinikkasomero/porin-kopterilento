# porikit – Porin kopterilennon grafiikkaputki

Kuvien käsittely ja Blender-renderöinnit näytönohjaimella pilvessä (Modal), jotta peliä voi rakentaa nopeasti ilman omaa näytönohjainta.

```
 Porin kaupungin kuvat ──► [tarkistustyökalu omalla koneella] 4 klikkausta / talo ──► porikit export ──► ph_*.jpg + phs.json
                                                                                                         │ git push
 GitHub ◄── päivän PR (päivittyy 2 h välein) ◄── Modal Volume results/ ◄── GPU-työntekijä (käynnistyy heti, ◄──┘
                                                                              sammuu kun jono on tyhjä)
```

## Miksi Modal

- Ei palvelimia eikä koneiden käynnistystä/sammutusta: Python-funktio ajetaan pyydettäessä näytönohjaimella.
- Laskutus sekunneittain vain ajon ajalta → työt ajetaan **heti**, yöajoa ei tarvita (hinta on sama).
- Kerrallaan yksi GPU-kone (`max_containers=1`), joka käy jonon tyhjäksi; tunnin välein halpa CPU-tarkistus, ettei jonoon jää mitään.
- Ajot EU-alueella (kaupungin kuvat pysyvät EU:ssa); alueen valinta maksaa hieman enemmän kuin "missä tahansa".
- Hinta (tarkista Modalin hinnastosta): L4-näytönohjain luokkaa 1 $/h EU-alueella; Starter-tason kuukausikrediitit riittänevät tämän projektin käyttöön.
  Aseta Modalin asetuksista kuukausiraja (*Settings → Usage → Spend limit*).

## Käyttöönotto (kerran, ~15 min)

1. **Modal-tili:** https://modal.com → Sign up (GitHub-tunnuksilla käy). Lisää maksukortti ja aseta kuukausiraja.
2. **Omalla koneella** (Python 3.11+):
   ```
   pip install modal
   modal setup                      # kirjautuminen selaimessa
   cd porin-kopterilento
   modal deploy pipeline/modal_app.py
   ```
   Ensimmäinen käyttöönotto rakentaa kontin (Blender, OpenCV, Chrome) Modalin koneilla, n. 5–10 min. Oma kone ei tee raskasta työtä.
3. **Data Modaliin** (ei gitissä: isoja tai lisensoituja tiedostoja):
   ```
   tar xzf porikit_data.tgz                              # syntyy kansio data/
   modal volume put pori-data data /data
   modal volume put pori-data "<Porin kuvat -kansio>" /photos     # vain jos automaattinen julkisivuajo halutaan pilveen
   ```
   Kuvat kuuluvat Porin kaupungille: varmista kaupungilta, että niitä saa säilyttää pilvipalvelussa EU-alueella.
4. **GitHub** (automaattinen käyttöönotto ja tulosten PR): Modalissa *Settings → API Tokens → New token*;
   repon *Settings → Secrets and variables → Actions → Secrets*: `MODAL_TOKEN_ID` ja `MODAL_TOKEN_SECRET`.
   Siirrä `pipeline/github-workflows/*.yml` kansioon `.github/workflows/`.

## Käyttö

**Julkisivut omalla koneella** (ei tarvitse näytönohjainta):
```
pip install -r pipeline/requirements.txt
cd pipeline
python3 -m porikit.cli review --photos <kuvakansio> --work ../work --game ..
# http://localhost:8800 : kuva → talon julkisivun 4 kulmaa → talo kartalta → Laske → Hyväksy
python3 -m porikit.cli export --work ../work --game ..
```
Rajaa vain puhtaat kerrokset; jos kerros toistuu puolikkaana tai tuplana, paina ÷2 / ×2. Matalat talot (räystäs alle 7,5 m): rajaa räystäästä sokkeliin.

**GPU-työt** (lähtevät heti; tulokset tulevat päivän PR:ään, tai hae itse `modal volume get pori-data results/<päivä> night/`):
```
modal run pipeline/modal_app.py --queue bake      --body '{"zones": ["tori0", "tori3", "tori4"], "samples": 64}'
modal run pipeline/modal_app.py --queue landmarks --body '{"names": ["tehdas", "asema"]}'
modal run pipeline/modal_app.py --queue shots     --body '{"views": [["tori", 75, 40, 14, 230]]}'
modal run pipeline/modal_app.py --queue facades   --body '{"district": "Keskusta"}'
modal run pipeline/modal_app.py --cmd "bake tori0 --samples 64"       # yksi työ, odottaa tuloksen terminaalissa
```
Tai GitHubista: *Actions → porikit run*.

## Tiedostot

- `porikit/` Python-paketti: `facade.py` (oikaisu, rytmi, peittävien kohteiden hylkäys, nauha), `review/` (tarkistustyökalu),
  `jobs.py` (jono, Blender-ajot, testikuvat), `gamedata.py` (pelin rakennusdata), `cli.py`
- `modal_app.py` Modal-sovellus: kontti, GPU-työntekijä, tuntitarkistus, jonoon lisäys
- `github-workflows/` Modal-käyttöönotto, käsiajo, päivän PR
- `Dockerfile`, `infra/` vaihtoehtoinen AWS-toteutus (Batch + Terraform), jos AWS-tili joskus saadaan kuntoon
- Blender-skriptit (`blender/`) toimivat ennallaan: `gpu_hook.py` vaihtaa Cyclesin näytönohjaimelle (`PORI_GPU=1`),
  `zones.py` jättää valokuvajulkisivun saaneet talot pois kortteleista. Skriptit olettavat kehitysympäristön polut (`/home/claude/...`);
  `porikit layout` rakentaa saman hakemistorakenteen konttiin.

## Vielä testaamatta

Julkisivuputki, tarkistustyökalu, jono ja testikuvat on testattu ilman näytönohjainta. Modal-käyttöönottoa ja GPU-renderöintiä ei ole vielä ajettu kertaakaan;
ensimmäinen `modal deploy` voi vaatia pieniä korjauksia (esim. paketin versio).
