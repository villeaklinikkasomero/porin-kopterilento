# HUOM: tehtävät on jo generoitu ja niitä muokataan nyt suoraan JSONina. Älä aja tätä uudelleen – se kirjoittaa käsin tehdyt muutokset yli.
# Käyttö (vain uudelleenrakennukseen): python tools/tarina/gen_sivu.py tarina/data/tehtavat
# Rautalangat: kaupat (K_*), korjaamo ja tuunaus (K_*) sekä mikrotehtävät (S_*). 21.11.2026.
# Kaikki ovat toistuvia tehtäviä (moottorin `toistuva` + `jaahtyy`). Talouden logiikka, jota data ei kata: tarina/talous.js.
import json, sys, os
sys.argv = [sys.argv[0], sys.argv[1]]
from gen_tarina import r, rep, soitto, mene, kulku, keraa, kohde, toim, valinta, vo, aseta, pysy, anna, merkki, OUT

S = []
def sivu(id, nimi, laji, vaiheet, *, laukaisu, merkkiK, vaatii=None, ehto=None, palkinto=None, jaahtyy=0, antaja=None, antajaPaikka=None, fail=None, huom=None, ruoka=False):
    t = {"id": id, "nimi": nimi, "luku": 0, "toistuva": True, "jaahtyy": jaahtyy, "laji": laji, "merkki": merkkiK, "rautalanka": True}
    if ruoka: t["ruoka"] = True
    if antaja: t["antaja"] = antaja
    if antajaPaikka: t["antajaPaikka"] = antajaPaikka
    if vaatii: t["vaatii"] = vaatii
    if ehto: t["ehto"] = ehto
    t["laukaisu"] = laukaisu
    if fail: t["fail"] = fail
    t["vaiheet"] = vaiheet
    if palkinto: t["palkinto"] = palkinto
    if huom: t["_huom"] = huom
    S.append(t)

def ruoka(teksti, hinta, energia, lahde, rivi=None):
    return vo(f"{teksti} – {hinta} € (+{energia} ⚡)", {"muuttujat": {"ENERGIA": f"+{energia}"}}, rivit=[rivi] if rivi else None, hinta=hinta) | {"lahde": lahde}
L = lambda p, dx=0, dy=0: {"paikka": p, "dx": dx, "dy": dy}

# ---------- ruoka ----------
sivu("K_GRILLI", "Grilli Kaksi Siivua", "kauppa", [
    valinta("Grilli Kaksi Siivua – mitä saisi olla?",
            ruoka("Porilainen", 8, 50, "Grilli Kaksi Siivua", r("GRILLI", "iloinen", "Porilainen, tuplana sipulia. Seuraava!")),
            ruoka("Lihapiirakka kahdella nakilla", 6, 35, "Grilli Kaksi Siivua", r("GRILLI", "iloinen", "Kaikilla mausteilla. Ole hyvä.")),
            ruoka("Ranskalaiset", 3, 15, "Grilli Kaksi Siivua"),
            vo("Ei tällä kertaa")),
], laukaisu=merkki("LOC_GRILLI", r=7), merkkiK="🍔", ruoka=True, jaahtyy=3,
   huom="Omistaja 21.11.2026: Ramin pitää syödä. Grilli Kaksi Siivua, Juhana Herttuan katu 19 (paikka arvio). Myyjän malli ja grillikioskin luukku puuttuvat.")

sivu("K_VAUHTIS", "Vauhtis", "kauppa", [
    valinta("Ravintola Rattaanpyörä – mitä otetaan?",
            ruoka("Hot wingsit", 12, 65, "Vauhtis", r("BAARIMIKKO", "iloinen", "Wingsit tulee. Talon kastike, niinku aina.")),
            ruoka("Wings-kori ja crispers", 16, 90, "Vauhtis", r("BAARIMIKKO", "ovela", "Iso kori rallikuskille.")),
            ruoka("Kahvi ja munkki", 4, 20, "Vauhtis"),
            vo("Ei kiitos")),
], laukaisu=merkki("LOC_VAUHTIS_OVI", r=7), merkkiK="🍗", ruoka=True, jaahtyy=3,
   huom="Rattaanpyörä, Yrjönkatu 27 (oven paikka arvio). Sisätila ja baarimikon malli puuttuvat.")

# ---------- korjaamo ----------
KOR = lambda n: {"muuttuja": "KORJAUS", "yhtakuin": n}
sivu("K_KORJAUS", "Korjaus Tapsan hallissa", "korjaamo", [
    rep(r("TAPSA", "huolestunut", "No mitä sää oot tehny? Aja sisään, katotaan.")),
    valinta("Korjaus – Tapsa veloittaa vain osat",
            vo("Pikkukolhut – 10 €", {"muuttujat": {"KORJAUS": 1}}, ehto={"muuttuja": "AUTON_VAURIO", "enint": 30}, hinta=10) | {"lahde": "korjaus"},
            vo("Kunnon korjaus – 25 €", {"muuttujat": {"KORJAUS": 1}}, ehto={"muuttuja": "AUTON_VAURIO", "vah": 31, "enint": 70}, hinta=25) | {"lahde": "korjaus"},
            vo("Iso remontti – 45 €", {"muuttujat": {"KORJAUS": 1}}, ehto={"muuttuja": "AUTON_VAURIO", "vah": 71}, hinta=45) | {"lahde": "korjaus"},
            vo("Ei nyt", {"muuttujat": {"KORJAUS": 0}})),
    toim("korjaa_auto", "Tapsa korjaa auton", ehto=KOR(1), ohita=0.5),
    rep(r("TAPSA", "ovela", "Valmis. Älä kerro kellekään, et mää tein tän melkein ilmaseks."), ehto=KOR(1)),
    aseta({"muuttujat": {"KORJAUS": 0}}),
], laukaisu=merkki(L("LOC_KORJAAMO", dx=5), r=8, kulku="auto"), merkkiK="🔧", vaatii=["FLAG_M01_DONE"],
   ehto={"muuttuja": "AUTON_VAURIO", "vah": 5},
   huom="Omistaja 21.11.2026: autot korjataan Tapsan hallissa. Auto ei korjaannu muualla (kopteri korjaantuu laskeutuneena kuten ennen). AUTON_VAURIO = talous.js.")

# ---------- tuunaus: osto → nouto pakulla → asennus ----------
EI_TILAUSTA = {"kaikki": [{"eiEsinetta": "ITEM_OSAT_NOUTAMATTA"}, {"eiEsinetta": "ITEM_OSAT_HALLISSA"}]}
def osa(n, teksti, hinta, tune):
    return vo(f"{teksti} – {hinta} €", {"muuttujat": {"TILAUS": n}, "esineet": ["ITEM_OSAT_NOUTAMATTA"]},
              ehto={"muuttuja": tune, "enint": 0}, hinta=hinta) | {"lahde": "Satakunnan Varaosa"}
sivu("K_OSAT", "Satakunnan Varaosa", "kauppa", [
    rep(r("VARAOSAMYYJA", "iloinen", "Päivää! Mitä Ramin farmariin tänään laitetaan?")),
    valinta("Tilaa osa (nouto pakettiautolla lastauslaiturilta)",
            osa(1, "Maalaus: helmiäismusta", 60, "TUNE_MAALI"), osa(2, "Urheiluvanteet", 150, "TUNE_VANTEET"),
            osa(3, "Takaspoileri", 90, "TUNE_SPOILERI"), osa(4, "Tuplapakoputki", 110, "TUNE_PAKO"),
            osa(5, "Moottorin viritys (+25 % kiihtyvyys)", 280, "TUNE_MOOTTORI"), osa(6, "Lisävalot", 70, "TUNE_VALOT"),
            vo("Ei mitään tänään")),
    rep(r("VARAOSAMYYJA", "neutraali", "Osat on isossa laatikossa lastauslaiturilla. Tuo paku, niin nostetaan kyytiin."), ehto={"esine": "ITEM_OSAT_NOUTAMATTA"}),
], laukaisu=merkki("LOC_VARAOSALIIKE", r=6), merkkiK="⚙", vaatii=["FLAG_M02_DONE"], ehto=EI_TILAUSTA,
   huom="Omistaja 21.11.2026: tuning-osat ostetaan autovaraosaliikkeestä rahalla ja noudetaan pakettiautolla. Yksi tilaus kerrallaan. Osamallit: tuunaus_mallipyynto.md.")

sivu("K_NOUTO", "Nouda osat pakulla", "korjaamo", [
    anna("LOC_KORJAAMO_PIHA", "van", "🚐 Tapsan paku", yaw=0.14, vari="#d8b030"),
    mene("LOC_VARAOSA_LAITURI", "Aja paku Satakunnan Varaosan lastauslaiturille", r=8, kulku="auto:van", merkki="Lastauslaituri", cp=True),
    rep(r("VARAOSAMYYJA", "neutraali", "Laatikko kyydissä. Aja nätisti, siinä on lasia.")),
    mene("LOC_KORJAAMO", "Vie osat Tapsan halliin", r=12, kulku="auto:van", merkki="Korjaamo"),
    aseta({"poistaEsineet": ["ITEM_OSAT_NOUTAMATTA"], "esineet": ["ITEM_OSAT_HALLISSA"]}),
    rep(r("TAPSA", "iloinen", "Osat tuli. Tuo farmari halliin, niin laitetaan kiinni.")),
], laukaisu=merkki("LOC_KORJAAMO_PIHA", r=5), merkkiK="🚐", vaatii=["FLAG_M02_DONE"], ehto={"esine": "ITEM_OSAT_NOUTAMATTA"},
   fail=[{"ehto": "kulkuneuvo_rikki", "teksti": "Paku ei kestänyt – osat jäivät laiturille."}],
   huom="Tapsan paku ilmestyy pihalle, kun aloitat tehtävän (pelin __take.give). Pysyvä pysäköity paku pihalla puuttuu.")

sivu("K_TUUNAUS", "Tuunaus Tapsan hallissa", "korjaamo", [
    rep(r("TAPSA", "ovela", "Aja nostimeen. Mä laitan osat kiinni, sää keität kahvit.")),
    toim("tuunaa", "Tapsa asentaa osat", ohita=0.5),
    aseta({"poistaEsineet": ["ITEM_OSAT_HALLISSA"], "muuttujat": {"TILAUS": 0}}),
    rep(r("TAPSA", "iloinen", "Kato nyt. Melkein yhtä hieno ku mun.")),
], laukaisu=merkki(L("LOC_KORJAAMO", dx=-5), r=8, kulku="auto:estate"), merkkiK="🔧", vaatii=["FLAG_M02_DONE"], ehto={"esine": "ITEM_OSAT_HALLISSA"},
   huom="Asennus Ramin farmariin. Maali ja moottori vaikuttavat jo (talous.js); vanteet, spoileri, pakoputki ja valot odottavat osamalleja.")

# ---------- mikrotehtävät: rahaa ----------
sivu("S_KUKAT", "Tertun kukkalähetys", "sivu", [
    rep(r("TERTTU", "iloinen", "Viäs nää kukat Raatihuoneelle, siel on häät. Pyörällä pääsee kiveyksiä pitkin nopeimmin.")),
    kulku("pyora", "Ota pyörä – torin laidalla on pyörätelineitä"),
    keraa("Ota kukat Tertun kojulta", [kohde("kukat", "LOC_TERTUN_KOJU", "Kukat", r=8, kulku="pyora")]),
    mene("LOC_RAATIHUONE", "Vie kukat Raatihuoneelle ennen kuin hääpari tulee (3 min)", r=12, kulku="pyora", merkki="Häät", aikaraja=180),
], laukaisu=merkki(L("LOC_TERTUN_KOJU", dx=-6, dy=4), r=3), merkkiK="€", vaatii=["FLAG_M01_DONE"], jaahtyy=240,
   palkinto={"raha": 12, "teksti": "Kukat perillä"})

sivu("S_SIIVET", "Vauhtiksen siipilähetti", "sivu", [
    rep(r("BAARIMIKKO", "iloinen", "Kaks laatikkoo wingsejä Kirjurinluodon jazzlavalle. Kuumana!")),
    kulku(["pyora", "auto"], "Ota pyörä tai auto"),
    mene("LOC_KIRJURINLUOTO", "Vie wingsit Kirjurinluodon jazzlavalle (4 min)", r=35, kulku=["pyora", "auto"], merkki="Jazzlava", aikaraja=240),
], laukaisu=merkki(L("LOC_VAUHTIS_OVI", dx=5), r=3), merkkiK="€", antaja="BAARIMIKKO", antajaPaikka=L("LOC_VAUHTIS_OVI", dx=6),
   vaatii=["FLAG_M01_DONE"], jaahtyy=300, palkinto={"raha": 18, "teksti": "Wingsit perillä kuumana"})

sivu("S_GRILLI", "Kaksi Siivun yölähetti", "sivu", [
    rep(r("GRILLI", "ovela", "Teatterin väki tilas kuus porilaista väliajalle. Ehdiksää?")),
    kulku(["pyora", "auto"], "Ota pyörä tai auto"),
    mene("LOC_TEATTERI", "Vie porilaiset Porin Teatterin takaovelle (3 min 20 s)", r=12, kulku=["pyora", "auto"], merkki="Teatteri", aikaraja=200),
], laukaisu=merkki(L("LOC_GRILLI", dx=6), r=3), merkkiK="€", antaja="GRILLI", antajaPaikka=L("LOC_GRILLI", dx=7),
   vaatii=["FLAG_M01_DONE"], jaahtyy=300, palkinto={"raha": 14, "teksti": "Väliaika pelastettu"})

sivu("S_HINAUS", "Asiakkaan auto", "sivu", [
    rep(r("TAPSA", "huolestunut", "Asiakkaan auto sammu Kauppahallin eteen. Hae se tänne, mut varovasti – se on jo valmiiks kipee.")),
    mene("LOC_KAUPPAHALLI", "Mene Kauppahallin eteen", r=15, kulku="maa", merkki="Asiakkaan auto"),
    kulku("jalan", "Nouse kyydistä ja mene asiakkaan autolle"),
    anna("LOC_KAUPPAHALLI", "hatch", "🚗 Asiakkaan auto", dx=4, vari="#6a7f9a"),
    mene("LOC_KORJAAMO", "Aja auto Tapsan halliin ehjänä", r=12, kulku="auto", merkki="Korjaamo", cp=True),
], laukaisu=merkki(L("LOC_KORJAAMO_OVI", dx=-4), r=3), merkkiK="€", vaatii=["FLAG_M02_DONE"], jaahtyy=360,
   fail=[{"ehto": "kulkuneuvo_rikki", "teksti": "Asiakkaan auto hajosi lopullisesti. Tapsa huokaa."}],
   palkinto={"raha": 25, "teksti": "Asiakas tyytyväinen"})

sivu("S_RENKAAT", "Rengaskuljetus", "sivu", [
    rep(r("VARAOSAMYYJA", "neutraali", "Talvirenkaat asemalle, bussivarikon kuski odottaa. Tarvitset pakun.")),
    kulku("auto:van", "Hanki pakettiauto (pysäköityjä pakuja on kaupungilla, Tapsan paku korjaamolla)"),
    mene("LOC_VARAOSA_LAITURI", "Lastaa renkaat laiturilta", r=8, kulku="auto:van", merkki="Lastauslaituri"),
    mene("LOC_ASEMA", "Vie renkaat asemalle", r=30, kulku="auto:van", merkki="Asema"),
], laukaisu=merkki(L("LOC_VARAOSALIIKE", dx=6), r=3), merkkiK="€", antaja="VARAOSAMYYJA", antajaPaikka=L("LOC_VARAOSALIIKE", dx=7),
   vaatii=["FLAG_M03_DONE"], jaahtyy=360, palkinto={"raha": 20, "teksti": "Renkaat perillä"})

sivu("S_ILMAKUVA", "Liikennekuvaus Radio Kirjurille", "sivu", [
    soitto("RADIO", r("RADIO", "iloinen", "Täällä Radio Kirjuri! Tarvitaan ilmakuvaa liikenteestä: Isosilta, tori ja kirkko. Leijaile hetki jokaisen yllä.")),
    pysy("LOC_ISOSILTA", 5, "Kuvaa Isosilta (leijaile yllä)", r=50, kulku="heli", mittari="Kuvaus"),
    pysy("LOC_TORI", 5, "Kuvaa Kauppatori", r=50, kulku="heli", mittari="Kuvaus"),
    pysy("LOC_KIRKKO", 5, "Kuvaa Keski-Porin kirkko", r=50, kulku="heli", mittari="Kuvaus"),
], laukaisu=merkki(L("LOC_ETELARANTA", dx=30), r=30, kulku="heli"), merkkiK="€", vaatii=["FLAG_HELI_AUKI"], jaahtyy=420,
   palkinto={"raha": 30, "teksti": "Ilmakuvat radiolle"},
   huom="Lennä kopterilla Etelärannan merkin yli aloittaaksesi.")

for t in S:
    with open(os.path.join(OUT, t["id"] + ".json"), "w", encoding="utf-8") as f:
        f.write(json.dumps(t, ensure_ascii=False, indent=1) + "\n")
ids = [f"M{n:02d}" for n in range(1, 27)] + [t["id"] for t in S]
with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8") as f:
    f.write(json.dumps(ids, ensure_ascii=False) + "\n")
print(len(S), "toistuvaa:", " ".join(t["id"] for t in S))
