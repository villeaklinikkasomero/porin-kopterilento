# HUOM: tehtävät on jo generoitu ja niitä muokataan nyt suoraan JSONina. Älä aja tätä uudelleen – se kirjoittaa käsin tehdyt muutokset yli.
# Käyttö (vain uudelleenrakennukseen): python tools/tarina/gen_tarina.py tarina/data/tehtavat
# Rautalangat: tarina/data/tehtavat/M07–M26 käsikirjoituksesta (tarina/KASIKIRJOITUS.md). 21.11.2026.
# Puuttuvat mekaniikat ovat `toiminto`-vaiheita, jotka moottori ohittaa muutamassa sekunnissa (puuttuuOhita) – tarinan voi pelata läpi alusta loppuun.
import json, sys, os
OUT = sys.argv[1]
OHITA = 3

def r(h, tu, te): return [h, tu, te]
def rep(*rows, estaa=True, ehto=None):
    s = {"tyyppi": "repliikit", "rivit": list(rows)}
    if not estaa: s["estaa"] = False
    if ehto: s["ehto"] = ehto
    return s
def cut(id, *rows, kamera=None, ehto=None):
    s = {"tyyppi": "cut", "id": id, "rivit": list(rows)}
    if kamera: s["kamera"] = kamera
    if ehto: s["ehto"] = ehto
    return s
def kuvaus(te): return {"h": "KERTOJA", "tu": "neutraali", "te": te}   # toimintarivi välianimaatiossa (ei puhujaa)
def soitto(h, *rows): return {"tyyppi": "soitto", "soittaja": h, "rivit": list(rows)}
def viesti(txt, lahettaja=None, kesto=4):
    s = {"tyyppi": "viesti", "viesti": txt, "kesto": kesto}
    if lahettaja: s["lahettaja"] = lahettaja
    return s
def mene(p, teksti, r=8, kulku=None, merkki=None, cp=False, aikaraja=None, ehto=None, **kw):
    s = {"tyyppi": "mene", "paikka": p, "r": r, "teksti": teksti}
    if kulku: s["kulku"] = kulku
    if merkki: s["merkki"] = merkki
    if cp: s["cp"] = True
    if aikaraja: s["aikaraja"] = aikaraja
    if ehto: s["ehto"] = ehto
    s.update(kw); return s
def kulku(k, teksti): return {"tyyppi": "kulku", "kulku": k, "teksti": teksti}
def keraa(teksti, kohteet, kulku=None, cp=False, laskuri=None, ehto=None):
    s = {"tyyppi": "keraa", "teksti": teksti, "kohteet": kohteet}
    if kulku: s["kulku"] = kulku
    if cp: s["cp"] = True
    if laskuri: s["laskuri"] = laskuri
    if ehto: s["ehto"] = ehto
    return s
def kohde(id, p, nimi, r=3, esine=None, dx=0, dy=0, kulku=None):
    k = {"id": id, "paikka": {"paikka": p, "dx": dx, "dy": dy} if (dx or dy) else p, "r": r, "nimi": nimi}
    if esine: k["esine"] = esine
    if kulku: k["kulku"] = kulku
    return k
def toim(nimi, teksti, cp=False, ehto=None, param=None, ohita=OHITA, paikka=None):
    s = {"tyyppi": "toiminto", "nimi": nimi, "teksti": teksti, "puuttuuOhita": ohita}
    if param: s["param"] = param
    if cp: s["cp"] = True
    if ehto: s["ehto"] = ehto
    if paikka: s["paikka"] = paikka
    return s
def valinta(kysymys, *opts): return {"tyyppi": "valinta", "kysymys": kysymys, "vaihtoehdot": list(opts)}
def vo(teksti, asettaa=None, ehto=None, rivit=None, hinta=None):
    o = {"teksti": teksti}
    if asettaa: o["asettaa"] = asettaa
    if ehto: o["ehto"] = ehto
    if rivit: o["rivit"] = rivit
    if hinta: o["hinta"] = hinta
    return o
def aseta(spec, ehto=None):
    s = {"tyyppi": "aseta", "asettaa": spec}
    if ehto: s["ehto"] = ehto
    return s
def pysy(p, s, teksti, r=12, kulku=None, mittari="", tiukka=False):
    o = {"tyyppi": "pysy", "paikka": p, "s": s, "r": r, "teksti": teksti, "mittari": mittari}
    if kulku: o["kulku"] = kulku
    if tiukka: o["tiukka"] = True
    return o
def anna(p, tyyppi, viesti, dx=0, dy=0, yaw=0, vari=None):
    q = {"paikka": p, "dx": dx, "dy": dy, "yaw": yaw, "tyyppi": tyyppi, "viesti": viesti}
    if vari: q["vari"] = vari
    return {"tyyppi": "toiminto", "nimi": "anna_ajoneuvo", "param": q, "puuttuuOhita": 0.5}
def merkki(p, r=4, kulku="jalan"): return {"tyyppi": "merkki", "paikka": p, "r": r, "kulku": kulku}
def automaattinen(viive=2): return {"tyyppi": "automaattinen", "viive": viive}
def hahmo(h, p, dx=0, dy=0, alkaen=None, asti=None, suunta="pelaaja", malli=None):
    q = {"h": h, "paikka": {"paikka": p, "dx": dx, "dy": dy}, "suunta": suunta}
    if alkaen is not None: q["alkaen"] = alkaen
    if asti is not None: q["asti"] = asti
    if malli: q["malli"] = malli
    return q
APP = lambda m, n: {"muuttuja": "VAR_APPROACH_" + m, "yhtakuin": n}     # 1 = hiljainen, 2 = äänekäs
ALUE = {"muuttujat": {"VAR_AREAS_SAVED": "+1"}}

T = []
def teht(id, nimi, luku, vaiheet, *, antaja=None, laukaisu=None, vaatii=None, ehto=None, asettaa=None, palkinto=None, hahmot=None, fail=None, antajaPaikka=None, piilota=None, huom=None):
    t = {"id": id, "nimi": nimi, "luku": luku, "rautalanka": True}
    if antaja: t["antaja"] = antaja
    if vaatii: t["vaatii"] = vaatii
    if ehto: t["ehto"] = ehto
    t["laukaisu"] = laukaisu
    if fail: t["fail"] = fail
    t["vaiheet"] = vaiheet
    a = {"liput": ["FLAG_" + id + "_DONE"]}
    if asettaa:
        for k, v in asettaa.items():
            if k == "liput": a["liput"] += v
            else: a[k] = v
    t["asettaa"] = a
    if palkinto: t["palkinto"] = palkinto
    if antajaPaikka: t["antajaPaikka"] = antajaPaikka
    if hahmot: t["hahmot"] = hahmot
    if piilota: t["piilota"] = piilota
    if huom: t["_huom"] = huom
    if id in ("M08", "M18"): t["merkki"] = "Te"   # Terttu seisoo aina kojullaan (maailma.json), ei toista antajaa
    T.append(t)

# ================= LUKU 2: Kaupunginosat takaisin =================
teht("M07", "Tavarajuna", 2, [
    rep(r("LUMI", "ovela", "Varjo lähettää alkuperäiset kauppakirjat Helsinkiin tavarajunassa. Kansio on viimeisen vaunun avoimella lavalla."),
        r("TAPSA", "iloinen", "Mää ajan, sää nappaat. Mul on haavi takakontissa.")),
    mene("LOC_ASEMA", "Mene rautatieasemalle – Tapsa odottaa avoautolla", r=30, kulku="maa", merkki="Asema", cp=True),
    toim("juna_rinnalla", "Pysy junan rinnalla radan vieressä huoltotiellä (etäisyysmittari)", cp=True),
    toim("nappaa_kansio", "Nappaa kansio haavilla, kun mittari on vihreällä"),
    aseta({"esineet": ["ITEM_KAUPPAKIRJAT_1"]}),
    rep(r("TAPSA", "yllättynyt", "Saatiin se! Kalastan tästä lähtien vaan papereita.")),
], antaja="LUMI", laukaisu=merkki("LOC_PIILO"), vaatii=["FLAG_CH1_DONE"], asettaa={"esineet": ["ITEM_KAUPPAKIRJAT_1"]},
   palkinto={"raha": 300, "teksti": "Ensimmäiset kauppakirjat · Luku 2 käynnissä"},
   fail=[{"ehto": "kulkuneuvo_rikki", "alkaen": 2}],
   huom="Käsikirjoitus: Tapsa ajaa avoautoa ja Rami nappaa. Rautalanka: juna_rinnalla ja nappaa_kansio puuttuvat (rata/juna-moduulin juna olemassa).")

teht("M08", "Toripaniikki", 2, [
    rep(r("TERTTU", "huolestunut", "Varjo sai meijän torilupien uusinnat \"hukkumaan\". Hakemukset pitää olla kaupungintalolla neljältä, tai torikesä on mennyttä.")),
    keraa("Kerää hakemukset viideltä kojulta", [
        kohde("h1", "LOC_TORI", "Hakemus 1", dx=-20, dy=10), kohde("h2", "LOC_TORI", "Hakemus 2", dx=0, dy=18),
        kohde("h3", "LOC_TORI", "Hakemus 3", dx=22, dy=8), kohde("h4", "LOC_TORI", "Hakemus 4", dx=18, dy=-14),
        kohde("h5", "LOC_TERTUN_KOJU", "Hakemus 5", dx=2)], laskuri="Hakemukset", cp=True),
    mene("LOC_KAUPUNGINTALO", "Vie hakemukset Junneliuksen palatsiin ennen kello 16 (3 min)", r=10, kulku="maa", merkki="Kaupungintalo", aikaraja=180,
         aikarajaTeksti="Kello löi neljä. Terttu laittaa kahvit – yritetään uudestaan."),
    rep(r("TERTTU", "iloinen", "Pojat, huomenna kahvit talon piikkiin.")),
], laukaisu=merkki("LOC_TERTUN_KOJU", r=5),
   vaatii=["FLAG_M07_DONE"], asettaa=ALUE, palkinto={"raha": 150, "teksti": "Kauppatori pelastettu (1/5)"},
   huom="Törmäyksessä hakemus putoaa (puuttuu: pudotus/poiminta). Merkki: Terttu seisoo aina kojullaan (maailma.json).")

teht("M09", "Gaala-ilta", 2, [
    rep(r("LUMI", "ovela", "Varjo pitää sijoittajagaalan taidemuseolla. Hae teatterin puvustamosta frakki ja nimeä itsesi joksikin, mikä kuulostaa rahalta.")),
    mene("LOC_TEATTERI", "Hae valepuku Porin Teatterin puvustamosta", r=8, kulku="maa", merkki="Teatteri"),
    keraa("Ota frakki puvustamosta", [kohde("frakki", "LOC_TEATTERI", "Frakki", r=6, esine="ITEM_FRAKKI")]),
    mene("LOC_TAIDEMUSEO", "Mene gaalaan taidemuseolle", r=8, kulku="jalan", merkki="Gaala", cp=True),
    valinta("Ovimies: \"Ja te olette…?\"",
            vo("\"Olen Kuusinen-sijoitusten edustaja.\"", {"muuttujat": {"VAR_GAALA_ROOLI": 1}}),
            vo("\"Tulin korjaamaan kaiuttimia.\"", {"muuttujat": {"VAR_GAALA_ROOLI": 2}}),
            vo("\"Olen taiteilija.\"", {"muuttujat": {"VAR_GAALA_ROOLI": 3}})),
    toim("salakuuntelu", "Seuraa Varjoa salissa ja pysy kuuloetäisyydellä (kuuntelumittari 100 %)", cp=True),
    cut("CUT_M09_A",
        r("VARJO", "ovela", "Pori saa kauppakeskuksen, jollaista ei ole nähty. Kukaan ei kaipaa vanhaa toria, kun on liukuportaat."),
        r("HARJU", "huolestunut", "Viktor, ne kauppakirjat… eikö niissä ollut jotain epäselvää?"),
        r("VARJO", "vihainen", "Hanna. Hymyile.")),
], antaja="LUMI", laukaisu=merkki("LOC_PIILO"), vaatii=["FLAG_M07_DONE"], asettaa=ALUE,
   palkinto={"raha": 200, "teksti": "Taidemuseon kortteli pelastettu"},
   hahmot=[hahmo("VARJO", "LOC_TAIDEMUSEO", dx=6, alkaen=5), hahmo("HARJU", "LOC_TAIDEMUSEO", dx=8, dy=2, alkaen=5)],
   fail=[{"ehto": "poistui", "paikka": "LOC_TAIDEMUSEO", "r": 80, "alkaen": 5}],
   huom="Hahmot VARJO ja HARJU tarvitsevat juhla-asut (puuttuu). Valinta muuttaa vain repliikkejä (VAR_GAALA_ROOLI).")

teht("M10", "Pienoislentokone", 2, [
    rep(r("TAPSA", "ovela", "Lumi kaivo Varjon kuorma-autojen reitit. Mul on vanha radio-ohjattava kone vintillä – laitetaan siihen Lumin lähetin.")),
    toim("rc_lentokone", "Ohjaa RC-lentokonetta Pohjoisrannan yllä ja pudota lähetin kolmen Varjon kuorma-auton katolle (120 s)", cp=True),
    rep(r("LUMI", "iloinen", "Signaali on kunnossa. Nyt nähdään, minne Varjo vie tavaransa.")),
], antaja="TAPSA", laukaisu=merkki("LOC_KORJAAMO_OVI"), antajaPaikka={"paikka": "LOC_KORJAAMO_OVI", "dx": 3.2, "dy": -1.5},
   vaatii=["FLAG_M09_DONE"], asettaa=ALUE, palkinto={"raha": 150, "teksti": "Pohjoisranta pelastettu"},
   huom="Uusi kulkuneuvo: RC-lentokone (malli + ohjaus puuttuvat).")

teht("M11", "Sillankilpa", 2, [
    rep(r("RADIO", "iloinen", "Kaupungin syysajot käynnistyvät! Reitti on suljettu muulta liikenteeltä, ja yhtenä kuljettajana on Varjo Holdingsin oma kuski!")),
    mene("LOC_ISOSILTA", "Aja lähtöviivalle Isosillalle", r=15, kulku="auto", merkki="Lähtö"),
    {"tyyppi": "portit", "kulku": "auto", "r": 14, "cp": True, "teksti": "Voita kolmen kierroksen kilpa: Isosilta → Eteläranta → Pohjoisranta",
     "portit": ["LOC_ETELARANTA", "LOC_POHJOISRANTA", "LOC_ISOSILTA", "LOC_ETELARANTA", "LOC_POHJOISRANTA", "LOC_ISOSILTA", "LOC_ETELARANTA", "LOC_POHJOISRANTA", "LOC_ISOSILTA"],
     "kilpailija": {"hahmo": "VARJO", "aika": 330, "voitti": "Varjon kuski ehti ensin. Yritä uudelleen."}},
    keraa("Poimi Varjon kuskin pudottama kulkukortti maalista", [kohde("kortti", "LOC_ISOSILTA", "Kulkukortti", r=6, esine="ITEM_KULKUKORTTI", dx=8)], kulku="maa"),
    rep(r("RAMI", "neutraali", "Hyvä auto. Huono kuski.")),
], laukaisu=merkki("LOC_ISOSILTA", r=12, kulku="auto"), vaatii=["FLAG_M07_DONE"], asettaa={**ALUE, "esineet": ["ITEM_KULKUKORTTI"]},
   palkinto={"raha": 250, "teksti": "Isosilta pelastettu · Varjon kulkukortti"},
   fail=[{"ehto": "kulkuneuvo_rikki"}],
   huom="Kilpailija on ajastin (moottorin portit-vaihe). Varjon kuskin auto radalla puuttuu (bottiauto reitillä). Pohjoisrannan paikka on arvio.")

teht("M12", "Paintball-turnaus", 2, [
    rep(r("TAPSA", "ovela", "Varjo osti nuorisotalon ja haastaa sen avaimista. Paintball, kaks joukkuetta, kolme erää. Ei mikään ongelma.")),
    mene("LOC_TEHDAS", "Mene vanhalle tehdasalueelle", r=25, kulku="maa", merkki="Paintball"),
    toim("paintball", "Voita kaksi kolmesta erästä (lipun ryöstö): väriosuma palauttaa lähtöön", cp=True),
    rep(r("VARTIJA", "yllättynyt", "Minuun osui. Toistan: minuun osui.")),
    rep(r("RADIO", "iloinen", "Nuorisotalon avaimet palasivat nuorille! Varjolle ei tänään mennyt hyvin.")),
], antaja="TAPSA", laukaisu=merkki("LOC_KORJAAMO_OVI"), antajaPaikka={"paikka": "LOC_KORJAAMO_OVI", "dx": 3.2, "dy": -1.5},
   vaatii=["FLAG_M08_DONE", "FLAG_M10_DONE"], asettaa={**ALUE, "liput": ["FLAG_CH2_DONE"]},
   palkinto={"raha": 300, "teksti": "Nuorisotalo pelastettu · Luku 3 avautui"},
   hahmot=[hahmo("VARTIJA", "LOC_TEHDAS", dx=10, alkaen=2), hahmo("VARTIJA", "LOC_TEHDAS", dx=14, dy=4, alkaen=2, malli="npc_vartija_b"),
           hahmo("VARTIJA", "LOC_TEHDAS", dx=12, dy=-4, alkaen=2, malli="npc_vartija_c")],
   huom="Paintball-pelimuoto (aseet → väripistooli, lippu, erät, joukkuebotit) puuttuu kokonaan.")

# ================= LUKU 3: Isot keikat =================
CH3 = cut("CUT_CH3_A", kuvaus("[Lumin piilo. Valkotaululle on kiinnitetty kuvia ja karttoja.]"),
          r("LUMI", "ovela", "Kaksi tapaa. Hiljainen: kukaan ei huomaa mitään. Äänekäs: kaikki huomaavat, mutta liian myöhään."),
          kamera={"paikka": "LOC_PIILO", "kohti": "LOC_PIILO"})
def tapa(m): return valinta("Miten keikka tehdään?",
                            vo("Hiljainen (vähemmän tähtiä)", {"muuttujat": {"VAR_APPROACH_" + m: 1}}),
                            vo("Äänekäs (nopeampi, enemmän tähtiä)", {"muuttujat": {"VAR_APPROACH_" + m: 2}}))

teht("M13", "Korukeikka", 3, [
    CH3,
    rep(r("LUMI", "vihainen", "Varjo \"lainasi\" Satakunnan Museolta vanhat hopeakorut omaan näyttelyynsä. Laina-aika on päättynyt, ja palautamme ne.")),
    tapa("M13"),
    mene("LOC_TUHOLAISTORJUJA", "Valmistelu: hae tuholaistorjujan haalarit ja pakettiauto", r=10, kulku="maa", merkki="Ötökkä-Oy", ehto=APP("M13", 1)),
    anna("LOC_TUHOLAISTORJUJA", "van", "🚐 Tuholaistorjujan paku", dx=6, vari="#e8e2c8") | {"ehto": APP("M13", 1)},
    mene("LOC_KORJAAMO", "Valmistelu: hae moottoripyörät Tapsan korjaamolta", r=12, kulku="maa", merkki="Korjaamo", ehto=APP("M13", 2)),
    toim("moottoripyora", "Nouse moottoripyörän selkään", ehto=APP("M13", 2)),
    mene("LOC_VARJOTORNI", "Mene Varjo-tornin näyttelykerrokseen", r=15, kulku="maa", merkki="Varjo-torni", cp=True),
    toim("saippuakupla", "Käynnistä saippuakuplakone – vartijat jahtaavat kuplia", ehto=APP("M13", 1)),
    toim("savuverhot", "Laukaise värilliset savuverhot", ehto=APP("M13", 2)),
    keraa("Kerää korut kuudesta vitriinistä", [kohde(f"v{i}", "LOC_VARJOTORNI", f"Vitriini {i}", r=3, dx=dx, dy=dy)
          for i, (dx, dy) in enumerate([(-6, 4), (-3, 7), (2, 8), (6, 5), (7, 0), (4, -5)], 1)], laskuri="Vitriinit", cp=True),
    toim("varjo_mittari", "Pakene!", param={"tahdet": 2}, ehto=APP("M13", 1), ohita=0.5),
    toim("varjo_mittari", "Pakene!", param={"tahdet": 4}, ehto=APP("M13", 2), ohita=0.5),
    mene("LOC_MUSEO_TAKAOVI", "Vie korut Satakunnan Museon takaovelle", r=8, kulku="maa", merkki="Museon takaovi"),
    rep(r("RADIO", "iloinen", "Satakunnan Museon kadonneet korut löytyivät aamulla ovelta pakattuina rusetilla!")),
], antaja="LUMI", laukaisu=merkki("LOC_PIILO"), vaatii=["FLAG_CH2_DONE"], asettaa={"liput": ["FLAG_MUSEOESINEET_PALAUTETTU"]},
   palkinto={"raha": 400, "teksti": "Museon korut palautettu"}, fail=[{"ehto": "kulkuneuvo_rikki", "alkaen": 7}],
   huom="Kiinni jääminen (Varjo-mittarin jahti) puuttuu → FAIL ei vielä laukea. Moottoripyörä ei ole pelissä.")

teht("M14", "Hotelli-ilta", 3, [
    CH3,
    mene("LOC_TEATTERI", "Valmistelu A: hae hotellin henkilökunnan asut teatterilta", r=8, kulku="maa", merkki="Teatteri"),
    keraa("Ota asut", [kohde("asut", "LOC_TEATTERI", "Henkilökunnan asut", r=6, esine="ITEM_HOTELLIASU")]),
    toim("hakkerointi", "Valmistelu B: Lumi hakkeroi kamerat – yhdistä johdot", cp=True),
    mene("LOC_HOTELLI", "Mene Hotelli Varjoon henkilökunnan ovesta", r=10, kulku="jalan", merkki="Hotelli Varjo", cp=True),
    toim("naamioituminen", "Kulje aulan läpi henkilökunnan asussa ja tarjoile kolmelle vieraalle (naamioitumismittari)"),
    toim("holvi_rytmipeli", "Avaa holvi kulkukortilla ja Lumin koodilla (rytmipeli)", cp=True),
    mene("LOC_HOTELLI", "Vie kauppakirjat ulos pyykkikärryssä", r=8, kulku="jalan", merkki="Pyykkiovi") | {"paikka": {"paikka": "LOC_HOTELLI", "dx": 25, "dy": -10}},
    cut("CUT_M14_A",
        r("HARJU", "yllättynyt", "Te ette ole hotellin henkilökuntaa."),
        r("RAMI", "neutraali", "Emme."),
        r("HARJU", "huolestunut", "…Toinen ovi vasemmalla on nopeampi.")),
    aseta({"liput": ["FLAG_HARJU_DOUBT"]}),
], antaja="LUMI", laukaisu=merkki("LOC_PIILO"), vaatii=["FLAG_M13_DONE"], ehto={"esine": "ITEM_KULKUKORTTI"},
   asettaa={"esineet": ["ITEM_KAUPPAKIRJAT_2"], "liput": ["FLAG_HARJU_DOUBT"]}, palkinto={"raha": 400, "teksti": "Toiset kauppakirjat"},
   hahmot=[hahmo("HARJU", "LOC_HOTELLI", dx=20, dy=-6, alkaen=8)],
   huom="Hotellin sisätila puuttuu (aula, holvi). Naamioituminen: pelaajan hahmon asu vaihtuu (malli puuttuu).")

teht("M15", "Panssariauto", 3, [
    CH3,
    rep(r("TAPSA", "iloinen", "Varjon panssariauto kuljettaa kokoustallenteet. Magneetti kiinni, ja Lumi sammuttaa moottorin kauko-ohjauksella. Kukaan ei ees huomaa.")),
    anna("LOC_KORJAAMO_PIHA", "van", "🚐 Tapsan hinausauto (rautalanka: pakettiauto)", yaw=0.14, vari="#d8b030"),
    mene("LOC_POHJOISRANTA", "Aja hinausautolla Pohjoisrannalle panssariauton perään", r=30, kulku="auto", merkki="Pohjoisranta", cp=True),
    {"tyyppi": "seuraa", "teksti": "Pysy panssariauton perässä (alle 60 m)", "kohde": "Panssariauto", "reitti": ["LOC_POHJOISRANTA", {"paikka": "LOC_POHJOISRANTA", "dx": 200}, {"paikka": "LOC_POHJOISRANTA", "dx": 380, "dy": -60}],
     "nopeus": 9, "min": 0, "max": 60, "armo": 6, "mittari": "Etäisyys", "karkasi": "Panssariauto katosi. Yritä uudelleen."},
    toim("magneetti", "Kiinnitä magneetti (toimintonappi, kun etäisyys alle 3 m)", cp=True),
    mene("LOC_KORJAAMO", "Hinaa panssariauto korjaamolle – kuljettaja lähtee kävellen kotiin", r=12, kulku="auto", merkki="Korjaamo"),
], antaja="TAPSA", laukaisu=merkki("LOC_KORJAAMO_OVI"), antajaPaikka={"paikka": "LOC_KORJAAMO_OVI", "dx": 3.2, "dy": -1.5},
   vaatii=["FLAG_M14_DONE"], asettaa={"esineet": ["ITEM_TALLENTEET"]}, palkinto={"raha": 400, "teksti": "Kokoustallenteet"},
   fail=[{"ehto": "kulkuneuvo_rikki", "alkaen": 3}],
   huom="Hinausauto ja panssariauto (mallit + hinaus) puuttuvat. Seuraa-vaiheen panssariauto näkyy nyt vain merkkinä.")

teht("M16", "Satamalaituri", 3, [
    CH3,
    rep(r("LUMI", "ovela", "Varjon kontissa on kauppakeskuksen pienoismalli ja kokousmuistiot. Kontti on liian painava autolle, joten se nostetaan ilmaan.")),
    mene("LOC_ETELARANTA", "Hae helikopteri Lumin tuttavalta Etelärannan laiturilta", r=12, kulku="maa", merkki="Laituri"),
    toim("anna_kopteri", "Nouse helikopteriin"),
    mene("LOC_VARASTO", "Lennä Varjon varastolle", r=40, kulku="heli", merkki="Kontti", cp=True),
    toim("vaijeri", "Laske vaijeri ja kiinnitä kontti (tarkkuuslasku)", cp=True),
    mene("LOC_PIILO", "Lennä kontti joen yli Lumin piilolle – vältä nostureita", r=40, kulku="heli", merkki="Piilo"),
], antaja="LUMI", laukaisu=merkki("LOC_PIILO"), vaatii=["FLAG_M15_DONE"], asettaa={"esineet": ["ITEM_PIENOISMALLI"]},
   palkinto={"raha": 450, "teksti": "Pienoismalli ja muistiot"}, fail=[{"ehto": "kulkuneuvo_rikki", "alkaen": 4}],
   huom="Kopterin vaijeri ja kontti (fysiikka, malli) puuttuvat. anna_kopteri: kopterin siirto laiturille puuttuu.")

teht("M17", "Pilvenpiirtäjä", 3, [
    CH3,
    tapa("M17"),
    mene("LOC_VARJOTORNI", "Pääse tornin 12. kerrokseen", r=15, kulku="maa", merkki="Varjo-torni", cp=True),
    toim("torni_sisatila", "Kulje 12. kerrokseen (sisätila)"),
    pysy("LOC_VARJOTORNI", 60, "Suojaa Lumia 60 s, kun hän kopioi palvelimen – ohjaa vartijat harhaan äänillä ja hissinapeilla", r=20, mittari="Kopiointi"),
    toim("pyykkikuilu", "Poistu tornista pyykkikuilua pitkin", ehto=APP("M17", 1)),
    toim("laskuvarjo_katolta", "Hyppää katolta laskuvarjolla joen yli", ehto=APP("M17", 2)),
    mene("LOC_PIILO", "Palaa Lumin piilolle", r=12, kulku="maa", merkki="Piilo", ehto=APP("M17", 1)),
    mene("LOC_KIRJURINLUOTO", "Laskeudu Kirjurinluodolle", r=40, merkki="Kirjurinluoto", ehto=APP("M17", 2)),
    rep(r("LUMI", "yllättynyt", "Sain sen. Ja löysin jotain muutakin. Varjo tietää, keitä te olette.")),
], antaja="LUMI", laukaisu=merkki("LOC_PIILO"), vaatii=["FLAG_M16_DONE"], asettaa={"esineet": ["ITEM_PALVELINDATA"], "liput": ["FLAG_CH3_DONE"]},
   palkinto={"raha": 500, "teksti": "Palvelindata · Luku 4 avautui"},
   hahmot=[hahmo("LUMI", "LOC_VARJOTORNI", dx=3, alkaen=4, asti=4)],
   huom="Tornin sisätila puuttuu. Laskuvarjo on pelissä (laskuvarjo/), mutta ei liitetty tarinaan.")

# ================= LUKU 4: Petos =================
teht("M18", "Ansa", 4, [
    cut("CUT_M18_A",
        kuvaus("[Ilta torilla. Varjo seisoo kojujen keskellä hymyillen. Kameramiehiä on joka puolella.]"),
        r("VARJO", "ovela", "Rami Koski! Ja hänen kummallisesti kadonneet museokorunsa. Hups, tarkoitin minun."),
        kuvaus("[Varjon vartijat nostavat Tapsan auton takakontista \"varastettuja\" esineitä. Ne ovat väärennettyjä kopioita. Uutiskopteri kuvaa.]"),
        r("TAPSA", "vihainen", "Rami, ne on feikkejä! Juokse!"),
        kamera={"paikka": "LOC_TORI", "kohti": "LOC_TERTUN_KOJU"}),
    aseta({"liput": ["FLAG_TAPSA_CAPTURED"]}),
    toim("varjo_mittari", "Pakene torilta!", param={"tahdet": 5, "kesto": 90}, ohita=0.5),
    toim("karista_jahtaajat", "Karista Varjo-mittari: kulje sillan alta ja pysy uutiskopterin katveessa", cp=True),
    mene("LOC_PIILO", "Mene Lumin piilolle", r=12, kulku="maa", merkki="Piilo"),
    rep(r("LUMI", "huolestunut", "Tapsa on poissa. Ja koko kaupunki luulee sinua varkaaksi. Sinun pitää kadota hetkeksi.")),
], laukaisu=merkki("LOC_TERTUN_KOJU", r=8), vaatii=["FLAG_CH3_DONE"],
   hahmot=[hahmo("VARJO", "LOC_TORI", dx=4, asti=0), hahmo("TAPSA", "LOC_TORI", dx=8, dy=3, asti=0), hahmo("VARTIJA", "LOC_TORI", dx=6, dy=-3, asti=3)],
   huom="Tähdet 5 ja jahtaajat (vartijabotit, uutiskopteri) puuttuvat. Tapsan pitäisi kadota maailmasta kunnes M23 (FLAG_TAPSA_CAPTURED): tehtävien antajana hän ei näy, koska M19–M23 antajat ovat muita.")

teht("M19", "Piilossa joella", 4, [
    rep(r("TERTTU", "iloinen", "Mun miehen vanha venevaja. Kukaan ei oo käyny siellä sitten -98. Korjaa itsellesi vene, niin pääset liikkumaan joella.")),
    keraa("Korjaa vene: kerää osat rannalta (4 kpl)", [kohde(f"o{i}", "LOC_ETELARANTA", f"Veneen osa {i}", r=3, dx=dx, dy=dy)
          for i, (dx, dy) in enumerate([(-15, -6), (-30, -2), (12, -8), (25, -4)], 1)], laskuri="Osat", cp=True),
    toim("vene", "Laske vene vesille"),
    mene("LOC_POHJOISRANTA", "Auta kalastajaa: hae verkko joen pohjoisrannalta", r=20, merkki="Kalastaja"),
    aseta({"muuttujat": {"VAR_ALLIES": "+1"}}),
    mene("LOC_KIRJURINLUOTO", "Etsi kadonnut koira Kirjurinluodolta", r=30, merkki="Koira"),
    aseta({"muuttujat": {"VAR_ALLIES": "+1"}}),
    toim("soutukilpa", "Voita soutukilpa joella"),
    aseta({"muuttujat": {"VAR_ALLIES": "+1"}}),
    rep(r("RADIO", "huolestunut", "Huhut Rami Koskesta jakavat kaupunkia. Torikauppiaat sanovat, että hän on hyvä poika.")),
], antaja="TERTTU", laukaisu=merkki("LOC_ETELARANTA", r=6), antajaPaikka={"paikka": "LOC_ETELARANTA", "dx": 3},
   vaatii=["FLAG_M18_DONE"], palkinto={"raha": 200, "teksti": "Vene ja kolme uutta liittolaista"},
   huom="Vene kulkuneuvona tarinassa (vene.js + perämoottori ovat pelissä, kulku 'vene' puuttuu moottorista). Liittolaiset ovat rautalangassa pelkkiä käyntejä.")

teht("M20", "Vapaapudotus", 4, [
    rep(r("LUMI", "huolestunut", "Varjon kuriiri vie todisteet väärennöksistä Varjon yksityiskoneella pois maasta. Kone lähtee lentoasemalta viidentoista minuutin päästä."),
        r("RAMI", "neutraali", "Sitten se ei lähde."),
        r("LUMI", "ovela", "Se lähtee. Mutta se tulee takaisin. Minulla on suunnitelma. Toivottavasti sinulla ei ole korkean paikan kammoa.")),
    mene("LOC_LENTOASEMA", "Aja keskustasta lentoasemalle (3 min)", r=40, kulku="maa", merkki="Lentoasema", aikaraja=180, cp=True),
    mene("LOC_LENTOASEMA_HALLI", "Mene huoltohalliin – Lumin tuttava odottaa helikopterin kanssa", r=25, merkki="Halli", cp=True),
    toim("anna_kopteri", "Nouse helikopteriin"),
    toim("seuraa_konetta", "Seuraa konetta ilmassa ja pysy vihreällä alueella 60 s, kunnes Lumi saa yhteyden autopilottiin", cp=True),
    toim("hyppy_kiitotielle", "Hyppää helikopterista ja laskeudu laskuvarjolla kiitotien merkkiin ennen kuin kone laskeutuu", cp=True),
    keraa("Ota salkku kuriirilta koneen portailla", [kohde("salkku", "LOC_KIITOTIE", "Salkku", r=8, esine="ITEM_KOPIOTODISTE")]),
    rep(r("KURIIRI", "yllättynyt", "Kone kääntyi itsestään ympäri. Ja sinä tulit taivaalta."),
        r("RAMI", "ovela", "Salkku, kiitos."),
        r("KURIIRI", "huolestunut", "…Ihan reilua. En minä edes pidä lentämisestä.")),
    rep(r("RADIO", "iloinen", "Porin lentoasemalla nähtiin tänään laskuvarjohyppy kiitotielle. Lentoaseman mukaan kenelläkään ei ole hätää, ja lennot jatkuvat normaalisti.")),
], antaja="LUMI", laukaisu=merkki("LOC_PIILO"), vaatii=["FLAG_M19_DONE"], asettaa={"esineet": ["ITEM_KOPIOTODISTE", "ITEM_LASKUVARJO"]},
   palkinto={"raha": 500, "teksti": "Todisteet väärennöksistä · laskuvarjo varusteisiin"},
   hahmot=[hahmo("KURIIRI", "LOC_KIITOTIE", dx=4, alkaen=6)],
   huom="Lentokone, laskuvarjo ja kopteri ovat pelissä erikseen. Tarina tarvitsee: AI-kone kiitotiellä, seuraa-alue ilmassa, hyppy kopterista (hyppy.js), kiitotiemerkki.")

def kierros(n, *opts): return valinta(f"Neuvottelu – kierros {n}/3", *opts)
BLUFF = {"muuttujat": {"VAR_VARJO_CONFESSION": "+1"}}
teht("M21", "Neuvottelu", 4, [
    rep(r("VARJO", "ovela", "Rami. Istu. Tarjoan sinulle sitä, mitä kukaan ei voi kieltäytyä: kauppakeskuksen hienoimman liiketilan.")),
    kierros(1, vo("\"Tapsalla on muitakin kavereita.\"", BLUFF), vo("\"Ehkä haluan liiketilan.\""), vo("\"Lumi näkee kaiken.\"", BLUFF)),
    rep(r("VARJO", "neutraali", "Kaverit. Kuinka liikuttavaa.")),
    kierros(2, vo("\"Kauppakirjat on jo lehdistöllä.\"", BLUFF), vo("\"Harju ei ole puolellasi.\"", BLUFF), vo("\"Mitä jos torilla ei olekaan kauppakeskusta?\"")),
    rep(r("VARJO", "vihainen", "Lehdistö kirjoittaa sen, minkä minä maksan.")),
    kierros(3, vo("\"Missä Tapsa on?\"")),
    rep(r("VARJO", "vihainen", "Tapsasi on turvassa varastollani. Niin kauan kuin sinä olet hiljaa.")),
], antaja="VARJO", laukaisu=merkki("LOC_VARJOTORNI", r=8), antajaPaikka={"paikka": "LOC_VARJOTORNI", "dx": 3}, vaatii=["FLAG_M20_DONE"],
   asettaa={"liput": ["FLAG_TAPSAN_SIJAINTI"]},
   huom="Kattoravintola (sisätila) puuttuu. Bluffit kasvattavat VAR_VARJO_CONFESSION (0–3) → finaalissa vähemmän vartijoita.")

teht("M22", "Salainen hanke", 4, [
    rep(r("LUMI", "ovela", "Varjon varaston kellarissa on prototyyppi, jota hän ei näytä sijoittajille. Jos se on mitä luulen, me lennetään.")),
    mene("LOC_VARASTO", "Mene Varjon varastolle", r=20, kulku="maa", merkki="Varasto", cp=True),
    toim("hiiviskely", "Hiivi kellariin: väistä hälytyslaserit tai sammuta ne sähkökaapista", cp=True),
    keraa("Ota prototyyppilentoreppu", [kohde("reppu", "LOC_VARASTO", "Lentoreppu", r=5, esine="ITEM_LENTOREPPU", dx=-6)]),
    toim("lentoreppu", "Lennä ulos kattoikkunasta lentorepulla", cp=True),
], antaja="LUMI", laukaisu=merkki("LOC_PIILO"), vaatii=["FLAG_M21_DONE"], asettaa={"esineet": ["ITEM_LENTOREPPU"]},
   palkinto={"raha": 300, "teksti": "Lentoreppu varusteisiin"},
   huom="Lentoreppu (uusi liikkumistapa) ja varaston sisätila puuttuvat.")

teht("M23", "Tapsan vapautus", 4, [
    viesti("Tapsa on varaston yläkerrassa. Tule katolta.", lahettaja="LUMI"),
    tapa("M23"),
    toim("lentoreppu", "Lennä varaston katolle lentorepulla"),
    mene("LOC_VARASTO", "Laskeudu varaston katolle", r=25, merkki="Katto", cp=True),
    toim("rc_auto", "Harhauta vartijat kauko-ohjattavalla autolla", ehto=APP("M23", 1)),
    toim("katkaise_sahkot", "Kytke varaston sähköt pois ja kaikki valot sammuvat", ehto=APP("M23", 2)),
    toim("tiirikka", "Avaa Tapsan varastohuoneen lukko (tiirikkaminipeli)", cp=True),
    aseta({"poista": ["FLAG_TAPSA_CAPTURED"]}),
    rep(r("TAPSA", "iloinen", "Mitä sulla on selässä? Hetkinen. Mul on kysymyksiä. Ja haluun kokeilla.")),
    mene("LOC_KORJAAMO", "Pakene Tapsan kanssa korjaamolle", r=12, kulku="maa", merkki="Korjaamo"),
], laukaisu=automaattinen(8), vaatii=["FLAG_M22_DONE"], asettaa={"liput": ["FLAG_CH4_DONE"]},
   palkinto={"raha": 400, "teksti": "Tapsa vapaana · Luku 5 avautui"},
   hahmot=[hahmo("TAPSA", "LOC_VARASTO", dx=-4, alkaen=8, asti=8)],
   huom="Alkaa itsestään M22:n jälkeen (Lumin viesti).")

# ================= LUKU 5: Finaali =================
teht("M24", "Iso keikka", 5, [
    cut("CUT_M24_A",
        kuvaus("[Lumin piilo. Koko porukka on koolla: Rami, Tapsa, Lumi, Terttu ja ne rantalaiset, joita Rami auttoi luvussa 4.]"),
        r("LUMI", "ovela", "Meillä on kopiot kaikesta. Mutta alkuperäiset väärennetyt kauppakirjat ovat Varjon omassa kassakaapissa, 20. kerroksessa. Ilman niitä Varjo kiistää kaiken."),
        r("TERTTU", "iloinen", "Me torilaiset hoidetaan harhautus. Kukaan ei vartioi ovia, kun ilmaisia munkkeja jaetaan.")),
    toim("torilaiset_harhauttavat", "Terttu ja liittolaiset harhauttavat vartijat (kesto = liittolaisten määrä × 10 s)"),
    anna("LOC_PIILO", "van", "🚐 Tapsan paku", dx=6, vari="#d8b030"),
    mene("LOC_VARJOTORNI", "Aja pakettiauto tornin lastauslaiturille (Tapsa ohjaa reittiä)", r=20, kulku="auto:van", merkki="Lastauslaituri", cp=True),
    kulku("jalan", "Nouse autosta"),
    toim("torni_kerros20", "Nouse 20. kerrokseen – vartijoiden määrä = 6 − Varjon tunnustukset", cp=True),
    toim("kassakaappi", "Avaa kassakaappi (Lumin ohjaama kolmivaiheinen minipeli)", cp=True),
], antaja="LUMI", laukaisu=merkki("LOC_PIILO"), vaatii=["FLAG_CH4_DONE"],
   ehto={"kaikki": [{"esine": "ITEM_KAUPPAKIRJAT_1"}, {"esine": "ITEM_KAUPPAKIRJAT_2"}, {"esine": "ITEM_TALLENTEET"}, {"esine": "ITEM_PALVELINDATA"}]},
   asettaa={"esineet": ["ITEM_ALKUPERAISET"]},
   hahmot=[hahmo("TAPSA", "LOC_PIILO", dx=3, asti=1), hahmo("TERTTU", "LOC_PIILO", dx=-3, asti=1)],
   huom="Finaalin harhautus, tornin sisätila ja kassakaappipeli puuttuvat.")

teht("M25", "Valinta", 5, [
    cut("CUT_M25_A",
        kuvaus("[Rami avaa kassakaapin. Takana on Harju, kansio kädessä.]"),
        r("HARJU", "huolestunut", "Minä tiedän, mitä noissa lukee. Allekirjoitin osan itse."),
        r("HARJU", "neutraali", "Antakaa ne minulle. Varjo luopuu hankkeesta hiljaisesti, eikä kukaan joudu ongelmiin. Myöskään minä."),
        r("LUMI", "ovela", "Tai näytämme ne koko kaupungille. Juhlassa on iso näyttö torilla.")),
    valinta("Mitä teet kauppakirjoille?",
            vo("\"Ota ne. Kunhan tori säilyy.\"", {"muuttujat": {"VAR_ENDING": 1}}),
            vo("\"Kaupunki ansaitsee tietää.\"", {"muuttujat": {"VAR_ENDING": 2}}),
            vo("\"Tule meidän puolellemme. Kerro itse.\"", {"muuttujat": {"VAR_ENDING": 3}}, ehto={"lippu": "FLAG_HARJU_DOUBT"})),
], laukaisu=automaattinen(1), vaatii=["FLAG_M24_DONE"],
   hahmot=[hahmo("HARJU", "LOC_VARJOTORNI", dx=2)],
   huom="Alkaa heti M24:n jälkeen. Loppu C näkyy vain, jos Harju epäili jo hotellissa (M14).")

END = lambda n: {"muuttuja": "VAR_ENDING", "yhtakuin": n}
teht("M26", "Viimeinen takaa-ajo", 5, [
    cut("CUT_M26_A", kuvaus("[Varjo tajuaa, mitä on tapahtunut, ja yrittää paeta yksityisveneellään ennen kuin totuus leviää.]"),
        r("VARJO", "vihainen", "Ette te mitään todista! Ilman minua tämä kaupunki on pelkkä vanha tori ja joki!"),
        r("RAMI", "neutraali", "Hyvä tori. Hyvä joki.")),
    toim("varjo_mittari", "Aja tornilta Etelärannan laiturille", param={"tahdet": 5, "kesto": 120}, ohita=0.5),
    mene("LOC_ETELARANTA", "Aja tornilta Etelärannan laiturille", r=15, kulku="maa", merkki="Laituri", cp=True),
    toim("veneen_takaa_ajo", "Seuraa Varjon venettä joella (vene)", cp=True),
    mene("LOC_KIRJURINLUOTO", "Ohjaa vene Kirjurinluodon rantaan, jossa juhlakansa odottaa", r=40, merkki="Kirjurinluoto"),
    cut("END_A", kuvaus("[Aamu torilla. Kojut auki. Varjo-tornin kyltti puretaan. Radio puhuu taustalla.]"),
        r("RADIO", "iloinen", "Varjo Holdings ilmoitti perääntyvänsä kauppakeskushankkeesta. Viktor Varjo ei ole tavoitettavissa kommentteja varten, ja hänen kerrotaan lähteneen pitkälle lomalle."),
        r("TAPSA", "huolestunut", "Ja jos se tulee takas?"),
        r("RAMI", "ovela", "Sitten tiedämme, mistä hänet löytää."),
        kuvaus("[Jatko-osan vihje: postikortti ulkomailta, allekirjoitus V.]"), ehto=END(1)),
    cut("END_B", kuvaus("[Juhlan iso näyttö torilla. Lumi painaa nappia. Näytölle ilmestyvät väärennetyt allekirjoitukset. Juhlakansa haukkoo henkeään.]"),
        r("RADIO", "yllättynyt", "Ennenkuulumatonta! Viktor Varjo saapui poliisilaitokselle vastaamaan kysymyksiin kauppakirjoista. Myös talousjohtaja Hanna Harjun osuutta selvitetään."),
        r("TERTTU", "iloinen", "Kahvit koko kaupungille!"), ehto=END(2)),
    cut("END_C", kuvaus("[Harju astuu juhlan lavalle mikrofoni kädessä.]"),
        r("HARJU", "iloinen", "Minä olen Hanna Harju. Työskentelin Varjo Holdingsille. Tänään kerron, mitä näin."),
        kuvaus("[Ruudun ulkopuolella: poliisi saattaa Varjon pois veneeltä. Kaupunki ilmoittaa ostavansa puretuiksi aiotut paikat asukkaiden käyttöön. Ilotulitus Kokemäenjoen yllä.]"),
        r("LUMI", "iloinen", "Seuraavaksi pitää keksiä, mitä tehdä tälle kaikelle vapaa-ajalle."),
        r("TAPSA", "iloinen", "Kyl sää tiärät. Sillankilpa."), ehto=END(3)),
], laukaisu=automaattinen(3), vaatii=["FLAG_M25_DONE"], asettaa={"liput": ["FLAG_GAME_COMPLETE"]},
   palkinto={"raha": 1000, "teksti": "Tarina läpäisty – Satamakaupunki on pelastettu"},
   hahmot=[hahmo("VARJO", "LOC_ETELARANTA", dx=20, dy=30, alkaen=3, asti=3)],
   huom="Veneen takaa-ajo puuttuu. Loppukohtaukset ovat välianimaatioita ilman omia kamera-ajoja.")

os.makedirs(OUT, exist_ok=True)
for t in T:
    with open(os.path.join(OUT, t["id"] + ".json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(t, ensure_ascii=False, indent=1) + "\n")
print(len(T), "tehtävää:", " ".join(t["id"] for t in T))
