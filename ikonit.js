// Porikopterin glyfi-ikonit (UI-konsepti 21.11.2026, kanvaasin työpöytä "Glyfi-ikonit": 24 px ruudukko, viiva 2,2 px, pyöreät päät, väri currentColor).
// Emojit pois käyttöliittymästä: tämä sarja korvaa ne. Tavallinen skripti (ei moduuli), ladataan <body>:n alussa, joten ikonit ovat käytössä heti.
//   HTML:  <svg class="ik"><use href="#ik-radio"/></svg>          (tiedosto lisää sivulle <symbol id="ik-…"> -sarjan)
//   JS:    window.ikoni('radio')  → '<svg class="ik" …>…</svg>' -merkkijono;  window.IKONIT = { nimi: SVG-sisältö }
// Uusi ikoni: lisää rivi IKONIT-tauluun (24 × 24, stroke-width 2.2, täytetyt osat fill="currentColor" stroke="none").
(function () {
  const T = 'fill="currentColor" stroke="none"';
  const IKONIT = {
    // konseptin sarja
    radio: '<rect x="3" y="8" width="18" height="12" rx="2"/><circle cx="9" cy="14" r="3"/><path d="M14 12h4M14 16h4M6 8l10-5"/>',
    kavely: `<circle cx="13" cy="4" r="2" ${T}/><path d="M12 7l-2 6 3 3v5M10 13l-3 8M11 9l4 3h3M11 9l-3 2-1 3"/>`,
    puhe: '<path d="M4 5h16v10H10l-4 4v-4H4z"/>',
    musiikki: '<path d="M9 18V5l11-2v13"/><circle cx="6.5" cy="18" r="2.5" fill="currentColor"/><circle cx="17.5" cy="16" r="2.5" fill="currentColor"/>',
    juoksu: `<circle cx="15" cy="4" r="2" ${T}/><path d="M13 7l-3 5 4 3-1 6M10 12l-5 2M12 8l5 3 3-1M11 8l-4 1-2 3M14 15l3 2"/>`,
    ylos: '<path d="M6 15l6-6 6 6"/>',
    alas: '<path d="M6 9l6 6 6-6"/>',
    suunta: '<path d="M12 3l7 18-7-4-7 4z" fill="currentColor"/>',
    henkilo: '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.4 3.6-7 8-7s8 2.6 8 7"/>',
    valmis: '<path d="M4 12l5 5L20 6"/>',
    ohita: '<path d="M6 6l12 12M18 6L6 18"/>',
    paketti: '<path d="M3 7l9-4 9 4v10l-9 4-9-4zM3 7l9 4 9-4M12 11v10"/>',
    kylma: '<path d="M12 2v20M3.3 7l17.4 10M3.3 17l17.4-10M9 3.5l3 2 3-2M9 20.5l3-2 3 2"/>',
    arka: '<path d="M7 3h10l-1 7a4 4 0 0 1-8 0zM12 14v6M8 21h8"/>',
    kiire: '<path d="M13 2L4 14h7l-1 8 9-12h-7z" fill="currentColor"/>',
    ilma: '<path d="M2 5h20M12 5v4M6 10h9a4 4 0 0 1 0 8H9a3 3 0 0 1-3-3zM19 13h3M7 21h10M9 18v3M15 18v3"/>',
    pyora: '<circle cx="6" cy="16" r="4"/><circle cx="18" cy="16" r="4"/><path d="M6 16l4-7h6l2 7M10 9l2 7M14 6h3"/>',
    tahti: '<path d="M12 2.5l2.9 6 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.2 1.3-6.6L2.5 9.3l6.6-.8z" fill="currentColor"/>',
    puhelu: `<path d="M5 3h4l2 5-2.5 1.5a11 11 0 0 0 6 6L16 13l5 2v4a2 2 0 0 1-2 2A17 17 0 0 1 3 5a2 2 0 0 1 2-2z" ${T}/>`,
    viesti: '<path d="M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H9l-5 4z"/>',
    raha: '<circle cx="12" cy="12" r="9"/><path d="M15.5 8.5a4.5 4.5 0 1 0 0 7M7 11h6M7 13.5h6"/>',
    nouto: '<path d="M12 22s7-7 7-12a7 7 0 0 0-14 0c0 5 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    aani: '<path d="M4 9h4l5-4v14l-5-4H4zM16 9a4 4 0 0 1 0 6M18.5 6.5a8 8 0 0 1 0 11"/>',
    kentta: `<rect x="3" y="15" width="3" height="5" ${T}/><rect x="8" y="11" width="3" height="9" ${T}/><rect x="13" y="7" width="3" height="13" ${T}/><rect x="18" y="3" width="3" height="17" ${T}/>`,
    seuraava: '<path d="M9 6l6 6-6 6"/>',
    edellinen: '<path d="M15 6l-6 6 6 6"/>',
    // lisätty samalla tyylillä (rautalangan emojit 🍔 🍗 ⚙ 🔧 🚐 € ja aloitussivu)
    ruoka: '<path d="M4 11h16a8 8 0 0 1-16 0zM4 11a8 8 0 0 1 16 0M3 15h18M7 19h10"/>',
    kauppa: '<path d="M4 9l1.5-5h13L20 9M4 9h16v11H4zM4 9a2.7 2.7 0 0 0 5.3 0 2.7 2.7 0 0 0 5.4 0 2.7 2.7 0 0 0 5.3 0M10 20v-5h4v5"/>',
    korjaamo: '<path d="M14.5 6.5a4 4 0 0 0 5 5L21 13a6 6 0 0 1-7.5 1.5L7 21a2.1 2.1 0 0 1-3-3l6.5-6.5A6 6 0 0 1 12 4l1.5 1.5-1 1 3 3 1-1"/>',
    pakettiauto: '<path d="M2 6h12v10H2zM14 9h4l4 4v3h-8z"/><circle cx="6" cy="17.5" r="2" fill="currentColor"/><circle cx="17" cy="17.5" r="2" fill="currentColor"/>',
    auto: '<path d="M3 16v-3l2-5h14l2 5v3zM3 13h18"/><circle cx="7" cy="16.5" r="2" fill="currentColor"/><circle cx="17" cy="16.5" r="2" fill="currentColor"/>',
    kopteri: '<path d="M3 4h18M12 4v3M5 8h9a5 5 0 0 1 0 10H9a4 4 0 0 1-4-4zM19 12h3M8 21h9M10 18v3M15 18v3"/>',
    lukko: '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3M12 15v2"/>',
    energia: '<rect x="3" y="7" width="16" height="10" rx="2"/><path d="M21 10v4"/><path d="M11.5 8.5L8 12.5h3l-.5 3 3.5-4h-3z" fill="currentColor"/>',
    tarina: '<path d="M4 4h6a2 2 0 0 1 2 2v14a2 2 0 0 0-2-2H4zM20 4h-6a2 2 0 0 0-2 2v14a2 2 0 0 1 2-2h6z"/>',
    kartta: '<path d="M3 6l6-2 6 2 6-2v14l-6 2-6-2-6 2zM9 4v14M15 6v14"/>',
    kello: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    varoitus: '<path d="M12 3l10 18H2zM12 10v5"/><circle cx="12" cy="18" r="1" fill="currentColor"/>',
    toisto: '<path d="M4 12a8 8 0 0 1 14-5.3M20 4v4h-4M20 12a8 8 0 0 1-14 5.3M4 20v-4h4"/>',
    pelaa: '<path d="M9 6l6 6-6 6"/>',
  };
  const ATTR = 'viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"';
  window.IKONIT = IKONIT;
  window.ikoni = (nimi, luokka) => IKONIT[nimi] ? `<svg class="ik${luokka ? ' ' + luokka : ''}" ${ATTR}>${IKONIT[nimi]}</svg>` : '';
  const lisaa = () => {
    if (document.getElementById('ik-sarja')) return;
    const d = document.createElement('div'); d.style.display = 'none';
    d.innerHTML = `<svg id="ik-sarja" xmlns="http://www.w3.org/2000/svg">${Object.entries(IKONIT).map(([n, s]) => `<symbol id="ik-${n}" ${ATTR.replace(' aria-hidden="true" focusable="false"', '')}>${s}</symbol>`).join('')}</svg>`;
    document.body.prepend(d);
  };
  if (document.body) lisaa(); else document.addEventListener('DOMContentLoaded', lisaa);
})();
