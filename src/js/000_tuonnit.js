import * as THREE from './three.module.min.js';
import CITY from './city.js';
import LOD2 from './lod2.js';
import RIV from './river.js';
import TER from './terrain.js';
import RATA from './rata/rata_data.js';   // 20.11.2026: rataverkko (rata/rata.js); täältä vain maastokorjaukset ennen maan rakentamista
// photo facades approved in the review tool (porikit export): building index -> [{ t: texture name, bw: bay width m }]
const CZ = await fetch('./city_zones.json').then(r => r.ok ? r.json() : { zones: {} }).catch(() => ({ zones: {} })), CZN = Object.keys(CZ.zones);   // whole-city blocks (blender/city.py), streamed by distance
const LOOK = await fetch('./styles.json').then(r => r.ok ? r.json() : null).catch(() => null) || { pal: [], wood: [], b: {} };   // locked wall colours and styles from the oblique aerial photos and street photos
const PHSJ = await fetch('./phs.json').then(r => r.ok ? r.json() : {}).catch(() => ({}));   // ground heights: Maanmittauslaitos 2 m elevation model (CC BY 4.0)   // Kokemäenjoki below street level (OpenStreetMap river area)   // measured LoD2 building models (Maanmittauslaitos Rakennukset 3D)
import PARKED from './parked.js';
import { GLTFLoader } from './GLTFLoader.js';

const HW = CITY.hw, YS = CITY.ys, YN = CITY.yn, HH = -YS, YSPAN = YN - YS;   // core: sharp aerial image
const OX0 = CITY.ox0, OX1 = CITY.ox1, OY0 = CITY.oy0, OY1 = CITY.oy1, OXS = OX1 - OX0, OYS = OY1 - OY0;   // whole map: coarser aerial image
const PSIL = { x: 207.45, y: 477.95, len: 170.04, head: Math.atan2(245.85 - 207.45, 643.6 - 477.95), deck: 2.6, half: 7.4 };
const PSIL_NOUSU = 2.8;   // 20.11.2026: Porinsillan keskikohdan nousu rantakatujen tasosta (m): alapaarteen alla noin 4 m vapaata vedestä
let PSIL_E = null;          // rantakatujen korkeudet sillan päissä (psilDeck)
const inCore = (x, y) => Math.abs(x) < HW && y > YS && y < YN;
