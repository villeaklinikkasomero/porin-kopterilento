# Hyppykoneen lentomalli (lento/lento.js)

Cessna 182 -tyyppinen kone jäykkänä kappaleena kuudella vapausasteella. Aerodynamiikka tulee C182:n stabiliteettiderivaatoista (Roskam / JSBSim): sakkaus ja sakkauksen jälkeinen nostovoima, siiven putoaminen, maavaikutus, laipat 0–40°, trimmi ja potkurivirta peräsimille. Moottorimallissa ovat imusarjan paine, vakiokierrospotkurin säädin, seos, kaasuttimen lämmitys, magneetot, käynnistin ja päävirta, sylinterin, öljyn ja pakokaasun lämmöt, polttoaineen kulutus, P-efekti ja vääntö. Maakontaktissa on kolme jousitettua rengasta jarruineen ja nokkapyöräohjauksineen sekä pyrstön kiinnitysrengas.

## Kalibrointi (1290 kg, merenpinta, `node sim_test.mjs`)

| | Malli | C182 POH |
|---|---|---|
| Lähtökiito, laipat 20° | irtoaa ~19 s, ~300 m | 242 m |
| Nousu 80 kt | ~820 ft/min | 924 ft/min (MTOW) |
| Sakkaus, laipat ylhäällä | 55 kt | 54 kt |
| Sakkaus, laipat 40° | ~48 kt (laskettu) | 49 kt |
| Matka 23"/2300 rpm | ~117 kt | ~125 kt |

`sim_rot.mjs hold|pulse` testaa näppäimistöllä tehdyn rotaation.

## Ohjaus

| Näppäin | Toiminto |
|---|---|
| W/S, ↑/↓ | sauva eteen / taakse (näppäin rakentaa poikkeutusta noin puoli liikealaa sekunnissa; maassa enintään 75 %) |
| ←/→ | kaarto: sivuperäsin (maassa nokkapyörä); helppo ohjaus kallistaa samalla ~25° ja oikaisee siivet, kun nuolet päästetään |
| A/D | siivekkeet (suoraan) |
| Q/E | sivuperäsin ja nokkapyörä |
| B | jarrut (pidä); peräsimen puoli jarruttaa enemmän |
| P | seisontajarru |
| Space / Shift | kaasu lisää / vähemmän |
| X / Z | potkurin kierrokset + / − |
| L / K | seos rikkaampi / laihempi |
| H | kaasuttimen lämmitys |
| O | päävirta |
| 6 | magneetot (POIS / R / L / MOLEMMAT) |
| I | käynnistin (pidä) |
| G / V | laipat alas / ylös 10° |
| U / J | trimmi nokka ylös / alas |
| 1 2 3 4 | navigointivalot, strobot, laskuvalo, majakka |
| 5 | jäähdytysläpät |
| 7 | mittaripalkki ulkokamerassa |
| 8 | helppo ohjaus päälle / pois (oletuksena päällä) |
| 9 | avustimet (peräsin, seos, yhden napin käynnistys; kosketuslaitteilla oletuksena päällä) |
| 0 | ohjeet |
| C | kamera: ohjaamo, ulko, ylhäältä |
| hiiri (vedä) | katsele ohjaamossa |
| Enter | nouse koneeseen / poistu (kone pysähdyksissä) |

Käynnistys: O, L kunnes seos 100 %, Space hetki (kaasua vähän), pidä I. Lentoonlähtö: P (seisontajarru pois), G G (laipat 20°), kaasu täysille, oikeaa peräsintä. Nokka ylös lyhyillä S-painalluksilla noin 52 kt:ssa, nousu 70–80 kt.

## Kytkennät index.html:ssä

`step()` → `__plane.step`, `updateCamera()` → `__plane.cam`, `walkNear()` palauttaa `'plane'` koneen vieressä, `walkAction()` nousee kyytiin tai poistuu, `walkOutAt()`. `window.__game` antaa lisäksi `touchIn`, `carGround`, `bldTopAt`, `fadeDo`, `toast`, `camMode`, `actx`, `soundOn` ja `world`.
