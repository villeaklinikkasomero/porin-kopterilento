// 21.11.2026 (omistaja: "maasta katsottuna maa näyttää materiaaleilta eikä venytetyltä ilmakuvalta. Ei lunta eikä ilmakuvaan palaneita autoja tai varjoja"):
// maan pinta 0–150 m (puhelimella 0–90 m) maankäyttökartan (maa/peite/) mukaisina PBR-materiaaleina (maa/tex/). Koodi: maa/maa.js.
// Laajentaa 033:n tarkkojen ilmakuvalaattojen materiaalia (HR.t); kaukana ja kopterista ilmakuva ennallaan. Vertailu: window.__maa.pois() / .paalle().
import kaynnista_maa from './maa/maa.js';
kaynnista_maa({ HR, renderer, isTouch });
